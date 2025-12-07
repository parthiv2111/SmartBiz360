"""
Email service for sending OTP and notifications
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.sender_email = os.getenv('SENDER_EMAIL', '')
        self.sender_password = os.getenv('SENDER_PASSWORD', '')
        self.sender_name = os.getenv('SENDER_NAME', 'SmartBiz360')
        
    def send_otp_email(self, to_email: str, otp_code: str, user_name: str = None) -> bool:
        """
        Send OTP email for password reset
        """
        try:
            subject = "Password Reset OTP - SmartBiz360"
            
            # Create HTML email template
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Password Reset OTP</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 30px;
                        text-align: center;
                        border-radius: 10px 10px 0 0;
                    }}
                    .content {{
                        background: #f9f9f9;
                        padding: 30px;
                        border-radius: 0 0 10px 10px;
                    }}
                    .otp-box {{
                        background: #fff;
                        border: 2px dashed #667eea;
                        padding: 20px;
                        text-align: center;
                        margin: 20px 0;
                        border-radius: 8px;
                    }}
                    .otp-code {{
                        font-size: 32px;
                        font-weight: bold;
                        color: #667eea;
                        letter-spacing: 5px;
                        margin: 10px 0;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        color: #666;
                        font-size: 14px;
                    }}
                    .warning {{
                        background: #fff3cd;
                        border: 1px solid #ffeaa7;
                        color: #856404;
                        padding: 15px;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🔐 Password Reset</h1>
                    <p>SmartBiz360 Account Security</p>
                </div>
                
                <div class="content">
                    <h2>Hello {user_name or 'User'}!</h2>
                    
                    <p>You have requested to reset your password for your SmartBiz360 account. Please use the OTP code below to verify your identity and set a new password.</p>
                    
                    <div class="otp-box">
                        <p><strong>Your OTP Code:</strong></p>
                        <div class="otp-code">{otp_code}</div>
                        <p><small>This code will expire in 10 minutes</small></p>
                    </div>
                    
                    <div class="warning">
                        <strong>⚠️ Security Notice:</strong>
                        <ul>
                            <li>This OTP is valid for 10 minutes only</li>
                            <li>Do not share this code with anyone</li>
                            <li>If you didn't request this reset, please ignore this email</li>
                        </ul>
                    </div>
                    
                    <p>If you have any questions or need assistance, please contact our support team.</p>
                    
                    <p>Best regards,<br>
                    <strong>SmartBiz360 Team</strong></p>
                </div>
                
                <div class="footer">
                    <p>This is an automated message. Please do not reply to this email.</p>
                    <p>&copy; 2024 SmartBiz360. All rights reserved.</p>
                </div>
            </body>
            </html>
            """
            
            # Create plain text version
            text_content = f"""
            Password Reset OTP - SmartBiz360
            
            Hello {user_name or 'User'}!
            
            You have requested to reset your password for your SmartBiz360 account.
            
            Your OTP Code: {otp_code}
            This code will expire in 10 minutes.
            
            Security Notice:
            - This OTP is valid for 10 minutes only
            - Do not share this code with anyone
            - If you didn't request this reset, please ignore this email
            
            If you have any questions, please contact our support team.
            
            Best regards,
            SmartBiz360 Team
            
            This is an automated message. Please do not reply to this email.
            """
            
            return self._send_email(to_email, subject, text_content, html_content)
            
        except Exception as e:
            logger.error(f"Failed to send OTP email to {to_email}: {str(e)}")
            return False
    
    def send_password_reset_success_email(self, to_email: str, user_name: str = None) -> bool:
        """
        Send confirmation email after successful password reset
        """
        try:
            subject = "Password Reset Successful - SmartBiz360"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Password Reset Successful</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                        color: white;
                        padding: 30px;
                        text-align: center;
                        border-radius: 10px 10px 0 0;
                    }}
                    .content {{
                        background: #f9f9f9;
                        padding: 30px;
                        border-radius: 0 0 10px 10px;
                    }}
                    .success-box {{
                        background: #d4edda;
                        border: 1px solid #c3e6cb;
                        color: #155724;
                        padding: 20px;
                        border-radius: 8px;
                        text-align: center;
                        margin: 20px 0;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        color: #666;
                        font-size: 14px;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>✅ Password Reset Successful</h1>
                    <p>SmartBiz360 Account Security</p>
                </div>
                
                <div class="content">
                    <h2>Hello {user_name or 'User'}!</h2>
                    
                    <div class="success-box">
                        <h3>🎉 Your password has been successfully reset!</h3>
                        <p>You can now log in to your SmartBiz360 account with your new password.</p>
                    </div>
                    
                    <p>If you have any questions or need assistance, please contact our support team.</p>
                    
                    <p>Best regards,<br>
                    <strong>SmartBiz360 Team</strong></p>
                </div>
                
                <div class="footer">
                    <p>This is an automated message. Please do not reply to this email.</p>
                    <p>&copy; 2024 SmartBiz360. All rights reserved.</p>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            Password Reset Successful - SmartBiz360
            
            Hello {user_name or 'User'}!
            
            Your password has been successfully reset!
            You can now log in to your SmartBiz360 account with your new password.
            
            If you have any questions, please contact our support team.
            
            Best regards,
            SmartBiz360 Team
            """
            
            return self._send_email(to_email, subject, text_content, html_content)
            
        except Exception as e:
            logger.error(f"Failed to send success email to {to_email}: {str(e)}")
            return False
    
    def _send_email(self, to_email: str, subject: str, text_content: str, html_content: str = None) -> bool:
        """
        Send email using SMTP
        """
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.sender_name} <{self.sender_email}>"
            message["To"] = to_email
            
            # Add text content
            text_part = MIMEText(text_content, "plain")
            message.attach(text_part)
            
            # Add HTML content if provided
            if html_content:
                html_part = MIMEText(html_content, "html")
                message.attach(html_part)
            
            # Create secure connection and send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, to_email, message.as_string())
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

# Global email service instance
email_service = EmailService()
