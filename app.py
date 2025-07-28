from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
# Secret key for session management and flash messages
app.secret_key = '05f3477f588134db3e689a77dc84cdfe'

# Configure database URI - using SQLite for this project
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mus_hub.db'

# Folder to store uploaded files
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Initialize SQLAlchemy with the Flask app
db = SQLAlchemy(app)

# -------------------- Models --------------------
# User model represents registered users
class User(db.Model):
    UserID = db.Column(db.Integer, primary_key=True)  # Primary key
    Username = db.Column(db.String(80), nullable=False)  # Username, required
    Email = db.Column(db.String(120), unique=True, nullable=False)  # Unique email
    Password = db.Column(db.String(200), nullable=False)  # Hashed password (should hash in real app)
    Role = db.Column(db.String(20), nullable=False)  # Role (e.g. admin, user)
    Bio = db.Column(db.String(500))  # Optional user bio
    comments = db.relationship('Comment', backref='author', lazy=True)  # One-to-many: user comments

# Content model for user-uploaded files or media
class Content(db.Model):
    ContentID = db.Column(db.Integer, primary_key=True)  # Primary key
    UserID = db.Column(db.Integer, db.ForeignKey('user.UserID'), nullable=False)  # Foreign key to User
    FilePath = db.Column(db.String(200), nullable=False)  # Path or filename of upload
    UploadDate = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp of upload

    # Relationship to User to access owner info easily
    user = db.relationship('User', backref='contents')

# Comment model for comments on uploaded content
class Comment(db.Model):
    CommentID = db.Column(db.Integer, primary_key=True)  # Primary key
    ContentID = db.Column(db.Integer, db.ForeignKey('content.ContentID'), nullable=False)  # FK to Content
    UserID = db.Column(db.Integer, db.ForeignKey('user.UserID'), nullable=False)  # FK to User
    CommentText = db.Column(db.Text, nullable=False)  # The comment text
    CommentDate = db.Column(db.DateTime, default=datetime.utcnow)  # When comment was posted
    user = db.relationship('User')  # Link to the user who posted comment

# -------------------- Context Processor --------------------
@app.context_processor
def inject_now():
    # Makes current UTC time and logged-in user id available in all templates
    return {
        'now': datetime.utcnow(),
        'current_user_id': session.get('user_id')
    }

# -------------------- Routes --------------------

@app.route('/initdb')
def init_db():
    # Create all tables in the database (run once or when needed)
    db.create_all()
    return "Database initialized!"

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Handle new user registration
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        # Create new user instance and save to DB
        new_user = User(Username=username, Email=email, Password=password, Role=role)
        db.session.add(new_user)
        db.session.commit()

        # Set session to log the user in immediately
        session['user_id'] = new_user.UserID
        flash("Registration successful! Please complete your profile.")
        return redirect(url_for('profile'))

    # GET request - render registration form
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Handle user login
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Query user with matching credentials (no password hashing here - should add in real app)
        user = User.query.filter_by(Username=username, Password=password).first()

        if user:
            # Successful login, save user_id in session
            session['user_id'] = user.UserID
            flash("Login successful!")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password.")

    # GET request - render login form
    return render_template('login.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    # Show and edit logged-in user's profile
    user_id = session.get('user_id')
    if user_id is None:
        # Redirect to login if no user logged in
        return redirect(url_for('login'))

    user = User.query.get(user_id)

    if request.method == 'POST':
        # Update bio if provided
        bio = request.form.get('bio')
        if bio is not None:
            user.Bio = bio
            db.session.commit()
            flash("Bio updated successfully!")
        return redirect(url_for('profile'))

    # GET: fetch all uploads by the user
    uploads = Content.query.filter_by(UserID=user_id).all()

    # Render profile page with user data and uploads
    return render_template('profile.html', user=user, user_uploads=uploads)

@app.route('/')
def index():
    # Homepage - shows recent uploads and welcome message
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None
    username = user.Username if user else 'Guest'

    # Fetch all content ordered by upload date descending
    contents = Content.query.order_by(Content.UploadDate.desc()).all()

    # For each content, fetch its comments ordered by date
    for content in contents:
        content.comments = Comment.query.filter_by(ContentID=content.ContentID).order_by(Comment.CommentDate).all()

    # Render index page with contents and user info
    return render_template('index.html', username=username, contents=contents)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    # Upload file handler - requires login
    if 'user_id' not in session:
        flash("Login required to upload files.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Check if file part is in request
        if 'file' not in request.files:
            flash("No file part")
            return redirect(request.url)

        file = request.files['file']

        # Check if a file was actually selected
        if file.filename == '':
            flash("No selected file")
            return redirect(request.url)

        # Secure the filename before saving
        filename = secure_filename(file.filename)

        # Construct full path and save file to upload folder
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Save the file info to database linked to current user
        user_id = session.get('user_id')
        new_content = Content(UserID=user_id, FilePath=filename)
        db.session.add(new_content)
        db.session.commit()

        flash("File uploaded successfully!")
        return redirect(url_for('index'))

    # GET: render upload form
    return render_template('upload.html')

@app.route('/comment/<int:content_id>', methods=['POST'])
def add_comment(content_id):
    # Add a comment to specific content - login required
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to comment.")
        return redirect(url_for('login'))

    comment_text = request.form.get('comment_text')
    if comment_text:
        # Create new comment and save it
        new_comment = Comment(ContentID=content_id, UserID=user_id, CommentText=comment_text)
        db.session.add(new_comment)
        db.session.commit()
        flash("Comment added!")

    return redirect(url_for('index'))

@app.route('/edit_comment/<int:comment_id>', methods=['POST'])
def edit_comment(comment_id):
    # Allow user to edit their comment within 30 seconds of posting
    user_id = session.get('user_id')
    comment = Comment.query.get(comment_id)

    if comment and comment.UserID == user_id:
        # Calculate time difference since comment was posted
        time_diff = (datetime.utcnow() - comment.CommentDate).total_seconds()
        if time_diff <= 30:
            new_text = request.form.get('comment_text')
            if new_text:
                comment.CommentText = new_text
                db.session.commit()
                flash("Comment updated.")
        else:
            flash("You can only edit comments within 30 seconds.")
    else:
        flash("Unauthorized or comment not found.")

    return redirect(url_for('index'))

@app.route('/delete/<int:content_id>', methods=['POST'])
def delete_upload(content_id):
    # Allow logged-in user to delete their own uploaded content
    user_id = session.get('user_id')
    if not user_id:
        flash("Login required.")
        return redirect(url_for('login'))

    content = Content.query.get(content_id)
    if content and content.UserID == user_id:
        # Remove file from filesystem
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], content.FilePath)
        if os.path.exists(file_path):
            os.remove(file_path)

        # Remove content record from database
        db.session.delete(content)
        db.session.commit()
        flash("Upload deleted.")
    else:
        flash("Unauthorized or content not found.")

    return redirect(url_for('profile'))

@app.route('/logout')
def logout():
    # Clear user session and logout
    session.pop('user_id', None)
    flash("You have been logged out.")
    return redirect(url_for('login'))

# ----------- Public profile page -----------
@app.route('/user/<int:user_id>')
def public_profile(user_id):
    # Public view of a user's profile and uploads
    user = User.query.get_or_404(user_id)
    uploads = Content.query.filter_by(UserID=user_id).order_by(Content.UploadDate.desc()).all()
    return render_template('public_profile.html', user=user, uploads=uploads)

# ----------- UPDATED Search Route -----------
@app.route('/search')
def search():
    # Search users by username or role, and uploads by filename or uploader
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to use the search function.")
        return redirect(url_for('login'))

    query = request.args.get('q', '').strip()
    if not query:
        flash("Please enter a search term.")
        return redirect(url_for('index'))

    # Find users matching query
    users = User.query.filter(
        (User.Username.ilike(f'%{query}%')) |
        (User.Role.ilike(f'%{query}%'))
    ).all()

    # Find uploads matching query or uploaded by matched users
    uploads = Content.query.filter(
        (Content.FilePath.ilike(f'%{query}%')) |
        (Content.UserID.in_([user.UserID for user in users]))
    ).all()

    # Attach user object to each upload for display
    for upload in uploads:
        upload.user = User.query.get(upload.UserID)

    # Render search results page
    return render_template('search_results.html', query=query, users=users, uploads=uploads)

# ------------------ Run App ------------------
if __name__ == '__main__':
    # Run app in debug mode for easier development
    app.run(debug=True)




