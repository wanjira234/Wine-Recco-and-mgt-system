import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

class EmailUtils:
    @staticmethod
    def send_email(to_email, subject, body, html=None):
        """
        Send email using SMTP
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = current_app.config.get('EMAIL_SENDER')
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))
            
            if html:
                msg.attach(MIMEText(html, 'html'))

            # Use app configuration for SMTP settings
            smtp_server = current_app.config.get('SMTP_SERVER')
            smtp_port = current_app.config.get('SMTP_PORT')
            smtp_username = current_app.config.get('SMTP_USERNAME')
            smtp_password = current_app.config.get('SMTP_PASSWORD')

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            current_app.logger.error(f"Email sending failed: {str(e)}")
            return False

    @staticmethod
    def send_welcome_email(user):
        """
        Send welcome email to new users
        """
        subject = "Welcome to Wine Recommender!"
        body = f"Hi {user.name},\n\nWelcome to Wine Recommender!"
        html = f"""
        <html>
            <body>
                <h1>Welcome, {user.name}!</h1>
                <p>Thank you for joining Wine Recommender</p>
            </body>
        </html>
        """
        return EmailUtils.send_email(user.email, subject, body, html)