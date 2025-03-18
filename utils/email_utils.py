from flask_mail import Message
from flask import current_app
from extensions import mail
import logging
from typing import List, Optional, Dict

class EmailUtils:
    """
    Comprehensive Email Utility Class
    """
    
    @classmethod
    def send_email(
        cls, 
        subject: str, 
        recipients: List[str], 
        body: str = None, 
        html: str = None,
        attachments: Optional[List[Dict[str, str]]] = None
    ):
        """
        Send email with flexible configuration
        
        :param subject: Email subject
        :param recipients: List of recipient email addresses
        :param body: Plain text email body
        :param html: HTML email body
        :param attachments: List of file attachments
        """
        try:
            msg = Message(
                subject, 
                recipients=recipients,
                body=body,
                html=html
            )
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    with current_app.open_resource(attachment['path']) as file:
                        msg.attach(
                            attachment['filename'], 
                            attachment['mimetype'], 
                            file.read()
                        )
            
            # Send email
            mail.send(msg)
            
            current_app.logger.info(f"Email sent to {', '.join(recipients)}")
        
        except Exception as e:
            current_app.logger.error(f"Email sending failed: {str(e)}")
            logging.error(f"Email Error: {str(e)}")