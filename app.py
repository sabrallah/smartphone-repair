from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Email configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

# Print configuration (without sensitive data)
logger.info(f"Mail Server: {app.config['MAIL_SERVER']}")
logger.info(f"Mail Port: {app.config['MAIL_PORT']}")
logger.info(f"Mail Use TLS: {app.config['MAIL_USE_TLS']}")
logger.info(f"Mail Username: {app.config['MAIL_USERNAME']}")

mail = Mail(app)

@app.route('/api/contact', methods=['POST'])
def contact():
    try:
        logger.info("Received contact form submission")
        data = request.json
        logger.debug(f"Form data received: {data}")
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'service', 'message']
        for field in required_fields:
            if not data.get(field):
                logger.error(f"Missing required field: {field}")
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Extract form data
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        device = data.get('device')
        service = data.get('service')
        message = data.get('message')
        
        # Create email content
        email_body = f"""
        New Contact Form Submission:
        
        Name: {name}
        Email: {email}
        Phone: {phone}
        Device: {device}
        Service: {service}
        Message: {message}
        """
        
        logger.info("Preparing to send email")
        
        # Send email
        msg = Message(
            subject='New Contact Form Submission',
            sender=app.config['MAIL_USERNAME'],
            recipients=[os.getenv('RECIPIENT_EMAIL')],
            body=email_body
        )
        
        mail.send(msg)
        logger.info("Email sent successfully")
        
        return jsonify({'message': 'Form submitted successfully!'}), 200
    
    except Exception as e:
        logger.error(f"Error processing form submission: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Flask application...")
    app.run(debug=True, port=5000)
