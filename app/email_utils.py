from flask import render_template
import requests
from app.config import Config

def generate_invoice_html(label, amount, confirmation_url):
    return render_template(
        'emails/invoice_email.html', 
        label=label, 
        amount=amount, 
        confirmation_url=confirmation_url,
        logo_url=Config.LOGO_URL
    )

def generate_payment_confirmation_html(first_name, amount, title):
    return render_template(
        'emails/payment_confirmation.html', 
        first_name=first_name, 
        amount=amount, 
        title=title,
        logo_url=Config.LOGO_URL
    )

def send_invoice_email_via_resend(to_email, subject, html_content):
    headers = {
        'Authorization': f'Bearer {Config.RESEND_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        'from': 'invoice@pawportal.io',
        'to': [to_email],
        'subject': subject,
        'html': html_content
    }
    response = requests.post('https://api.resend.com/emails', json=payload, headers=headers)
    
    if response.status_code != 200:
        print(f'Failed to send email: {response.text}')
    return response.status_code == 200

def send_payment_confirmation_email(to_email, first_name, amount, title):
    subject = f"Payment Confirmation for {title}"
    
    html_content = generate_payment_confirmation_html(first_name, amount, title)

    return send_invoice_email_via_resend(to_email, subject, html_content)
