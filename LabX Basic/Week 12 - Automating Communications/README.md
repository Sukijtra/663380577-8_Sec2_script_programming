# Week 21: Automating Communications (Email &amp; SMS)
This project demonstrates how to automate sending and receiving emails, and sending SMS
messages, using Python. It covers the use of `smtplib` for sending, `imaplib` for receiving, and
leveraging email-to-SMS gateways for text messages. Secure handling of credentials via
environment variables is a key focus.
## Key Concepts Demonstrated
* **Email Sending (SMTP)**:
* Connecting to an SMTP server (e.g., Gmail&#39;s) securely with TLS.
* Authenticating with an &quot;App password&quot; (crucial for 2FA-enabled accounts).
* Constructing multi-part emails with `email.mime` for plaintext, HTML, and file attachments.
* **Email Receiving (IMAP)**:
* Connecting to an IMAP server securely.
* Searching for emails based on various criteria (sender, subject, seen/unseen status).
* Fetching email content, including parsing message parts and extracting attachments.
* Marking emails as read.

* **SMS via Email Gateway**:
* Understanding the concept of carrier-specific email-to-SMS addresses.
* Sending a message to a phone number using this method.
* **Secure Credential Handling**:
* Utilizing `.env` files and `python-dotenv` to load sensitive information (email, password) as
environment variables, preventing hardcoding.
* **Modular Design**: Code is organized into `email_sender.py`, `email_receiver.py`,
`sms_gateway.py`, and `utils.py` for clarity and reusability.
* **Logging**: Informative logging to track the execution of communication tasks.
## Setup &amp; How to Run
1. **Clone the repository:**
```bash
git clone [https://github.com/YOUR_USERNAME/email-sms-
automator.git](https://github.com/YOUR_USERNAME/email-sms-automator.git)
cd email-sms-automator
```
2. **Install Dependencies:**
This project primarily uses built-in Python modules (`smtplib`, `imaplib`, `email`). The only external
dependency is `python-dotenv` for loading environment variables.
```bash
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate.bat
pip install python-dotenv
```
3. **Prepare Input Data Files:**
* Create a folder named `data` in the root of your project: `mkdir data`.
* Inside `data`, create an `attachments` subfolder: `mkdir data/attachments`. This is where downloaded
attachments will be saved.
* **`data/dummy_report.pdf`**: Create any simple PDF file and save it as `dummy_report.pdf` inside
the `data` folder. This will be used as a sample attachment.
4. **Configure Environment Variables (`.env` file):**
* In the root directory of your project, create a file named `.env`.
* **DO NOT COMMIT THIS FILE TO GITHUB OR ANY PUBLIC REPOSITORY!**
* Populate it with your email credentials and test recipient information:
```ini
# .env
SENDER_EMAIL=your_gmail_address@gmail.com
SENDER_APP_PASSWORD=your_generated_gmail_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
IMAP_SERVER=imap.gmail.com
# Recipient for test emails
TEST_RECIPIENT_EMAIL=another_email@example.com

# Recipient for test SMS via email gateway (replace with your actual phone number and carrier)
TEST_SMS_PHONE_NUMBER=1234567890
TEST_SMS_CARRIER=att # or verizon, tmobile, sprint, boost, us_cellular, cricket, etc.
```
* **Important for Gmail Users:** If you have 2-Step Verification (2FA) enabled (highly
recommended), you **must** generate an &quot;App password&quot; for your Python script to log in. Your
regular Gmail password will *not* work for programmatic access.
* Go to your Google Account.
* Navigate to &quot;Security&quot; -&gt; &quot;How you sign in to Google&quot; -&gt; &quot;App passwords&quot;.
* Follow the instructions to generate a new app password. Use this password for
`SENDER_APP_PASSWORD`.
* If you *do not* have 2FA, you might need to enable &quot;Less secure app access&quot; in your
Google Account settings, but this is **not recommended** for security reasons. Enable 2FA and
use an App Password instead.
5. **Run the script:**
```bash
python main.py
```
The script will:
* Attempt to send a simple plaintext email to `TEST_RECIPIENT_EMAIL`.
* Attempt to send an email with `dummy_report.pdf` as an attachment to `TEST_RECIPIENT_EMAIL`.
* Attempt to send an SMS to `TEST_SMS_PHONE_NUMBER` via the specified
`TEST_SMS_CARRIER` gateway.
* Send a demo email *to yourself* (your `SENDER_EMAIL`) with an attachment.
* Search your inbox for unread emails from `SENDER_EMAIL` with a specific subject.
* If found, it will print details, download attachments to `data/attachments/`, and mark the email as read.
## Project Structure

email-sms-automator/
├── src/
│ ├── init.py # Python package marker
│ ├── email_sender.py # Logic for sending emails via SMTP
│ ├── email_receiver.py # Logic for receiving emails via IMAP
│ ├── sms_gateway.py # Logic for sending SMS via email gateways
│ └── utils.py # Logging, env var loading, directory helpers
├── data/
│ ├── attachments/ # Directory where received attachments will be saved
│ └── dummy_report.pdf # Sample PDF file for sending as attachment (YOU CREATE)
├── .env # Environment variables for sensitive credentials (YOU CREATE &amp; DO NOT
COMMIT)
├── main.py # Main script to run the automation workflow
├── .gitignore # Files/folders to ignore in Git

└── README.md # This project overview

## Debugging Automated Communications
* **`ValueError: Environment variable &#39;...&#39; not set`**:
* You forgot to create the `.env` file, or it&#39;s not in the root directory.
* You have a typo in the variable name in `.env` or `main.py`.
* **`SMTPAuthenticationError`**:
* **Most common issue:** Your `SENDER_APP_PASSWORD` is incorrect or you used your
regular Gmail password instead of an App Password. **Generate an App Password!**
* If you don&#39;t use 2FA, ensure &quot;Less secure app access&quot; is enabled (though not
recommended).
* Your `SENDER_EMAIL` might be incorrect.
* **`SMTPConnectError` / `IMAP4.error` (Connection issues)**:
* Check `SMTP_SERVER`, `SMTP_PORT`, and `IMAP_SERVER` values. For Gmail, they
are `smtp.gmail.com:587` and `imap.gmail.com`.
* Firewall: Your network&#39;s firewall might be blocking outbound connections on these ports.
* Internet connection: Ensure you have a stable internet connection.
* **Emails not arriving**:
* Check recipient&#39;s spam folder.
* Ensure `send_email` method returns `True`.
* SMTP server might have rate limits if you send too many emails too quickly.
* **Attachments not sending/downloading**:
* Ensure the `attachment_path` is correct and the file exists.
* Check the `data/attachments` directory after running for downloaded files.
* **SMS not arriving**:
* Double-check the `TEST_SMS_PHONE_NUMBER` and `TEST_SMS_CARRIER`. Carrier
gateways can change or be unreliable.
* Email-to-SMS messages might be filtered as spam by carriers.
* **Email content decoding issues**: If you see garbled text, it&#39;s likely an encoding problem. The
`_decode_header_part` function handles common cases, but some emails can have unusual
encodings.
## Extension Ideas (Future Work)
* **Scheduled Notifications**: Integrate with a scheduling library (e.g., `APScheduler` or
`schedule`) to send emails/SMS at specific times or intervals (e.g., daily reports, weekly
summaries).
* **Dynamic Email Content**: Generate personalized email content using template engines
(e.g., Jinja2) based on data from databases or files.
* **Interactive Email Processing**: Build a system that responds to specific commands or

keywords in incoming emails (e.g., &quot;status report&quot; in subject triggers a data fetch and email
reply).
* **Webhooks for Alerts**: Instead of polling IMAP, set up a webhook if your email provider
supports it, to receive instant notifications of new emails.
* **Robust SMS API Integration**: For production-grade SMS solutions, integrate with dedicated
SMS APIs like [Twilio](https://www.twilio.com/sms) or
[Nexmo/Vonage](https://www.vonage.com/communications-apis/messages/sms/) for better
reliability, delivery reports, and two-way messaging.
* **Email List Management**: Build functions to manage a list of recipients (add, remove,
segment) and send bulk emails while adhering to anti-spam regulations.
* **Error Reporting**: Configure the system to email or SMS you directly when critical errors
occur in your automated scripts.