# Email Configuration Setup

This guide explains how to configure email settings for the forgot password functionality.

## Gmail Setup (Recommended)

### 1. Enable 2-Factor Authentication
1. Go to your Google Account settings
2. Navigate to Security
3. Enable 2-Factor Authentication

### 2. Generate App Password
1. Go to Google Account settings
2. Navigate to Security > 2-Step Verification
3. Scroll down to "App passwords"
4. Generate a new app password for "Mail"
5. Copy the generated password (16 characters)

### 3. Environment Variables
Create a `.env` file in the backend directory with the following variables:

```env
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-16-character-app-password
SENDER_NAME=SmartBiz360
```

## Other Email Providers

### Outlook/Hotmail
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SENDER_EMAIL=your-email@outlook.com
SENDER_PASSWORD=your-password
SENDER_NAME=SmartBiz360
```

### Yahoo
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SENDER_EMAIL=your-email@yahoo.com
SENDER_PASSWORD=your-app-password
SENDER_NAME=SmartBiz360
```

### Custom SMTP Server
```env
SMTP_SERVER=your-smtp-server.com
SMTP_PORT=587
SENDER_EMAIL=your-email@yourdomain.com
SENDER_PASSWORD=your-password
SENDER_NAME=SmartBiz360
```

## Testing Email Configuration

You can test the email configuration by running the backend server and checking the logs for any SMTP connection errors.

## Security Notes

1. **Never commit your `.env` file to version control**
2. **Use app passwords instead of your main account password**
3. **Enable 2FA on your email account**
4. **Consider using a dedicated email account for your application**

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Check if 2FA is enabled
   - Verify the app password is correct
   - Ensure "Less secure app access" is disabled (use app passwords instead)

2. **Connection Timeout**
   - Check firewall settings
   - Verify SMTP server and port
   - Try different ports (465 for SSL, 587 for TLS)

3. **Email Not Received**
   - Check spam folder
   - Verify sender email address
   - Check email server logs

### Testing Commands

```python
# Test email configuration
from services.email_service import email_service

# Test OTP email
success = email_service.send_otp_email(
    to_email="test@example.com",
    otp_code="123456",
    user_name="Test User"
)

print(f"Email sent: {success}")
```

## Production Considerations

1. **Use a dedicated email service** (SendGrid, Mailgun, AWS SES)
2. **Implement rate limiting** for OTP requests
3. **Add email templates** for different languages
4. **Monitor email delivery rates**
5. **Set up email bounce handling**
