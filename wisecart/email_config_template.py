# Email Configuration Template
# Copy the configuration you want to use and paste it into wisecart/settings.py
# Replace the placeholder values with your actual email credentials

# ============================================================================
# OPTION 1: Gmail SMTP (Most Popular for Development)
# ============================================================================
# Uncomment and configure these lines in settings.py:
"""
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'  # Replace with your Gmail address
EMAIL_HOST_PASSWORD = 'your-app-password'  # Replace with your Gmail app password
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'  # Replace with your Gmail address
"""

# ============================================================================
# OPTION 2: Outlook/Hotmail SMTP
# ============================================================================
"""
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp-mail.outlook.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@outlook.com'  # Replace with your Outlook address
EMAIL_HOST_PASSWORD = 'your-password'  # Replace with your Outlook password
DEFAULT_FROM_EMAIL = 'your-email@outlook.com'  # Replace with your Outlook address
"""

# ============================================================================
# OPTION 3: Yahoo SMTP
# ============================================================================
"""
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mail.yahoo.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@yahoo.com'  # Replace with your Yahoo address
EMAIL_HOST_PASSWORD = 'your-app-password'  # Replace with your Yahoo app password
DEFAULT_FROM_EMAIL = 'your-email@yahoo.com'  # Replace with your Yahoo address
"""

# ============================================================================
# OPTION 4: SendGrid (Recommended for Production)
# ============================================================================
"""
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'  # This should always be 'apikey'
EMAIL_HOST_PASSWORD = 'your-sendgrid-api-key'  # Replace with your SendGrid API key
DEFAULT_FROM_EMAIL = 'noreply@yourdomain.com'  # Replace with your verified sender
"""

# ============================================================================
# OPTION 5: Mailgun (Recommended for Production)
# ============================================================================
"""
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-mailgun-username'  # Replace with your Mailgun username
EMAIL_HOST_PASSWORD = 'your-mailgun-password'  # Replace with your Mailgun password
DEFAULT_FROM_EMAIL = 'noreply@yourdomain.com'  # Replace with your verified sender
"""

# ============================================================================
# IMPORTANT NOTES:
# ============================================================================

# For Gmail:
# 1. Enable 2-factor authentication on your Google account
# 2. Generate an "App Password" from Google Account settings
# 3. Use the app password instead of your regular password
# 4. The app password is 16 characters long

# For Outlook/Hotmail:
# 1. You may need to enable "Less secure app access" or use an app password
# 2. Some accounts require enabling SMTP access in account settings

# For Yahoo:
# 1. Enable 2-factor authentication
# 2. Generate an app-specific password
# 3. Use the app password instead of your regular password

# For SendGrid/Mailgun:
# 1. Sign up for a free account
# 2. Verify your sender email address
# 3. Get your API credentials from the dashboard
# 4. These services are more reliable for production use

# ============================================================================
# TESTING YOUR EMAIL CONFIGURATION:
# ============================================================================

# After configuring your email settings, you can test them by:
# 1. Running the Django server
# 2. Going to the password reset page
# 3. Entering an email address
# 4. Checking if the email is sent successfully

# If you want to test without changing the main settings, you can temporarily
# modify the settings.py file and then test the password reset functionality. 