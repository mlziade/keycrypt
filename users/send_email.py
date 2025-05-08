import os
import uuid
from dotenv import load_dotenv
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def send_reset_password_email(reset_id: uuid, user_email: str, username: str):
    try:
        # Create the reset link using the reset_id
        reset_link = f"https://keycrypt.mlziade.com.br/users/change-password/{reset_id}/"
        
        # Email content
        subject = 'KeyCrypt - Password Reset Request'
        
        text_content = f"""
        Hello {username},
        
        You recently requested to reset your password for your KeyCrypt account.
        
        Please click the link below to set a new password:
        {reset_link}
        
        If you did not request a password reset, please ignore this email or contact support.
        
        This link will expire in 1 hour.
        
        Thank you,
        KeyCrypt Team
        """
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 10px;">KeyCrypt Password Reset</h2>
                <p>Hello {username},</p>
                <p>You recently requested to reset your password for your KeyCrypt account.</p>
                <div style="margin: 25px 0;">
                    <a href="{reset_link}" style="background-color: #3498db; color: white; padding: 12px 20px; text-decoration: none; border-radius: 4px; display: inline-block;">Reset Your Password</a>
                </div>
                <p style="margin-top: 25px;">If you did not request a password reset, please ignore this email or contact support.</p>
                <p><strong>This link will expire in 1 hour.</strong></p>
                <p style="margin-top: 30px; padding-top: 15px; border-top: 1px solid #eee; font-size: 12px; color: #777;">
                    Thank you,<br>
                    KeyCrypt Team
                </p>
            </div>
        </body>
        </html>
        """
        
        # Send the email to the actual user
        from_email = 'KeyCrypt <keycrypt@mlziade.com.br>'
        to = [user_email]
        
        email = EmailMultiAlternatives(subject, text_content, from_email, to)
        email.attach_alternative(html_content, "text/html")
        email.send()
    except Exception as e:
        logger.error(f"Failed to send reset password email to {user_email}: {e}")
        return HttpResponse("An error occurred while sending the email.", status=500)