# agentic-comm-automator/src/email_tasks.py
import smtplib
import imaplib
import email
import os
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.header import decode_header
from .utils import setup_logging, ensure_directory_exists

logger = setup_logging(__name__)


class EmailTasks:
    """
    Handles sending and receiving emails via SMTP and IMAP protocols.

    In dry-run mode nothing goes over the network: sent emails are written as .eml files
    to `mailbox_dir`, and inbox searches read from that same folder. This lets the whole
    workflow (send -> receive -> apply rules) be tested without real credentials.
    """
    def __init__(self, smtp_server, smtp_port, imap_server, sender_email, sender_password,
                 dry_run=False, mailbox_dir=None):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.imap_server = imap_server
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.dry_run = dry_run
        self.mailbox_dir = mailbox_dir
        self._smtp_server = None  # Internal SMTP server object
        self._imap_mail = None    # Internal IMAP mail object
        mode = f"DRY RUN (mailbox: {mailbox_dir})" if dry_run else "LIVE"
        logger.info(f"EmailTasks initialized for {sender_email} [{mode}].")

    # --- SMTP (Sending) Methods ---
    def _connect_smtp(self):
        """Establishes and logs into the SMTP server."""
        if self._smtp_server:  # Already connected
            return True
        try:
            self._smtp_server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
            self._smtp_server.starttls()  # Secure the connection
            self._smtp_server.login(self.sender_email, self.sender_password)
            logger.info("Successfully connected and logged into SMTP server.")
            return True
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed. Check email and app password. Error: {e}")
        except (smtplib.SMTPConnectError, OSError) as e:
            logger.error(f"SMTP connection failed. Check server address and port. Error: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during SMTP connect/login: {e}")
        self._smtp_server = None
        return False

    def _disconnect_smtp(self):
        """Disconnects from the SMTP server."""
        if self._smtp_server:
            try:
                self._smtp_server.quit()
                logger.info("Disconnected from SMTP server.")
            except Exception as e:
                logger.warning(f"Error during SMTP disconnection: {e}")
            finally:
                self._smtp_server = None

    def _build_message(self, recipients, subject, body, attachments, is_html):
        """Builds a MIME message. Returns (message, list of all recipient addresses)."""
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['Subject'] = subject
        msg['Date'] = email.utils.formatdate(localtime=True)

        to_recipients = recipients.get('to', [])
        cc_recipients = recipients.get('cc', [])
        bcc_recipients = recipients.get('bcc', [])  # BCC is not written in the header

        msg['To'] = ", ".join(to_recipients)
        if cc_recipients:
            msg['Cc'] = ", ".join(cc_recipients)

        msg.attach(MIMEText(body, 'html' if is_html else 'plain', 'utf-8'))

        for attachment_path in attachments or []:
            if not os.path.exists(attachment_path):
                logger.warning(f"Attachment file not found: {attachment_path}. Skipping.")
                continue
            filename = os.path.basename(attachment_path)
            with open(attachment_path, "rb") as f:
                part = MIMEApplication(f.read(), Name=filename)
            part['Content-Disposition'] = f'attachment; filename="{filename}"'
            msg.attach(part)
            logger.info(f"Attached file: {attachment_path}")

        return msg, to_recipients + cc_recipients + bcc_recipients

    def send_email(self, recipients, subject, body, attachments=None, is_html=False):
        """
        Sends an email with dynamic content and multiple attachments.
        :param recipients: Dictionary with lists for 'to', 'cc', 'bcc'.
        :param subject: The subject line of the email.
        :param body: The content of the email.
        :param attachments: List of file paths to attach.
        :param is_html: Set to True if the body is HTML, False for plain text.
        :return: True if email sent successfully, False otherwise.
        """
        msg, all_recipients = self._build_message(recipients, subject, body, attachments, is_html)
        if not all_recipients:
            logger.error("No recipients specified for email.")
            return False

        if self.dry_run:
            ensure_directory_exists(self.mailbox_dir)
            filename = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.eml"
            with open(os.path.join(self.mailbox_dir, filename), "wb") as f:
                f.write(msg.as_bytes())
            logger.info(f"[DRY RUN] Email to {', '.join(all_recipients)} saved as {filename}. Subject: '{subject}'.")
            return True

        if not self._connect_smtp():
            return False
        try:
            self._smtp_server.send_message(msg, from_addr=self.sender_email, to_addrs=all_recipients)
            logger.info(f"Email sent successfully to {', '.join(all_recipients)}. Subject: '{subject}'.")
            return True
        except Exception as e:
            logger.error(f"Failed to send email. Error: {e}")
            return False
        finally:
            self._disconnect_smtp()

    # --- IMAP (Receiving) Methods ---
    def _connect_imap(self):
        """Establishes and logs into the IMAP server."""
        if self._imap_mail:  # Already connected
            return True
        try:
            self._imap_mail = imaplib.IMAP4_SSL(self.imap_server)
            self._imap_mail.login(self.sender_email, self.sender_password)
            logger.info("Successfully connected and logged into IMAP server.")
            return True
        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP authentication failed. Check email and app password. Error: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during IMAP connect/login: {e}")
        self._imap_mail = None
        return False

    def _disconnect_imap(self):
        """Disconnects from the IMAP server."""
        if self._imap_mail:
            try:
                self._imap_mail.logout()
                logger.info("Disconnected from IMAP server.")
            except Exception as e:
                logger.warning(f"Error during IMAP disconnection: {e}")
            finally:
                self._imap_mail = None

    def _search_local_mailbox(self, criteria, from_sender, subject_contains):
        """Dry-run version of search_emails: looks through .eml files in mailbox_dir."""
        if not os.path.isdir(self.mailbox_dir):
            return []
        uids = []
        for filename in sorted(os.listdir(self.mailbox_dir)):
            if not filename.endswith(".eml"):
                continue
            seen = filename.endswith(".seen.eml")
            if (criteria == "UNSEEN" and seen) or (criteria == "SEEN" and not seen):
                continue
            with open(os.path.join(self.mailbox_dir, filename), "rb") as f:
                msg = email.message_from_bytes(f.read())
            # Like IMAP, FROM and SUBJECT are case-insensitive "contains" matches
            if from_sender and from_sender.lower() not in self._decode_header_part(msg['From']).lower():
                continue
            if subject_contains and subject_contains.lower() not in self._decode_header_part(msg['Subject']).lower():
                continue
            uids.append(filename.encode())
        return uids

    def search_emails(self, mailbox='INBOX', criteria='UNSEEN', from_sender=None, subject_contains=None):
        """
        Searches for emails based on criteria.
        :param mailbox: Mailbox to search (e.g., 'INBOX').
        :param criteria: IMAP search criteria (e.g., 'UNSEEN', 'ALL', 'SEEN').
        :param from_sender: Filter by sender email address.
        :param subject_contains: Filter by subject line containing this string.
        :return: A list of email UIDs (bytes).
        """
        if self.dry_run:
            uids = self._search_local_mailbox(criteria, from_sender, subject_contains)
            logger.info(f"[DRY RUN] Found {len(uids)} emails matching criteria in local mailbox.")
            return uids

        if not self._connect_imap():
            return []
        try:
            self._imap_mail.select(mailbox)
            search_query = [criteria]
            if from_sender:
                search_query += ['FROM', f'"{from_sender}"']
            if subject_contains:
                search_query += ['SUBJECT', f'"{subject_contains}"']

            status, data = self._imap_mail.uid('search', None, *search_query)
            if status != 'OK':
                logger.error(f"IMAP search failed. Status: {status}")
                return []
            uids = data[0].split()
            logger.info(f"Found {len(uids)} emails matching criteria in '{mailbox}'.")
            return uids
        except Exception as e:
            logger.error(f"Error searching emails: {e}")
            return []
        finally:
            self._disconnect_imap()

    def fetch_email_content(self, uid, mark_as_read=True, download_attachments_dir=None, mailbox='INBOX'):
        """
        Fetches the content of a specific email by UID.
        Optionally marks as read and downloads attachments.
        :return: A dictionary containing email details or None.
        """
        if self.dry_run:
            path = os.path.join(self.mailbox_dir, uid.decode())
            with open(path, "rb") as f:
                msg = email.message_from_bytes(f.read())
            info = self._parse_message(msg, uid, download_attachments_dir)
            if mark_as_read and not path.endswith(".seen.eml"):
                os.rename(path, path[:-len(".eml")] + ".seen.eml")
                logger.info(f"[DRY RUN] Marked email {uid.decode()} as read.")
            return info

        if not self._connect_imap():
            return None
        try:
            self._imap_mail.select(mailbox)
            status, msg_data = self._imap_mail.uid('fetch', uid, '(RFC822)')
            if status != 'OK' or not msg_data or msg_data[0] is None:
                logger.error(f"Failed to fetch email UID {uid}. Status: {status}")
                return None
            msg = email.message_from_bytes(msg_data[0][1])
            info = self._parse_message(msg, uid, download_attachments_dir)
            if mark_as_read:
                self._imap_mail.uid('store', uid, '+FLAGS', '\\Seen')
                logger.info(f"Marked email UID {uid.decode('utf-8')} as read.")
            return info
        except Exception as e:
            logger.error(f"Error fetching/parsing email UID {uid.decode('utf-8')}: {e}")
            return None
        finally:
            self._disconnect_imap()

    def _parse_message(self, msg, uid, download_attachments_dir):
        """Extracts sender, subject, bodies and attachments from an email message."""
        email_text_body = ""
        email_html_body = ""
        attachments_meta = []  # List of dicts: {'filename': 'name', 'filepath': 'path'}

        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            filename = part.get_filename()

            if "attachment" in content_disposition or filename:
                if not filename:
                    continue
                # basename() prevents a malicious filename like "../../x" from escaping the folder
                filename = os.path.basename(self._decode_header_part(filename))
                filepath = None
                if download_attachments_dir:
                    ensure_directory_exists(download_attachments_dir)
                    filepath = os.path.join(download_attachments_dir, filename)
                    with open(filepath, "wb") as f:
                        f.write(part.get_payload(decode=True))
                    logger.info(f"Downloaded attachment: {filepath}")
                attachments_meta.append({'filename': filename, 'filepath': filepath})
            elif content_type == "text/plain":
                email_text_body += part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors='replace')
            elif content_type == "text/html":
                email_html_body += part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors='replace')

        return {
            "uid": uid.decode('utf-8'),
            "sender": self._decode_header_part(msg['From']),
            "subject": self._decode_header_part(msg['Subject']),
            "text_body": email_text_body,
            "html_body": email_html_body,
            "has_attachments": bool(attachments_meta),
            "attachments_meta": attachments_meta
        }

    def _decode_header_part(self, header_value):
        """Decodes header parts that might be encoded (e.g., '=?UTF-8?B?U3ViamVjdA==?=')."""
        if header_value is None:
            return ""
        decoded_string = ""
        for part, charset in decode_header(header_value):
            if isinstance(part, bytes):
                try:
                    decoded_string += part.decode(charset if charset else 'utf-8')
                except (LookupError, UnicodeDecodeError):
                    decoded_string += part.decode('latin-1', errors='replace')  # Fallback for decoding
            else:
                decoded_string += part
        return decoded_string.strip()
