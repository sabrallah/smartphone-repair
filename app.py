from flask import Flask, request, jsonify, send_from_directory
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

# Verify required environment variables
required_env_vars = [
    'MAIL_SERVER',
    'MAIL_PORT',
    'MAIL_USE_TLS',
    'MAIL_USERNAME',
    'MAIL_PASSWORD',
    'RECIPIENT_EMAIL'
]

missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    raise RuntimeError(f"Missing required environment variables: {', '.join(missing_vars)}")

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://smartphone-repair.onrender.com"],
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Email configuration
app.config.update(
    MAIL_SERVER=os.getenv('MAIL_SERVER'),
    MAIL_PORT=int(os.getenv('MAIL_PORT', 587)),
    MAIL_USE_TLS=os.getenv('MAIL_USE_TLS', 'True').lower() == 'true',
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD')
)

# Initialize Flask-Mail
try:
    mail = Mail(app)
    logger.info("Flask-Mail initialized successfully")
except Exception as e:
    logger.error(f"Error initializing Flask-Mail: {str(e)}")
    raise

# Print configuration (without sensitive data)
logger.info("Mail Configuration:")
logger.info(f"Mail Server: {app.config['MAIL_SERVER']}")
logger.info(f"Mail Port: {app.config['MAIL_PORT']}")
logger.info(f"Mail Use TLS: {app.config['MAIL_USE_TLS']}")
logger.info(f"Mail Username: {app.config['MAIL_USERNAME']}")
logger.info(f"Recipient Email: {os.getenv('RECIPIENT_EMAIL')}")

# Serve static files
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/api/contact', methods=['POST'])
def contact():
    try:
        logger.info("Received contact form submission")
        
        if not request.is_json:
            logger.error("Request is not JSON")
            return jsonify({'error': 'Content-Type must be application/json'}), 400
            
        data = request.json
        logger.debug(f"Form data received: {data}")
        logger.debug(f"Request headers: {dict(request.headers)}")
        
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
        
        # Log email configuration
        logger.debug(f"Mail server: {app.config['MAIL_SERVER']}")
        logger.debug(f"Mail port: {app.config['MAIL_PORT']}")
        logger.debug(f"Mail username: {app.config['MAIL_USERNAME']}")
        logger.debug(f"Recipient email: {os.getenv('RECIPIENT_EMAIL')}")
        
        try:
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
            
        except Exception as email_error:
            logger.error(f"Error sending email: {str(email_error)}", exc_info=True)
            return jsonify({'error': f'Email sending failed: {str(email_error)}'}), 500
    
    except Exception as e:
        logger.error(f"Error processing form submission: {str(e)}", exc_info=True)
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    logger.info("Starting Flask application...")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
