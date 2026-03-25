import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import (
    SMTP_SERVER,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASSWORD,
    APP_NAME,
    FRONTEND_URL,
)

class EmailService:
    """Service for sending emails via SMTP."""
    
    @staticmethod
    def send_password_reset_email(email: str, reset_token: str) -> bool:
        """Send password reset email."""
        reset_link = f"{FRONTEND_URL}/reset-password?token={reset_token}"
        
        subject = f"{APP_NAME} - Password Reset Request"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <h2>Password Reset Request</h2>
                <p>You requested a password reset for your {APP_NAME} account.</p>
                <p>Click the link below to reset your password (valid for 24 hours):</p>
                <a href="{reset_link}" style="background-color: #FF6B6B; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    Reset Password
                </a>
                <p>Or copy this link: <code>{reset_link}</code></p>
                <p><strong>If you didn't request this, please ignore this email.</strong></p>
                <hr>
                <small>This is an automated message, please do not reply to this email.</small>
            </body>
        </html>
        """
        
        return EmailService._send_email(email, subject, html_content)
    
    @staticmethod
    def send_verification_email(email: str, verification_token: str) -> bool:
        """Send email verification email."""
        verify_link = f"{FRONTEND_URL}/verify-email?token={verification_token}"
        
        subject = f"{APP_NAME} - Verify Your Email"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <h2>Welcome to {APP_NAME}!</h2>
                <p>Please verify your email address to complete your registration.</p>
                <a href="{verify_link}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    Verify Email
                </a>
                <p>Or copy this link: <code>{verify_link}</code></p>
                <p>This link expires in 24 hours.</p>
                <hr>
                <small>This is an automated message, please do not reply to this email.</small>
            </body>
        </html>
        """
        
        return EmailService._send_email(email, subject, html_content)
    
    @staticmethod
    def _send_email(to_email: str, subject: str, html_content: str) -> bool:
        """Internal method to send email."""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = SMTP_USER
            msg["To"] = to_email
            
            part = MIMEText(html_content, "html")
            msg.attach(part)
            
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(SMTP_USER, to_email, msg.as_string())
            
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False