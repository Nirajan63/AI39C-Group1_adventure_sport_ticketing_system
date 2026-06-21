import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import current_app

def send_email(to_email, subject, html_content, text_content=None):
    """
    Sends an email to the specified recipient.
    If SMTP credentials are not configured, it will print the email contents to the console as a fallback.
    """
    smtp_server = current_app.config.get('SMTP_SERVER')
    smtp_port = current_app.config.get('SMTP_PORT', 587)
    smtp_username = current_app.config.get('SMTP_USERNAME')
    smtp_password = current_app.config.get('SMTP_PASSWORD')
    smtp_sender = current_app.config.get('SMTP_SENDER')

    
    is_placeholder = (
        not smtp_username or 
        not smtp_password or 
        'your-email' in smtp_username or 
        'your-16-digit' in smtp_password
    )

    
    if is_placeholder:
        print("\n=== [SIMULATED EMAIL LOG (DEVELOPMENT MODE)] ===", flush=True)
        print(f"To: {to_email}", flush=True)
        print(f"From: {smtp_sender}", flush=True)
        print(f"Subject: {subject}", flush=True)
        print(f"Text Content: {text_content or html_content}", flush=True)
        print("================================================\n", flush=True)
        return True

    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = smtp_sender
    msg['To'] = to_email

    if text_content:
        msg.attach(MIMEText(text_content, 'plain'))
    msg.attach(MIMEText(html_content, 'html'))

    try:
        
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=10)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
            server.starttls()
        
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_sender, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email via SMTP: {e}", flush=True)
        
        print("\n=== [FALLBACK EMAIL LOG DUE TO SMTP ERROR] ===", flush=True)
        print(f"To: {to_email}", flush=True)
        print(f"From: {smtp_sender}", flush=True)
        print(f"Subject: {subject}", flush=True)
        print(f"Text Content: {text_content or html_content}", flush=True)
        print("==============================================\n", flush=True)
        
       
        return True
