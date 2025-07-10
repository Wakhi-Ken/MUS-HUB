from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = '05f3477f588134db3e689a77dc84cdfe'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mus_hub.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)

# -------------------- Models --------------------
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
    user = db.relationship('User')  # For access to comment.user.Username

# -------------------- Routes --------------------
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
        new_user = User(Username=username, Email=email, Password=password, Role=role)
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.UserID
        flash("Registration successful! Please complete your profile.")
        return redirect(url_for('profile'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(Username=username, Password=password).first()
        if user:
            session['user_id'] = user.UserID
            flash("Login successful!")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password.")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login'))
    user = User.query.get(user_id)
    if request.method == 'POST':
        user.Bio = request.form.get('bio', user.Bio)
        db.session.commit()
    return render_template('profile.html', user=user)

@app.route('/')
def index():
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None
    username = user.Username if user else 'Guest'
    contents = Content.query.all()
    for content in contents:
        content.comments = Comment.query.filter_by(ContentID=content.ContentID).all()
    return render_template('index.html', username=username, contents=contents)

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

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        user_id = session.get('user_id')
        new_content = Content(UserID=user_id, FilePath=filename)
        db.session.add(new_content)
        db.session.commit()

        flash("File uploaded successfully!")
        return redirect(url_for('index'))

    user_id = session.get('user_id')
    return render_template('upload.html', user_id=user_id)

@app.route('/comment/<int:content_id>', methods=['POST'])
def add_comment(content_id):
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to comment.")
        return redirect(url_for('login'))

    comment_text = request.form.get('comment_text')
    if comment_text:
        new_comment = Comment(ContentID=content_id, UserID=user_id, CommentText=comment_text)
        db.session.add(new_comment)
        db.session.commit()
        flash("Comment added!")
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out.")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
