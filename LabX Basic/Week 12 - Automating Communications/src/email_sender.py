# email-sms-automator/src/email_sender.py
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
from .utils import setup_logging
logger = setup_logging(__name__)
class EmailSender:
&quot;&quot;&quot;
Handles sending emails via SMTP.
&quot;&quot;&quot;
def __init__(self, smtp_server, smtp_port, sender_email, sender_password):
self.smtp_server = smtp_server
self.smtp_port = smtp_port
self.sender_email = sender_email
self.sender_password = sender_password
self.server = None
logger.info(f&quot;EmailSender initialized for {sender_email} via {smtp_server}:{smtp_port}.&quot;)
def _connect(self):
&quot;&quot;&quot;Establishes and logs into the SMTP server.&quot;&quot;&quot;
try:
self.server = smtplib.SMTP(self.smtp_server, self.smtp_port)
self.server.starttls() # Secure the connection
self.server.login(self.sender_email, self.sender_password)
logger.info(&quot;Successfully connected and logged into SMTP server.&quot;)
return True
except smtplib.SMTPAuthenticationError as e:
logger.error(f&quot;SMTP authentication failed. Check email and app password. Error: {e}&quot;)
self.server = None
return False
except smtplib.SMTPConnectError as e:
logger.error(f&quot;SMTP connection failed. Check server address and port. Error: {e}&quot;)
self.server = None
return False
except Exception as e:
logger.error(f&quot;An unexpected error occurred during SMTP connect/login: {e}&quot;)
self.server = None

return False
def _disconnect(self):
&quot;&quot;&quot;Disconnects from the SMTP server.&quot;&quot;&quot;
if self.server:
try:
self.server.quit()
logger.info(&quot;Disconnected from SMTP server.&quot;)
except Exception as e:
logger.warning(f&quot;Error during SMTP disconnection: {e}&quot;)
finally:
self.server = None
def send_email(self, recipient_email, subject, body, attachment_path=None, is_html=False):
&quot;&quot;&quot;
Sends an email.
:param recipient_email: The email address of the recipient.
:param subject: The subject line of the email.
:param body: The content of the email.
:param attachment_path: Optional path to a file to attach.
:param is_html: Set to True if the body is HTML, False for plain text.
:return: True if email sent successfully, False otherwise.
&quot;&quot;&quot;
if not self._connect():
return False
msg = MIMEMultipart()
msg[&#39;From&#39;] = self.sender_email
msg[&#39;To&#39;] = recipient_email
msg[&#39;Subject&#39;] = subject
# Attach body
if is_html:
msg.attach(MIMEText(body, &#39;html&#39;))
else:
msg.attach(MIMEText(body, &#39;plain&#39;))
# Attach file if path is provided
if attachment_path:
try:
with open(attachment_path, &quot;rb&quot;) as f:
part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
part[&#39;Content-Disposition&#39;] = f&#39;attachment; filename=&quot;{os.path.basename(attachment_path)}&quot;&#39;
msg.attach(part)
logger.info(f&quot;Attached file: {attachment_path}&quot;)

except FileNotFoundError:
logger.error(f&quot;Attachment file not found: {attachment_path}. Email will be sent without it.&quot;)
except Exception as e:
logger.error(f&quot;Error attaching file {attachment_path}: {e}. Email will be sent without it.&quot;)
try:
self.server.send_message(msg)
logger.info(f&quot;Email sent successfully to {recipient_email} with subject: &#39;{subject}&#39;.&quot;)
return True
except Exception as e:
logger.error(f&quot;Failed to send email to {recipient_email}. Error: {e}&quot;)
return False
finally:
self._disconnect()