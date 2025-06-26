import sqlite3

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('mus_hub.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create the user table
cursor.execute('''
CREATE TABLE IF NOT EXISTS user (
    UserID INTEGER PRIMARY KEY AUTOINCREMENT,
    Username TEXT NOT NULL,
    Email TEXT NOT NULL UNIQUE,
    Role TEXT NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Create the content table
cursor.execute('''
CREATE TABLE IF NOT EXISTS content (
    ContentID INTEGER PRIMARY KEY AUTOINCREMENT,
    UserID INTEGER NOT NULL,
    FilePath TEXT NOT NULL,
    UploadDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserID) REFERENCES user (UserID)
)
''')

# Create the comment table
cursor.execute('''
CREATE TABLE IF NOT EXISTS comment (
    CommentID INTEGER PRIMARY KEY AUTOINCREMENT,
    ContentID INTEGER NOT NULL,
    UserID INTEGER NOT NULL,
    CommentText TEXT NOT NULL,
    CommentDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ContentID) REFERENCES content (ContentID),
    FOREIGN KEY (UserID) REFERENCES user (UserID)
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Tables created successfully.")