from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = '05f3477f588134db3e689a77dc84cdfe'  # Set your secret key here
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    file_path = db.Column(db.String(200), nullable=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(200), nullable=False)

# Routes
@app.route('/')
def index():
    # Replace with actual logic to get the logged-in user's username
    username = "User"  # This should be replaced with the actual user's username if logged in

    # Example data fetching
    uploads = Content.query.all()  # Fetch all uploads
    uploads_list = [upload.file_path for upload in uploads]

    comments = Comment.query.all()  # Fetch all comments
    comments_list = [{'username': comment.username, 'content': comment.content} for comment in comments]

    return render_template('index.html', username=username, uploads=uploads_list, comments=comments_list)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))
        
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        try:
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('index'))  # Redirect to home page after registration
        except IntegrityError:
            db.session.rollback()  # Rollback the session on error
            flash('An error occurred. Please try again.', 'danger')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login failed. Check your username and/or password.', 'danger')
    return render_template('login.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)