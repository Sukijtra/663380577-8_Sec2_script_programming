# agentic-comm-automator/src/communication_agent.py
import os
import json
import datetime
from .utils import setup_logging, log_audit_entry, ensure_directory_exists, get_env_variable, is_dry_run
from .email_tasks import EmailTasks
from .sms_tasks import SMSTasks
from .template_renderer import TemplateRenderer

logger = setup_logging(__name__)


class CommunicationAgent:
    """
    An agent that orchestrates communication tasks (email, SMS) based on a
    structured configuration file, managing an internal context for dynamic values.
    """
    def __init__(self, config, base_dir):
        self.config = config
        self.audit_log = []
        self.context = {}  # Stores dynamic values for templating and task chaining
        self.start_time = datetime.datetime.now()
        self.base_dir = base_dir
        self.dry_run = is_dry_run()

        # In dry-run mode, credentials are optional so the workflow can be tested without them
        default = "not-set" if self.dry_run else None
        sender_email = get_env_variable("SENDER_EMAIL", "agent@example.com" if self.dry_run else None)
        sender_app_password = get_env_variable("SENDER_APP_PASSWORD", default)
        smtp_server = get_env_variable("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(get_env_variable("SMTP_PORT", "587"))
        imap_server = get_env_variable("IMAP_SERVER", "imap.gmail.com")

        self.email_tasks = EmailTasks(smtp_server, smtp_port, imap_server, sender_email, sender_app_password,
                                      dry_run=self.dry_run,
                                      mailbox_dir=os.path.join(base_dir, "data", "dry_run_mailbox"))
        self.sms_tasks = SMSTasks(self.email_tasks)  # SMS tasks uses EmailTasks for underlying send
        self.template_renderer = TemplateRenderer()

        # Task dispatcher: maps task "type" from the config to a handler method
        self.handlers = {
            "send_email": self._handle_send_email,
            "send_sms": self._handle_send_sms,
            "process_inbox": self._handle_process_inbox,
        }
        logger.info(f"CommunicationAgent initialized ({'DRY RUN' if self.dry_run else 'LIVE'} mode).")

    def _update_context(self, key, value):
        """Updates a value in the agent's context."""
        self.context[key] = value
        logger.debug(f"Context updated: '{key}' = {value}")

    def _render_template(self, template_string, extra_context=None):
        """Renders a template string using the current agent context (plus optional extra values)."""
        context = {**self.context, **(extra_context or {})}
        try:
            return self.template_renderer.render(template_string, context)
        except Exception as e:
            log_audit_entry(self.audit_log, "ERROR", f"Template rendering failed: {e}", "template_render",
                            {"template": template_string})
            raise

    # --- Task handlers: each returns (success, output_data) ---
    def _handle_send_email(self, params):
        recipients = {k: [self._render_template(r) for r in v] for k, v in params.get('recipients', {}).items()}
        subject = self._render_template(params.get("subject_template"))
        body = self._render_template(params.get("body_template"))

        # Conditional attachments: only files that exist are attached
        attachments = []
        for att_path in params.get("attachments", []):
            rendered_path = os.path.join(self.base_dir, self._render_template(att_path))
            if os.path.exists(rendered_path):
                attachments.append(rendered_path)
            else:
                log_audit_entry(self.audit_log, "WARNING", f"Attachment not found, skipped: {rendered_path}", "send_email")

        success = self.email_tasks.send_email(recipients, subject, body, attachments, params.get("is_html", False))
        return success, {"recipients": recipients, "subject": subject, "attachments": attachments}

    def _handle_send_sms(self, params):
        phone_numbers = [self._render_template(p) for p in params.get("phone_numbers", [])]
        message = self._render_template(params.get("message_template"))
        carrier_name = self._render_template(params.get("carrier_name", ""))
        success = self.sms_tasks.send_sms(phone_numbers, message, carrier_name)
        return success, {"phone_numbers": phone_numbers, "message": message}

    def _rule_matches(self, conditions, email_info):
        """Checks the 'if' part of a rule against one email."""
        if "subject_contains" in conditions and \
                self._render_template(conditions["subject_contains"]).lower() not in email_info['subject'].lower():
            return False
        if "body_contains" in conditions and \
                self._render_template(conditions["body_contains"]).lower() not in email_info['text_body'].lower():
            return False
        if "from_contains" in conditions and \
                self._render_template(conditions["from_contains"]).lower() not in email_info['sender'].lower():
            return False
        if "has_attachments" in conditions and conditions["has_attachments"] != email_info['has_attachments']:
            return False
        return True

    def _apply_rule_actions(self, rule_name, actions, email_info):
        """Runs the 'then' part of a matched rule."""
        if actions.get("send_sms_alert"):
            message = self._render_template(
                actions.get("alert_message_template", "Urgent email received: {subject} from {sender}"), email_info)
            phone_numbers = [self._render_template(p) for p in actions.get("alert_phone_numbers", [])]
            carrier = self._render_template(actions.get("alert_carrier", ""))
            sent = self.sms_tasks.send_sms(phone_numbers, message, carrier)
            log_audit_entry(self.audit_log, "SUCCESS" if sent else "ERROR",
                            f"Rule '{rule_name}': SMS alert {'sent' if sent else 'failed'}.", "rule_action",
                            {"message": message})

        if "reply_with_template" in actions:
            reply_body = self._render_template(actions["reply_with_template"], email_info)
            reply_subject = self._render_template(actions.get("reply_subject_template", "Re: {subject}"), email_info)
            sent = self.email_tasks.send_email(recipients={'to': [email_info['sender']]},
                                               subject=reply_subject, body=reply_body)
            log_audit_entry(self.audit_log, "SUCCESS" if sent else "ERROR",
                            f"Rule '{rule_name}': auto-reply {'sent' if sent else 'failed'} to {email_info['sender']}.",
                            "rule_action", {"subject": reply_subject})

    def _handle_process_inbox(self, params):
        search_criteria = params.get("search_criteria", {})
        rules = params.get("rules", [])
        download_dir = os.path.join(self.base_dir, params.get("download_attachments_base_dir", "data/incoming_attachments"))

        from_sender = search_criteria.get("from_sender")
        subject_contains = search_criteria.get("subject_contains")
        uids = self.email_tasks.search_emails(
            mailbox=params.get("mailbox", "INBOX"),
            criteria=search_criteria.get("status", "UNSEEN"),
            from_sender=self._render_template(from_sender) if from_sender else None,
            subject_contains=self._render_template(subject_contains) if subject_contains else None,
        )
        if not uids:
            logger.info("No emails found matching search criteria for inbox processing.")
            return True, {"processed_emails": []}  # No emails found is not a failure

        processed = []
        for uid in uids:
            email_info = self.email_tasks.fetch_email_content(uid=uid, mark_as_read=params.get("mark_as_read", True),
                                                              download_attachments_dir=download_dir)
            if not email_info:
                log_audit_entry(self.audit_log, "ERROR", f"Failed to fetch email UID {uid.decode('utf-8')}.", "process_inbox")
                continue
            processed.append({k: email_info[k] for k in ("uid", "sender", "subject", "has_attachments", "attachments_meta")})
            log_audit_entry(self.audit_log, "INFO", f"Processing email '{email_info['subject']}' from {email_info['sender']}.",
                            "process_inbox", {"attachments": email_info["attachments_meta"]})

            matched_any = False
            for i, rule in enumerate(rules, start=1):
                rule_name = rule.get("name", f"rule_{i}")
                if self._rule_matches(rule.get("if", {}), email_info):
                    matched_any = True
                    log_audit_entry(self.audit_log, "INFO", f"Rule '{rule_name}' matched email UID {email_info['uid']}.", "rule_match")
                    self._apply_rule_actions(rule_name, rule.get("then", {}), email_info)
            if not matched_any:
                logger.info(f"No rule matched for email UID {email_info['uid']}.")

        return True, {"processed_emails": processed}

    def _process_task(self, task):
        """Dispatches a task to the appropriate handler and manages context."""
        task_type = task.get("type")
        task_name = task.get("name", task_type)
        output_context_key = task.get("output_context_key")

        logger.info(f"Executing task: '{task_name}' (Type: {task_type})")
        log_audit_entry(self.audit_log, "INFO", f"Starting task '{task_name}'", task_type)

        handler = self.handlers.get(task_type)
        if handler is None:
            log_audit_entry(self.audit_log, "WARNING", f"Unsupported task type: {task_type}", task_type, task)
            return

        try:
            success, task_output_data = handler(task.get("parameters", {}))

            # Store the output data so later tasks can use it in their templates
            if success and task_output_data is not None and output_context_key:
                self._update_context(output_context_key, task_output_data)

            if success:
                log_audit_entry(self.audit_log, "SUCCESS", f"Task '{task_name}' completed successfully.", task_type,
                                task_output_data)
            else:
                log_audit_entry(self.audit_log, "ERROR", f"Task '{task_name}' failed.", task_type, task_output_data)
        except Exception as e:
            log_audit_entry(self.audit_log, "ERROR", f"An error occurred during task '{task_name}': {e}", task_type,
                            {"error": str(e)})
            logger.error(f"Error during task '{task_name}': {e}", exc_info=True)

    def _generate_audit_report(self, output_dir="reports"):
        """Generates a JSON audit report."""
        ensure_directory_exists(output_dir)
        report_filename = f"audit_report_comm_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = os.path.join(output_dir, report_filename)
        try:
            log_audit_entry(self.audit_log, "INFO", f"Audit report generated at {report_path}", "audit_report")
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(self.audit_log, f, indent=4, ensure_ascii=False, default=str)
            logger.info(f"Audit report saved to: {report_path}")
        except Exception as e:
            logger.error(f"Failed to save audit report: {e}")
        return report_path

    def run(self, initial_context=None):
        """Executes all tasks defined in the configuration."""
        logger.info("Starting Communication Agent run...")
        log_audit_entry(self.audit_log, "INFO", f"Communication Agent started ({'DRY RUN' if self.dry_run else 'LIVE'}).", "agent_run")

        # Data that might come from previous agent runs (e.g., the Week 8 Data Agent)
        self._update_context("report_date", datetime.date.today().strftime("%Y-%m-%d"))
        for key, value in {**self.config.get("initial_context", {}), **(initial_context or {})}.items():
            self._update_context(key, value)

        for task in self.config.get("tasks", []):
            self._process_task(task)

        duration = (datetime.datetime.now() - self.start_time).total_seconds()
        log_audit_entry(self.audit_log, "INFO", f"Communication Agent finished in {duration:.2f} seconds.", "agent_run_summary")

        # Save audit report in a dedicated 'reports' subfolder within the base directory
        return self._generate_audit_report(os.path.join(self.base_dir, 'reports'))
