from flask import Flask
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Email configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

mail = Mail(app)

with app.app_context():
    try:
        msg = Message(
            subject='Test Email',
            sender=app.config['MAIL_USERNAME'],
            recipients=[os.getenv('RECIPIENT_EMAIL')],
            body='This is a test email to verify your email configuration.'
        )
        mail.send(msg)
        print("Test email sent successfully!")
    except Exception as e:
        print(f"Error sending test email: {str(e)}")
