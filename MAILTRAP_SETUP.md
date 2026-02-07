# Mailtrap Email Configuration Guide

This guide explains how to configure Mailtrap for email testing in your Job Board Platform.

## What is Mailtrap?

Mailtrap is an email testing service that catches all emails sent from your application in a safe testing environment. Perfect for development and testing without sending real emails.

## Step-by-Step Setup

### 1. Create Mailtrap Account

1. Go to [https://mailtrap.io](https://mailtrap.io)
2. Click **Sign Up** (or **Sign In** if you already have an account)
3. You can use the free plan for development/testing

### 2. Create an Inbox

1. After logging in, you'll see your dashboard
2. Click **Add Inbox** or select an existing inbox
3. Give it a name (e.g., "Job Board Development")
4. Click **Create Inbox**

### 3. Get SMTP Credentials

1. Click on your inbox to open it
2. Go to the **SMTP Settings** tab
3. You'll see different integration options
4. Select **Django** from the integrations list
5. You'll see your credentials displayed:
   - **Host**: `smtp.mailtrap.io`
   - **Port**: `2525` (or `587` for TLS)
   - **Username**: Your Mailtrap username (shown in the settings)
   - **Password**: Your Mailtrap password (shown in the settings)

### 4. Alternative: Manual SMTP Settings

If you prefer to get credentials manually:

1. In your inbox, go to **SMTP Settings** tab
2. Under **SMTP Credentials**, you'll see:
   - **Host**: `smtp.mailtrap.io`
   - **Port**: `2525` (or `587`)
   - **Username**: A long string (your Mailtrap username)
   - **Password**: A long string (your Mailtrap password)

### 5. Update Your .env File

Add these values to your `.env` file:

```env
# Email Configuration (Mailtrap)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.mailtrap.io
EMAIL_PORT=2525
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=your-mailtrap-username-here
EMAIL_HOST_PASSWORD=your-mailtrap-password-here
DEFAULT_FROM_EMAIL=noreply@jobboard.local
```

### Example Configuration

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.mailtrap.io
EMAIL_PORT=2525
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=a1b2c3d4e5f6g7h8
EMAIL_HOST_PASSWORD=1a2b3c4d5e6f7g8h9
DEFAULT_FROM_EMAIL=noreply@jobboard.local
```

## Port Options

Mailtrap supports two ports:

### Port 2525 (Recommended for Development)
- **TLS**: Optional (can use `EMAIL_USE_TLS=True` or `False`)
- **SSL**: Not used
- **Settings**:
  ```env
  EMAIL_PORT=2525
  EMAIL_USE_TLS=True
  EMAIL_USE_SSL=False
  ```

### Port 587 (Alternative)
- **TLS**: Required
- **SSL**: Not used
- **Settings**:
  ```env
  EMAIL_PORT=587
  EMAIL_USE_TLS=True
  EMAIL_USE_SSL=False
  ```

## Testing Email Sending

### 1. Send a Test Email

After configuring, test by:

1. Start your Django application
2. Trigger an email (e.g., user registration, password reset)
3. Go to your Mailtrap inbox
4. You should see the email appear in the inbox

### 2. View Email Details

In Mailtrap inbox, you can:
- View email content (HTML and plain text)
- Check email headers
- See email source
- Test email rendering
- Check spam score

## Quick Reference

| Setting | Value | Description |
|---------|-------|-------------|
| `EMAIL_HOST` | `smtp.mailtrap.io` | Mailtrap SMTP server |
| `EMAIL_PORT` | `2525` or `587` | SMTP port |
| `EMAIL_USE_TLS` | `True` | Enable TLS encryption |
| `EMAIL_USE_SSL` | `False` | SSL not used with Mailtrap |
| `EMAIL_HOST_USER` | Your Mailtrap username | From SMTP Settings |
| `EMAIL_HOST_PASSWORD` | Your Mailtrap password | From SMTP Settings |

## Production Considerations

⚠️ **Important**: Mailtrap is for **development and testing only**. 

For production, you should use:
- **Real SMTP server** (Gmail, SendGrid, Mailgun, AWS SES, etc.)
- Update your `.env` with production email credentials
- Or use environment-specific settings

### Example Production Configuration (Gmail)

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

### Example Production Configuration (SendGrid)

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

## Troubleshooting

### "Authentication failed" error
- Double-check your username and password
- Make sure you copied the entire credentials (they're long strings)
- Verify you're using the correct inbox credentials

### "Connection timeout" error
- Check your internet connection
- Verify firewall isn't blocking port 2525 or 587
- Try switching between ports 2525 and 587

### Emails not appearing in Mailtrap
- Verify your `.env` file is loaded correctly
- Check Django logs for email sending errors
- Make sure `EMAIL_BACKEND` is set to SMTP backend
- Verify you're looking at the correct Mailtrap inbox

### "SSL/TLS error"
- For port 2525: Set `EMAIL_USE_TLS=True` and `EMAIL_USE_SSL=False`
- For port 587: Set `EMAIL_USE_TLS=True` and `EMAIL_USE_SSL=False`
- Never use `EMAIL_USE_SSL=True` with Mailtrap

## Mailtrap Features

- **Email Testing**: Catch all emails without sending real ones
- **Email Preview**: See how emails render in different clients
- **Spam Analysis**: Check spam score of your emails
- **HTML/Text View**: View both HTML and plain text versions
- **Email Forwarding**: Forward emails to real addresses for testing
- **Team Collaboration**: Share inboxes with team members

## Additional Resources

- [Mailtrap Documentation](https://mailtrap.io/docs/)
- [Django Email Backend Documentation](https://docs.djangoproject.com/en/stable/topics/email/)
- [Mailtrap SMTP Settings](https://mailtrap.io/docs/smtp/)

## Security Notes

1. **Never commit your `.env` file** with Mailtrap credentials
2. Mailtrap credentials are safe to use in development
3. For production, use proper email service credentials
4. Rotate credentials if accidentally exposed

---

**Happy Testing! 📧**
