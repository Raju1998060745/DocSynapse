from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from langchain.schema import AIMessage
import time
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import uuid
import datetime
import requests
import json
import logging
from logging.handlers import RotatingFileHandler

# Setup logging
def setup_logging(app):
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Set up file handler for logging
    file_handler = RotatingFileHandler('logs/chatbot.log', maxBytes=10485760, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    
    # Set up console handler for logging
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    
    # Configure app logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)
    
    # Log application startup
    app.logger.info('Chatbot application startup')

# App configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chatbot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # Go up one level
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'service_2', 'uploads')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Setup logging for the application
setup_logging(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
app.logger.info(f"Upload folder ensured at {app.config['UPLOAD_FOLDER']}")

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    messages = db.relationship('Message', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    sender = db.Column(db.String(10), nullable=False)  # 'user' or 'bot'
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    files = db.relationship('File', backref='message', lazy=True)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_id = db.Column(db.String(36), unique=True, nullable=False)  # UUID
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    app.logger.info('Home page accessed')
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        app.logger.info(f'Authenticated user {current_user.username} redirected from register to chat')
        return redirect(url_for('chat'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        app.logger.info(f'Registration attempt for username: {username}, email: {email}')
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            app.logger.warning(f'Registration failed: Username {username} already exists')
            flash('Username already exists.')
            return redirect(url_for('register'))
            
        if User.query.filter_by(email=email).first():
            app.logger.warning(f'Registration failed: Email {email} already registered')
            flash('Email already registered.')
            return redirect(url_for('register'))
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        
        # Commit to generate the user ID
        db.session.commit()
        
        # Now that we have a valid user ID, add the welcome message
        welcome_message = Message(
            text="Hello! How can I help you today?",
            sender="ai",
            user_id=user.id
        )
        db.session.add(welcome_message)
        db.session.commit()
        
        app.logger.info(f'New user registered: {username}, ID: {user.id}')
        
        # Log in the new user
        login_user(user)
        return redirect(url_for('chat'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        app.logger.info(f'Already authenticated user {current_user.username} redirected from login to chat')
        return redirect(url_for('chat'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        app.logger.info(f'Login attempt for username: {username}')
        
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            app.logger.warning(f'Login failed: Invalid credentials for username: {username}')
            flash('Invalid username or password')
            return redirect(url_for('login'))
            
        login_user(user)
        app.logger.info(f'User logged in: {username}, ID: {user.id}')
        
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('chat')
            
        return redirect(next_page)
        
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    app.logger.info(f'User logged out: {current_user.username}, ID: {current_user.id}')
    logout_user()
    return redirect(url_for('home'))

@app.route('/chat')
@login_required
def chat():
    app.logger.info(f'Chat page accessed by: {current_user.username}, ID: {current_user.id}')
    return render_template('chat.html')

@app.route('/api/messages', methods=['GET', 'POST'])
@login_required
def handle_messages():
    if request.method == 'GET':
        app.logger.info(f'Messages requested by user: {current_user.username}, ID: {current_user.id}')
        # Get all messages for the current user
        messages = Message.query.filter_by(user_id=current_user.id).order_by(Message.timestamp).all()
        
        # Convert to JSON-serializable format
        message_list = []
        for message in messages:
            files_data = []
            for file in message.files:
                files_data.append({
                    "id": file.file_id,
                    "name": file.filename
                })
                
            message_list.append({
                "id": message.id,
                "text": message.text,
                "sender": message.sender,
                "timestamp": message.timestamp.isoformat(),
                "files": files_data
            })
            
        app.logger.info(f'Returning {len(message_list)} messages to user: {current_user.username}')
        return jsonify(message_list)
        
    elif request.method == 'POST':
        data = request.json
        
        # Validate input
        if not data or 'message' not in data:
            app.logger.warning(f'Invalid message request from user: {current_user.username} - missing message field')
            return jsonify({"error": "Message is required"}), 400
        
        # Process the message
        message_text = data['message']
        file_ids = data.get('fileIds', [])
        
        app.logger.info(f'New message from user: {current_user.username}, message length: {len(message_text)}, files: {len(file_ids)}')
        
        # Add user message to database
        user_message = Message(
            text=message_text,
            sender="human",
            user_id=current_user.id
        )
        db.session.add(user_message)
        db.session.flush()  # Get the ID without committing
        
        # Associate files with the message
        for file_id in file_ids:
            file = File.query.filter_by(file_id=file_id, user_id=current_user.id).first()
            if file:
                file.message_id = user_message.id
                app.logger.info(f'File associated with message: file_id={file_id}, message_id={user_message.id}')
            else:
                app.logger.warning(f'Attempted to associate nonexistent file: file_id={file_id}')
        
        # Generate bot response
        app.logger.info(f'Generating bot response for message: {message_text[:50]}{"..." if len(message_text) > 50 else ""}')
        messagess = Message.query.filter_by(user_id=current_user.id).order_by(Message.timestamp).all()
        message_list = []
        for message in messagess:
            files_data = []
            for file in message.files:
                files_data.append({
                    "id": file.file_id,
                    "name": file.filename
                })
                
            message_list.append({
                "sender": message.sender,
                "text": message.text
                
            })
        formatted_messages = [{msg['sender']: msg['text']} for msg in message_list]
        #print(formatted_messages)
        bot_response_text = generate_response(current_user.username,message_text)
        print(bot_response_text)
        # if isinstance(bot_response_text, AIMessage):
        #     bot_response_text = bot_response_text.content  # Extract actual text

        bot_message= Message(
        text=bot_response_text,  # Now it's a plain string
        sender="ai",
        user_id=current_user.id
        )

        db.session.add(bot_message)
        db.session.commit()
        
        app.logger.info(f'Bot response generated, length: {len(bot_response_text)}')
        
        # Prepare response data
        bot_response = {
            "id": bot_message.id,
            "text": bot_message.text,
            "sender": "ai",
            "timestamp": bot_message.timestamp.isoformat(),
            "files": []
        }
        
        return jsonify(bot_response)

@app.route('/api/files/upload', methods=['POST'])
@login_required
def upload_files():
    uploaded_files = request.files.getlist('files')
    if not uploaded_files:
        app.logger.warning(f'File upload attempt with no files by user: {current_user.username}')
        return jsonify({"error": "No files provided"}), 400
    
    app.logger.info(f'File upload attempt by user: {current_user.username}, files: {len(uploaded_files)}')
    
    file_ids = []
    for file in uploaded_files:
        if file:
            filename = secure_filename(file.filename)
            file_id = str(uuid.uuid4())
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}")
            
            try:
                file.save(file_path)
                app.logger.info(f'File saved: {filename}, size: {os.path.getsize(file_path)}, path: {file_path}')
                
                # Save file reference to database
                file_record = File(
                    filename=filename,
                    file_id=file_id,
                    user_id=current_user.id,
                    message_id=0  # Will be updated when message is sent
                )

                file_list=[]
                filename_without_ext = filename.replace(".pdf", "")
                file_list.append(filename_without_ext)

                send={
                    "filename": file_list,
                    "user":current_user.username

                    }
                print(file_record.filename + " " + file_record.file_id + " " + str(file_record.user_id))
                print("Waiting for 10 seconds before sending...")
                time.sleep(10)
                print(send)
                response = requests.post("http://127.0.0.1:8000/api/files/upload", json=send)
                content = response.json() 
                print(content)
                db.session.add(file_record)
                file_ids.append(file_id)
                
            except Exception as e:
                app.logger.error(f'Error saving file {filename}: {str(e)}')
    
    db.session.commit()
    app.logger.info(f'File upload completed for user: {current_user.username}, files saved: {len(file_ids)}')
    return jsonify({"fileIds": file_ids})

def generate_response(user,message_text):
    send={
            "user": user,
            "query": message_text,
         }
    response = requests.post("http://127.0.0.1:8000/api/rag", json=send)
    content = response.json()  # Parse the JSON response
    response_text = content["results"]["content"]
    return response_text

@app.errorhandler(404)
def not_found_error(error):
    app.logger.warning(f'404 Error: {request.path} - IP: {request.remote_addr}')
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.error(f'500 Error: {str(error)} - IP: {request.remote_addr}')
    return render_template('500.html'), 500

# Create database tables
with app.app_context():
    try:
        db.create_all()
        app.logger.info('Database tables created successfully')
    except Exception as e:
        app.logger.error(f'Error creating database tables: {str(e)}')

if __name__ == '__main__':
    app.run(debug=True)