# email-sms-automator/main.py
import sys

import os
import time
# Add the &#39;src&#39; directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), &#39;src&#39;))
from email_sender import EmailSender
from email_receiver import EmailReceiver
from sms_gateway import SMSGateway
from utils import setup_logging, get_env_variable, ensure_directory_exists
logger = setup_logging(__name__)
def main():
&quot;&quot;&quot;
Main function to orchestrate email and SMS automation tasks.
&quot;&quot;&quot;
base_dir = os.path.dirname(__file__)
data_dir = os.path.join(base_dir, &#39;data&#39;)
attachments_dir = os.path.join(data_dir, &#39;attachments&#39;)
ensure_directory_exists(data_dir)
ensure_directory_exists(attachments_dir)
# --- Load Credentials from Environment Variables ---
try:
sender_email = get_env_variable(&quot;SENDER_EMAIL&quot;)
sender_app_password = get_env_variable(&quot;SENDER_APP_PASSWORD&quot;)
smtp_server = get_env_variable(&quot;SMTP_SERVER&quot;)
smtp_port = int(get_env_variable(&quot;SMTP_PORT&quot;))
imap_server = get_env_variable(&quot;IMAP_SERVER&quot;)
test_recipient_email = get_env_variable(&quot;TEST_RECIPIENT_EMAIL&quot;)
test_sms_phone_number = get_env_variable(&quot;TEST_SMS_PHONE_NUMBER&quot;)
test_sms_carrier = get_env_variable(&quot;TEST_SMS_CARRIER&quot;)
except ValueError as e:
logger.critical(f&quot;Configuration error: {e}. Please set all required environment variables in your .env
file.&quot;)
sys.exit(1)
# --- Initialize Handlers ---
email_sender = EmailSender(smtp_server, smtp_port, sender_email, sender_app_password)
email_receiver = EmailReceiver(imap_server, sender_email, sender_app_password)
sms_gateway = SMSGateway(email_sender)
# --- Task 1: Send a simple plaintext email ---

logger.info(&quot;\n--- Task 1: Sending a simple plaintext email ---&quot;)
email_sender.send_email(
recipient_email=test_recipient_email,
subject=&quot;Automated Python Test Email&quot;,
body=&quot;Hello from your Python automation script! This is a plain text email.&quot;
)
time.sleep(2) # Give a short delay
# --- Task 2: Send an email with an attachment ---
logger.info(&quot;\n--- Task 2: Sending an email with an attachment ---&quot;)
attachment_file_path = os.path.join(data_dir, &#39;dummy_report.pdf&#39;)
if os.path.exists(attachment_file_path):
email_sender.send_email(
recipient_email=test_recipient_email,
subject=&quot;Python Test Email with Attachment - Daily Report&quot;,
body=&quot;Please find the daily report attached.&quot;,
attachment_path=attachment_file_path
)
else:
logger.warning(f&quot;Attachment file not found at &#39;{attachment_file_path}&#39;. Skipping attachment email.&quot;)
time.sleep(2) # Give a short delay
# --- Task 3: Send an SMS via email gateway ---
logger.info(&quot;\n--- Task 3: Sending an SMS via email gateway ---&quot;)
sms_message = &quot;Hello from Python! This is an automated SMS via email gateway.&quot;
sms_gateway.send_sms(
phone_number=test_sms_phone_number,
message=sms_message,
carrier_name=test_sms_carrier
)
time.sleep(5) # Give more time for SMS to arrive
# --- Task 4: Receive and process emails ---
logger.info(&quot;\n--- Task 4: Receiving and processing emails ---&quot;)
# Send a new email to self to ensure there&#39;s an email to find for demo
email_sender.send_email(
recipient_email=sender_email, # Send to self
subject=&quot;Python Test: Email for Receiving Demo&quot;,
body=&quot;This email is specifically for the receiving demo. It has an attachment!&quot;,
attachment_path=attachment_file_path # Attach the dummy report again
)
logger.info(&quot;Sent a demo email to self for receiving task. Waiting a few seconds...&quot;)
time.sleep(10) # Give email server time to process and deliver

# Search for unseen emails from self with a specific subject
uids = email_receiver.search_emails(
criteria=&#39;UNSEEN&#39;,
from_sender=sender_email,
subject_contains=&quot;Python Test: Email for Receiving Demo&quot;
)
if uids:
logger.info(f&quot;Found {len(uids)} matching unread email(s) for receiving demo.&quot;)
for uid in uids:
logger.info(f&quot;Processing email UID: {uid.decode(&#39;utf-8&#39;)}&quot;)
email_details = email_receiver.fetch_email_content(
uid=uid,
mark_as_read=True,
download_attachments_dir=attachments_dir
)
if email_details:
logger.info(f&quot; Sender: {email_details[&#39;sender&#39;]}&quot;)
logger.info(f&quot; Subject: {email_details[&#39;subject&#39;]}&quot;)
logger.info(f&quot; Body Snippet: {email_details[&#39;body_snippet&#39;]}&quot;)
if email_details[&#39;attachments_downloaded&#39;]:
logger.info(f&quot; Attachments downloaded: {&#39;,
&#39;.join(email_details[&#39;attachments_downloaded&#39;])}&quot;)
else:
logger.info(&quot; No attachments downloaded for this email.&quot;)
else:
logger.error(f&quot;Could not retrieve details for email UID: {uid.decode(&#39;utf-8&#39;)}&quot;)
else:
logger.info(&quot;No matching unread emails found for receiving demo.&quot;)
logger.info(&quot;\n--- All communication automation tasks completed ---&quot;)
if __name__ == &quot;__main__&quot;:
main()