from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a real secret key

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# In-memory storage for simplicity (replace with a database in production)
requests_data = {}

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', user=session['user'], requests=requests_data)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/sso', methods=['POST'])
def sso():
    # Simulate SSO authentication
    session['user'] = {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'avatar': 'https://api.dicebear.com/6.x/initials/svg?seed=JD'
    }
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = secure_filename(file.filename)
        doc_uuid = str(uuid.uuid4())
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        requests_data[doc_uuid] = {
            'filename': filename,
            'status': 'Uploaded',
            'file_path': file_path,
            'upload_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'doc_uuid': doc_uuid
        }
        return jsonify({'doc_uuid': doc_uuid, 'message': 'File uploaded successfully'}), 200

@app.route('/process', methods=['POST'])
def process():
    doc_uuid = request.form.get('doc_uuid')
    process_type = request.form.get('process_type')
    openai_model = request.form.get('openai_model')
    document_type = request.form.get('document_type')

    if doc_uuid not in requests_data:
        return jsonify({'error': 'Invalid document UUID'}), 400
    if process_type not in ['classify', 'extract']:
        return jsonify({'error': 'Invalid process type'}), 400

    # Simulate processing
    requests_data[doc_uuid]['status'] = f'{process_type.capitalize()}ing'
    requests_data[doc_uuid]['openai_model'] = openai_model
    if process_type == 'extract':
        requests_data[doc_uuid]['document_type'] = document_type

    return jsonify({'message': f'Document {process_type} started successfully'}), 200

@app.route('/email', methods=['POST'])
def email():
    doc_uuid = request.form.get('doc_uuid')
    email_addresses = request.form.get('email_addresses')
    process_name = request.form.get('process_name')

    if doc_uuid not in requests_data:
        return jsonify({'error': 'Invalid document UUID'}), 400
    if not email_addresses:
        return jsonify({'error': 'Email addresses are required'}), 400
    if process_name not in ['classification', 'extraction']:
        return jsonify({'error': 'Invalid process name'}), 400

    # Simulate sending email
    requests_data[doc_uuid]['status'] = 'Completed'
    requests_data[doc_uuid]['email_addresses'] = email_addresses
    requests_data[doc_uuid]['process_name'] = process_name

    return jsonify({'message': f'Results sent to {email_addresses}'}), 200

@app.route('/status/<doc_uuid>')
def status(doc_uuid):
    if doc_uuid not in requests_data:
        return jsonify({'error': 'Invalid document UUID'}), 400
    return jsonify({'status': requests_data[doc_uuid]['status']})

@app.route('/download/<doc_uuid>')
def download(doc_uuid):
    if doc_uuid not in requests_data:
        return jsonify({'error': 'Invalid document UUID'}), 400
    # In a real application, you would generate the result file here
    # For this example, we'll just return a dummy file
    dummy_file = os.path.join(app.config['UPLOAD_FOLDER'], 'dummy_results.xlsx')
    with open(dummy_file, 'w') as f:
        f.write('Dummy results')
    return send_file(dummy_file, as_attachment=True, attachment_filename='results.xlsx')

if __name__ == '__main__':
    app.run(debug=True)