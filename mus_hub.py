import sqlite3  # Standard library for lightweight SQL database integration

def create_database_and_table():
    try:
        # Establish connection to the SQLite database.
        # If 'mus_hub.db' doesn't exist, it will be created in the current directory.
        connection = sqlite3.connect('mus_hub.db')
        cursor = connection.cursor()

        # Create the 'User' table.
        # 'Email' is marked UNIQUE to prevent duplicate registrations.
        # 'Role' can be used for differentiating between admin, artist, listener, etc.
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS User (
            UserID INTEGER PRIMARY KEY AUTOINCREMENT,
            Username TEXT NOT NULL,
            Email TEXT NOT NULL UNIQUE,
            Role TEXT NOT NULL,
            Bio TEXT
        )
        """)
        
        # Create the 'Content' table.
        # Stores uploaded media with a reference to the uploading user.
        # 'UploadDate' defaults to the current timestamp, which is useful for sorting.
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Content (
            ContentID INTEGER PRIMARY KEY AUTOINCREMENT,
            UserID INTEGER,
            FilePath TEXT NOT NULL,
            UploadDate DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (UserID) REFERENCES User(UserID)
        )
        """)

        # Create the 'Comment' table.
        # Tracks user comments per content.
        # Includes timestamps and foreign key relationships to both user and content.
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Comment (
            CommentID INTEGER PRIMARY KEY AUTOINCREMENT,
            ContentID INTEGER,
            UserID INTEGER,
            CommentText TEXT NOT NULL,
            CommentDate DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ContentID) REFERENCES Content(ContentID),
            FOREIGN KEY (UserID) REFERENCES User(UserID)
        )
        """)

        print("Tables 'User', 'Content', and 'Comment' created successfully.")

    except sqlite3.Error as e:
        # Catch and print any database-related errors.
        print(f"Error: {e}")
    finally:
        # Ensure that the connection is properly closed even if an error occurs.
        if connection:
            cursor.close()
            connection.close()
            print("SQLite connection is closed.")

# Entry point to ensure this function only runs when the script is executed directly.
if __name__ == "__main__":
    create_database_and_table()
