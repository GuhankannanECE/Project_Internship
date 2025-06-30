import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# SMTP configuration
SMTP_HOST = "localhost"  # Use the actual SMTP host
SMTP_PORT = 1025  # Common SMTP port for TLS
SENDER_EMAIL = 'guhank@study.iitm.ac.in'
SENDER_PASSWORD = ''  # Replace with your actual password if required

def send_test_email(to_email, subject, html_content):
    try:
        # Create message
        msg = MIMEMultipart()
        msg["To"] = to_email
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        
        # Attach HTML content
        msg.attach(MIMEText(html_content, 'html'))
        
        # Connect and send
        with smtplib.SMTP(host=SMTP_HOST, port=SMTP_PORT) as client:
            client.send_message(msg)
        print("Email sent successfully!")
        
    except Exception as e:
        print(f"Failed to send email: {e}")