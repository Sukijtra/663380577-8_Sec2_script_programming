# Week 12: Agentic Communication Workflows (Advanced Email & SMS)

This project introduces an "Agentic Communication Automator" that executes email and SMS workflows defined declaratively in a JSON configuration file. It extends basic sending/receiving with dynamic content templating, rule-based inbox processing, and contextual data flow between tasks.

## Key Concepts Demonstrated

* **Communication Agent**: `CommunicationAgent` runs the sequence of tasks in `configs/comm_pipeline_config.json` through a **task dispatcher** (`send_email`, `send_sms`, `process_inbox`).
* **Contextual Data Flow**: The agent keeps a `context` dictionary (report date, sales figure, results of earlier tasks via `output_context_key`) that fills the templates.
* **Dynamic Content Templating** (`TemplateRenderer`):
    * `${ENV_VAR}` → value from `.env` (e.g. `${SENDER_EMAIL}`)
    * `{key}` → value from the agent's context, with Python format specs (`${sales_figure:,.2f}` → `$12,345.67`) and indexing (`{attachments_meta[0][filename]}`)
* **Advanced Email Sending**: To / CC / BCC, plain text or HTML, multiple attachments (missing attachments are skipped and logged).
* **Rule-Based Inbox Processing**: IMAP search (status, sender, subject) → download attachments → mark as read → apply **if/then rules**:
    * Conditions: `subject_contains`, `body_contains`, `from_contains`, `has_attachments`
    * Actions: `send_sms_alert`, `reply_with_template`
* **SMS via Email-to-SMS Gateway**: `SMSTasks` sends SMS to `number@carrier-gateway` using the email sender.
* **Secure Credential Handling**: Credentials are read from `.env`, which is git-ignored. Only `.env.example` is committed.
* **Dry-Run Mode**: With `DRY_RUN=true` nothing is sent over the network. Emails/SMS are saved as `.eml` files in `data/dry_run_mailbox/`, and `process_inbox` reads from that folder — so the full send → receive → rules workflow can be tested without a Gmail account.
* **Audit Logging**: Every action is recorded in `reports/audit_report_comm_*.json`.

## Setup & How to Run

1. **Clone the repository:**
    ```bash
    git clone https://github.com/Sukijtra/663380577-8_Sec2_script_programming.git
    cd "663380577-8_Sec2_script_programming/LabX Advance/Week 12 - Agentic Communication Workflows"
    ```
2. **Install Dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate.bat
    pip install -r requirements.txt
    ```
3. **Sample attachments** are provided in `data/reports/` (`sales_report.pdf`, `summary_data.xlsx`).
4. **Create the `.env` file** from the example:
    ```bash
    cp .env.example .env
    ```
    ```ini
    DRY_RUN=true

    SENDER_EMAIL=your_gmail_address@gmail.com
    SENDER_APP_PASSWORD=your_generated_gmail_app_password
    SMTP_SERVER=smtp.gmail.com
    SMTP_PORT=587
    IMAP_SERVER=imap.gmail.com

    TEST_RECIPIENT_EMAIL=another_email@example.com
    TEST_SMS_PHONE_NUMBER=1234567890
    TEST_SMS_CARRIER=att
    ```
    **Never commit `.env` to GitHub.**
5. **Run the script:**
    ```bash
    python main.py
    ```

### Running for real (Gmail)

1. Turn on **2-Step Verification** in your Google Account.
2. Go to Google Account → Security → **App passwords** and create one. Put it in `SENDER_APP_PASSWORD` (your normal password will not work).
3. Set `DRY_RUN=false` in `.env` and run `python main.py` again.

> **Note on SMS:** Email-to-SMS gateways (`@txt.att.net`, `@vtext.com`, …) only exist for some US carriers. Thai carriers do not provide them, so for real SMS in Thailand use an SMS API provider and replace `SMSTasks.send_sms`. You can also put a full gateway address (e.g. `5551234567@vtext.com`) directly in `TEST_SMS_PHONE_NUMBER`.

## What the Workflow Does

| # | Task | Result |
|---|------|--------|
| 1 | Send Daily Sales Report Email | Email to `TEST_RECIPIENT_EMAIL` (CC self) with subject `Daily Sales Report - <date>`, total sales/customers in the body and 2 attachments |
| 2 | Send Sales Alert SMS | `Sales for <date> are $12,345.67. Total customers: 500. Review!` |
| 3 | Simulate Incoming Request Email | Sends `Data Request for <date> - Urgent` (with attachment) to yourself |
| 4 | Process Incoming Data Requests | Finds that email, downloads the attachment to `data/incoming_attachments/`, marks it read, then:<br>• Rule 1 (subject has "Urgent" + has attachments) → **SMS alert**<br>• Rule 2 (body has "new data processing") → **auto-reply** `Re: … - Received & Processing` |

### Example log (dry run)

```
AUDIT LOG - SUCCESS: Task 'Send Daily Sales Report Email' completed successfully.
AUDIT LOG - SUCCESS: Task 'Send Sales Alert SMS' completed successfully.
AUDIT LOG - SUCCESS: Task 'Simulate Incoming Request Email (to self)' completed successfully.
[DRY RUN] Found 1 emails matching criteria in local mailbox.
AUDIT LOG - INFO: Rule 'Urgent request with attachments -> SMS alert' matched email ...
AUDIT LOG - SUCCESS: Rule 'Urgent request with attachments -> SMS alert': SMS alert sent.
AUDIT LOG - INFO: Rule 'New data processing request -> auto reply' matched email ...
AUDIT LOG - SUCCESS: Rule 'New data processing request -> auto reply': auto-reply sent to ...
AUDIT LOG - SUCCESS: Task 'Process Incoming Data Requests' completed successfully.
```

## Project Structure

```
agentic-comm-automator/
├── src/
│   ├── __init__.py
│   ├── communication_agent.py  # Core agent: dispatches tasks, manages context, applies inbox rules
│   ├── email_tasks.py          # SMTP sending, IMAP search/fetch, attachment download (+ dry-run mailbox)
│   ├── sms_tasks.py            # SMS via email-to-SMS gateways
│   ├── config_parser.py        # Loads and validates the JSON configuration
│   ├── template_renderer.py    # ${ENV} and {context} template rendering
│   └── utils.py                # Logging, .env loading, directory helpers, audit logging
├── configs/
│   └── comm_pipeline_config.json
├── data/
│   ├── attachments/            # General attachments folder
│   ├── reports/                # Sample reports to send
│   │   ├── sales_report.pdf
│   │   └── summary_data.xlsx
│   └── incoming_attachments/   # Attachments downloaded from processed emails (git-ignored)
├── .env.example                # Template for .env (copy to .env and fill in)
├── .env                        # Your credentials (YOU CREATE, git-ignored)
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Debugging Tips

* **`Environment variable '...' not set`**: Create `.env` from `.env.example` and fill every value (only needed when `DRY_RUN=false`).
* **`SMTPAuthenticationError` / `IMAP4.error`**: Use a Gmail **App password**, and check `SMTP_SERVER`, `SMTP_PORT`, `IMAP_SERVER`.
* **Inbox task finds 0 emails**: The search only matches **UNSEEN** emails from `SENDER_EMAIL` with "Data Request" in the subject. Gmail may take a few seconds to deliver the simulated email.
* **`Missing context key`**: A `{placeholder}` in the config is not in the agent context or the email info.
* **Audit report**: Check `reports/audit_report_comm_*.json` to see exactly what each step did.
