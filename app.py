from flask import Flask, render_template, request, redirect, url_for, session, flash
import os

app = Flask(__name__)
app.secret_key = '05f3477f588134db3e689a77dc84cdfe'  # Change this to a random secret key
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# In-memory user storage for demonstration (replace with a database in production)
users = {}

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        # Create user and set session
        user_id = len(users) + 1
        users[user_id] = {'Username': username, 'Email': email, 'Password': password, 'Role': role}
        session['user_id'] = user_id
        flash("Registration successful! Please complete your profile.")
        return redirect(url_for('profile', user_id=user_id))
    
    return render_template('register.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('register'))
    
    user = users.get(user_id)
    if request.method == 'POST':
        # Handle profile update if needed
        pass
    
    return render_template('profile.html', user=user)

@app.route('/')
def index():
    user_id = session.get('user_id')
    username = users[user_id]['Username'] if user_id and user_id in users else 'Guest'
    return render_template('index.html', username=username)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        flash("File uploaded successfully!")
        return redirect(url_for('index'))
    
    user_id = session.get('user_id')
    return render_template('upload.html', user_id=user_id)

if __name__ == '__main__':
    app.run(debug=True)