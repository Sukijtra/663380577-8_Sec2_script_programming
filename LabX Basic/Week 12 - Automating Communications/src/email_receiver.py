# email-sms-automator/src/email_receiver.py
import imaplib
import email
from email.header import decode_header
import os
from .utils import setup_logging, ensure_directory_exists
logger = setup_logging(__name__)
class EmailReceiver:
&quot;&quot;&quot;
Handles receiving and parsing emails via IMAP.
&quot;&quot;&quot;
def __init__(self, imap_server, sender_email, sender_password):
self.imap_server = imap_server
self.sender_email = sender_email
self.sender_password = sender_password
self.mail = None
logger.info(f&quot;EmailReceiver initialized for {sender_email} via {imap_server}.&quot;)
def _connect(self):
&quot;&quot;&quot;Establishes and logs into the IMAP server.&quot;&quot;&quot;

try:
self.mail = imaplib.IMAP4_SSL(self.imap_server)
self.mail.login(self.sender_email, self.sender_password)
logger.info(&quot;Successfully connected and logged into IMAP server.&quot;)
return True
except imaplib.IMAP4.error as e:
logger.error(f&quot;IMAP authentication failed. Check email and app password. Error: {e}&quot;)
self.mail = None
return False
except Exception as e:
logger.error(f&quot;An unexpected error occurred during IMAP connect/login: {e}&quot;)
self.mail = None
return False
def _disconnect(self):
&quot;&quot;&quot;Disconnects from the IMAP server.&quot;&quot;&quot;
if self.mail:
try:
self.mail.logout()
logger.info(&quot;Disconnected from IMAP server.&quot;)
except Exception as e:
logger.warning(f&quot;Error during IMAP disconnection: {e}&quot;)
finally:
self.mail = None
def search_emails(self, mailbox=&#39;INBOX&#39;, criteria=&#39;UNSEEN&#39;, from_sender=None,
subject_contains=None):
&quot;&quot;&quot;
Searches for emails based on criteria.
:param mailbox: Mailbox to search (e.g., &#39;INBOX&#39;).
:param criteria: IMAP search criteria (e.g., &#39;UNSEEN&#39;, &#39;ALL&#39;, &#39;SEEN&#39;).
:param from_sender: Filter by sender email address.
:param subject_contains: Filter by subject line containing this string.
:return: A list of email UIDs (unique identifiers).
&quot;&quot;&quot;
if not self._connect():
return []
try:
self.mail.select(mailbox)
search_query = [criteria]
if from_sender:
search_query.extend([&#39;FROM&#39;, from_sender])
if subject_contains:
search_query.extend([&#39;SUBJECT&#39;, subject_contains])

status, email_ids = self.mail.search(None, *search_query)
if status != &#39;OK&#39;:
logger.error(f&quot;IMAP search failed. Status: {status}&quot;)
return []
uids = email_ids[0].split()
logger.info(f&quot;Found {len(uids)} emails matching criteria in &#39;{mailbox}&#39;.&quot;)
return uids
except Exception as e:
logger.error(f&quot;Error searching emails: {e}&quot;)
return []
finally:
self._disconnect()
def fetch_email_content(self, uid, mark_as_read=True, download_attachments_dir=None):
&quot;&quot;&quot;
Fetches the content of a specific email by UID.
Optionally marks as read and downloads attachments.
:param uid: The unique ID of the email.
:param mark_as_read: If True, marks the email as SEEN.
:param download_attachments_dir: Directory to save attachments, or None to skip.
:return: A dictionary containing email details (sender, subject, body, attachments_downloaded) or
None.
&quot;&quot;&quot;
if not self._connect(): # Reconnect if needed for fetching specific email
return None
try:
self.mail.select(&#39;INBOX&#39;) # Select inbox again as previous connection might have been for
search
# Fetch the email by UID
status, msg_data = self.mail.fetch(uid, &#39;(RFC822)&#39;)
if status != &#39;OK&#39;:
logger.error(f&quot;Failed to fetch email UID {uid}. Status: {status}&quot;)
return None
raw_email = msg_data[0][1]
msg = email.message_from_bytes(raw_email)
sender = self._decode_header_part(msg[&#39;From&#39;])
subject = self._decode_header_part(msg[&#39;Subject&#39;])
email_body = &quot;&quot;

attachments_downloaded = []
for part in msg.walk():
content_type = part.get_content_type()
content_disposition = str(part.get(&quot;Content-Disposition&quot;))
if &quot;attachment&quot; in content_disposition:
filename = part.get_filename()
if filename and download_attachments_dir:
ensure_directory_exists(download_attachments_dir)
filepath = os.path.join(download_attachments_dir, filename)
try:
with open(filepath, &quot;wb&quot;) as f:
f.write(part.get_payload(decode=True))
attachments_downloaded.append(filepath)
logger.info(f&quot;Downloaded attachment: {filepath}&quot;)
except Exception as e:
logger.error(f&quot;Error downloading attachment {filename}: {e}&quot;)
elif &quot;text/plain&quot; in content_type and not &quot;attachment&quot; in content_disposition:
try:
email_body +=
part.get_payload(decode=True).decode(part.get_content_charset() or &#39;utf-8&#39;)
except Exception as e:
logger.warning(f&quot;Could not decode plain text part from email UID {uid}. Error: {e}&quot;)
email_body += &quot;[ undecodable plain text part ]&quot;
elif &quot;text/html&quot; in content_type and not &quot;attachment&quot; in content_disposition:
# For simplicity, we prioritize plain text or capture HTML as is
pass # You might want to parse HTML differently
if mark_as_read:
self.mail.store(uid, &#39;+FLAGS&#39;, &#39;\\Seen&#39;)
logger.info(f&quot;Marked email UID {uid} as read.&quot;)
return {
&quot;uid&quot;: uid.decode(&#39;utf-8&#39;),
&quot;sender&quot;: sender,
&quot;subject&quot;: subject,
&quot;body_snippet&quot;: email_body[:200] + &quot;...&quot; if len(email_body) &gt; 200 else email_body,
&quot;attachments_downloaded&quot;: attachments_downloaded
}
except Exception as e:
logger.error(f&quot;Error fetching/parsing email UID {uid}: {e}&quot;)
return None
finally:
self._disconnect()

def _decode_header_part(self, header_value):
&quot;&quot;&quot;Decodes header parts that might be encoded (e.g., &#39;=?UTF-8?B?U3ViamVjdA==?=&#39;).&quot;&quot;&quot;
if header_value is None:
return &quot;&quot;
decoded_parts = decode_header(header_value)
decoded_string = &quot;&quot;
for part, charset in decoded_parts:
if isinstance(part, bytes):
try:
decoded_string += part.decode(charset if charset else &#39;utf-8&#39;)
except:
decoded_string += part.decode(&#39;latin-1&#39;, errors=&#39;replace&#39;) # Fallback for decoding
else:
decoded_string += part
return decoded_string.strip()