"""
BinkRead - AI-powered PDF summarization application
A Flask web application that uses BART model to summarize PDF documents.
"""

import os
import logging
from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
from config import config
from pdf_processor import PDFProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Load configuration
config_name = os.environ.get('FLASK_ENV', 'default')
app.config.from_object(config[config_name])

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize PDF processor
pdf_processor = None


def init_processor():
    """Initialize the PDF processor."""
    global pdf_processor
    try:
        pdf_processor = PDFProcessor()
        logger.info("PDF processor initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing PDF processor: {e}")
        raise


def allowed_file(filename: str) -> bool:
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def home():
    """Home page with file upload form."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_pdf():
    """Handle PDF upload and summarization."""
    try:
        if 'uploaded_file' not in request.files:
            flash('No file selected', 'error')
            return redirect(url_for('home'))
        
        file = request.files['uploaded_file']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('home'))
        
        if not allowed_file(file.filename):
            flash('Invalid file type. Please upload a PDF file.', 'error')
            return redirect(url_for('home'))
        
        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > app.config['MAX_CONTENT_LENGTH']:
            flash('File too large. Maximum size is 16MB.', 'error')
            return redirect(url_for('home'))
        
        if file_size == 0:
            flash('Empty file uploaded', 'error')
            return redirect(url_for('home'))
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            # Process PDF
            summary = pdf_processor.process_pdf(file_path)
            return render_template('index.html', summary=summary)
            
        finally:
            # Clean up temporary file
            if os.path.exists(file_path):
                os.remove(file_path)
    
    except Exception as e:
        logger.error(f"Error processing upload: {e}")
        flash('An error occurred while processing the file', 'error')
        return redirect(url_for('home'))


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    flash('File too large. Maximum size is 16MB.', 'error')
    return redirect(url_for('home'))


@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors."""
    logger.error(f"Internal server error: {e}")
    flash('An internal error occurred. Please try again.', 'error')
    return redirect(url_for('home'))


if __name__ == '__main__':
    # Initialize processor on startup
    init_processor()
    
    # Run the application
    app.run(
        debug=app.config['DEBUG'],
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000))
    )