# agentic-comm-automator/src/sms_tasks.py
from .utils import setup_logging
from .email_tasks import EmailTasks  # Reuse EmailTasks for sending the actual email

logger = setup_logging(__name__)


class SMSTasks:
    """
    Provides a simplified interface to send SMS via email-to-SMS gateways.
    Relies on EmailTasks for the actual email transmission.
    """
    def __init__(self, email_tasks_instance):
        if not isinstance(email_tasks_instance, EmailTasks):
            raise TypeError("SMSTasks requires an instance of EmailTasks.")
        self.email_tasks = email_tasks_instance

        # Common US carrier email-to-SMS gateways (add more as needed)
        self.carrier_gateways = {
            "att": "@txt.att.net",
            "verizon": "@vtext.com",
            "tmobile": "@tmomail.net",
            "sprint": "@messaging.sprintpcs.com",
            "boost": "@sms.boostmobile.com",
            "cricket": "@mms.cricketwireless.net",
            "us_cellular": "@email.uscc.net",
        }
        logger.info("SMSTasks initialized.")

    def _gateway_address(self, phone_number, carrier_name):
        """Builds the email address of the SMS gateway for one phone number."""
        if '@' in phone_number:  # Already a full gateway address
            return phone_number
        if carrier_name and carrier_name.lower() in self.carrier_gateways:
            return f"{phone_number}{self.carrier_gateways[carrier_name.lower()]}"
        return None

    def send_sms(self, phone_numbers, message, carrier_name=None):
        """
        Sends SMS messages via email-to-SMS gateway for multiple recipients.
        :param phone_numbers: List of recipient phone numbers (e.g., ['1234567890']).
        :param message: The text message content.
        :param carrier_name: Optional carrier (e.g., 'att', 'verizon'). Not needed if the number is a full gateway address.
        :return: True if every message was sent, False otherwise.
        """
        if not phone_numbers:
            logger.warning("No phone numbers given. No SMS sent.")
            return False

        success_count = 0
        for phone_number in phone_numbers:
            gateway_address = self._gateway_address(phone_number, carrier_name)
            if gateway_address is None:
                logger.warning(f"Unknown carrier '{carrier_name}' for {phone_number} and it's not a gateway address. Cannot send SMS.")
                continue
            logger.info(f"Sending SMS to {phone_number} via gateway: {gateway_address}")
            # SMS emails usually don't show the subject, so it is left empty
            if self.email_tasks.send_email(recipients={'to': [gateway_address]}, subject="", body=message):
                success_count += 1

        logger.info(f"Attempted to send {len(phone_numbers)} SMS messages, {success_count} succeeded (email-wise).")
        return success_count == len(phone_numbers)
