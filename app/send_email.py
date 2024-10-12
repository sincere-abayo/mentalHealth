import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(subject, body, to_email):
    # Email configuration
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "mhpcms2024@gmail.com"
    sender_password = "qrpe sixl znov dxgj"

    # Create the email message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = to_email
    message["Subject"] = subject

    # Add body to email as HTML
    message.attach(MIMEText(body, "html"))

    # Connect to the SMTP server and send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(message)

def send_test_email():
    subject = "Patient Payment Confirmation - MentalHealth Project"
    body = """
    <html>
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }
            .container {
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f4f4f4;
            }
            h1 {
                color: #0066cc;
            }
            p {
                margin-bottom: 15px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Patient Payment Confirmation</h1>
            <p>This is a confirmation email for your recent payment to the MentalHealth project.</p>
        </div>
    </body>
    </html>
    """
  
  
  
    to_email = "abayosincere11@gmail.com"    
    send_email(subject, body, to_email)
    print("Patient payment confirmation email sent successfully!")

if __name__ == "__main__":
    send_test_email()
