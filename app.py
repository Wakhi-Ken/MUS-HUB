from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = '05f3477f588134db3e689a77dc84cdfe'  # Change this to a random secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mus_hub.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    UserID = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(80), nullable=False)
    Email = db.Column(db.String(120), unique=True, nullable=False)
    Password = db.Column(db.String(200), nullable=False)
    Role = db.Column(db.String(20), nullable=False)
    Bio = db.Column(db.String(500))

class Content(db.Model):
    ContentID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('user.UserID'), nullable=False)
    FilePath = db.Column(db.String(200), nullable=False)
    UploadDate = db.Column(db.DateTime, default=datetime.utcnow)

class Comment(db.Model):
    CommentID = db.Column(db.Integer, primary_key=True)
    ContentID = db.Column(db.Integer, db.ForeignKey('content.ContentID'), nullable=False)
    UserID = db.Column(db.Integer, db.ForeignKey('user.UserID'), nullable=False)
    CommentText = db.Column(db.Text, nullable=False)
    CommentDate = db.Column(db.DateTime, default=datetime.utcnow)

# Route to initialize the database
@app.route('/initdb')
def init_db():
    db.create_all()
    return "Database initialized!"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        # Create and save user to the database
        new_user = User(Username=username, Email=email, Password=password, Role=role)
        db.session.add(new_user)
        db.session.commit()
        
        session['user_id'] = new_user.UserID
        flash("Registration successful! Please complete your profile.")
        return redirect(url_for('profile'))
    
    return render_template('register.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('register'))
    
    user = User.query.get(user_id)
    if request.method == 'POST':
        user.Bio = request.form.get('bio', user.Bio)  # Update bio if provided
        db.session.commit()
    
    return render_template('profile.html', user=user)

@app.route('/')
def index():
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None
    username = user.Username if user else 'Guest'
    return render_template('index.html', username=username)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash("No selected file")
            return redirect(request.url)
        
        # Save file and record content in the database
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        user_id = session.get('user_id')
        new_content = Content(UserID=user_id, FilePath=file_path)
        db.session.add(new_content)
        db.session.commit()
        
        flash("File uploaded successfully!")
        return redirect(url_for('index'))
    
    user_id = session.get('user_id')
    return render_template('upload.html', user_id=user_id)

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user_id from session
    flash("You have been logged out.")
    return redirect(url_for('index'))  # Redirect to the homepage

if __name__ == '__main__':
    app.run(debug=True)