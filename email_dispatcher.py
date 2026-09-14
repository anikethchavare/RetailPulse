# RetailPulse (Enterprise Sales Data Analyzer) - email_dispatcher.py

# Imports
import os
import smtplib
from dotenv import load_dotenv
from typing import Tuple, Optional
from email.utils import formataddr
from email.message import EmailMessage

# Loading the Environment Variables
load_dotenv()

# Class 1: EmailDispatcher
class EmailDispatcher:
    """ Handles automated SMTP email alerts and executive report delivery. """
    
    # Constructor: __init__
    def __init__(self) -> None:
        # Load Environment Variables
        self.sender_email = os.getenv("GOOGLE_EMAIL_ADDRESS")
        self.app_password = os.getenv("GOOGLE_APP_PASSWORD")
    
    # Method 1: is_configured
    def is_configured(self) -> bool:
        """ Check if sender email credentials are set. """
        
        return bool(self.sender_email.strip() and self.app_password.strip())

    # Method 2: update_credentials
    def update_credentials(self, sender_email: str, app_password: str) -> None:
        """ Update runtime email credentials from GUI settings. """
        
        self.sender_email = sender_email.strip()
        self.app_password = app_password.strip()
    
    # Method 3: send_report
    def send_report(
        self,
        receiver_email: str,
        subject: str,
        text_body: str,
        html_body: Optional[str] = None
    ) -> Tuple[bool, str]:
        """ Send an analytical summary or alert to an executive/auditor inbox. """
        
        if not self.is_configured():
            return False, "SMTP credentials not configured. Please set email and app password."

        if not receiver_email or "@" not in receiver_email:
            return False, "Invalid receiver email address."

        msg = EmailMessage()
        msg["From"] = formataddr(("RetailPulse Alerts", self.sender_email))
        msg["To"] = receiver_email.strip()
        msg["Subject"] = subject
        msg.set_content(text_body)

        if html_body:
            msg.add_alternative(html_body, subtype="html")

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(self.sender_email, self.app_password)
                server.send_message(msg)
                
            return True, f"Email dispatched successfully to {receiver_email}."

        except smtplib.SMTPAuthenticationError:
            return False, "Authentication Failed: Please verify Gmail app password."
        except smtplib.SMTPException as error:
            return False, f"SMTP Protocol Error: {str(error)}"
        except Exception as error:
            return False, f"Unexpected Error During Dispatch: {str(error)}"
    
    # Method 3: dispatch_security_alert
    def dispatch_security_alert(self, event_type: str, details: str, admin_email: str) -> Tuple[bool, str]:
        """ Send automated high-priority alert regarding security or analytical anomalies. """
        
        subject = f"[RetailPulse Alert] Security Notice: {event_type}"
        
        body = (
            f"RetailPulse Security & Audit Engine Alert\n"
            f"=========================================\n"
            f"Event Type: {event_type}\n"
            f"Description: {details}\n\n"
            f"Please inspect the tamper-evident audit ledger inside RetailPulse.\n"
        )
        
        return self.send_report(admin_email, subject, body)