# email-sms-automator/src/sms_gateway.py
from .utils import setup_logging
from .email_sender import EmailSender
logger = setup_logging(__name__)
class SMSGateway:
&quot;&quot;&quot;
Provides a simplified interface to send SMS via email-to-SMS gateways.
Relies on EmailSender for the actual email transmission.
&quot;&quot;&quot;
def __init__(self, email_sender_instance):
if not isinstance(email_sender_instance, EmailSender):
raise TypeError(&quot;SMSGateway requires an instance of EmailSender.&quot;)
self.email_sender = email_sender_instance
# Common US carrier email-to-SMS gateways (add more as needed)
self.carrier_gateways = {
&quot;att&quot;: &quot;@txt.att.net&quot;,
&quot;verizon&quot;: &quot;@vtext.com&quot;,

&quot;tmobile&quot;: &quot;@tmomail.net&quot;,
&quot;sprint&quot;: &quot;@messaging.sprintpcs.com&quot;,
&quot;boost&quot;: &quot;@sms.boostmobile.com&quot;,
&quot;cricket&quot;: &quot;@mms.cricketwireless.net&quot;,
&quot;us_cellular&quot;: &quot;@email.uscc.net&quot;,
# Add international carriers if known
}
logger.info(&quot;SMSGateway initialized.&quot;)
def send_sms(self, phone_number, message, carrier_name=None):
&quot;&quot;&quot;
Sends an SMS message via email-to-SMS gateway.
:param phone_number: Recipient phone number (e.g., &#39;1234567890&#39;).
:param message: The text message content.
:param carrier_name: Optional, specific carrier (e.g., &#39;att&#39;, &#39;verizon&#39;). If None, tries common ones or
assumes phone_number includes gateway.
:return: True if message sent (email-wise), False otherwise.
&quot;&quot;&quot;
sms_gateway_address = None
if carrier_name and carrier_name.lower() in self.carrier_gateways:
sms_gateway_address = f&quot;{phone_number}{self.carrier_gateways[carrier_name.lower()]}&quot;
elif &#39;@&#39; in phone_number and &#39;.&#39; in phone_number: # Assume phone_number is already a full
gateway address
sms_gateway_address = phone_number
else:
logger.warning(&quot;No specific carrier provided and phone number is not a gateway address.
Cannot send SMS.&quot;)
return False
if sms_gateway_address:
subject = &quot;&quot; # SMS emails usually don&#39;t show the subject
logger.info(f&quot;Attempting to send SMS to {phone_number} via gateway:
{sms_gateway_address}&quot;)
return self.email_sender.send_email(sms_gateway_address, subject, message)
else:
logger.error(&quot;Could not determine SMS gateway address.&quot;)
return False