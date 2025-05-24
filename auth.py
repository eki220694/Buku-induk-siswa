import sqlite3
import bcrypt
import logging
import os

DATABASE_NAME = 'student_records.db'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db_connection():
    """Establishes and returns a database connection."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

def initialize_auth_database():
    """
    Connects to the SQLite database and creates the 'users' table
    if it doesn't already exist.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    hashed_password TEXT NOT NULL,
                    role TEXT DEFAULT 'admin' CHECK(role IN ('admin', 'teacher', 'student_viewer')) 
                )
            ''')
            # Added more roles for potential future flexibility as per good practice
            conn.commit()
            logging.info("Checked/created 'users' table in the database.")
    except sqlite3.Error as e:
        logging.error(f"Auth database initialization error: {e}")
        raise

def create_user(username: str, password: str, role: str = 'admin') -> bool:
    """
    Creates a new user with a hashed password and stores it in the database.
    Uses bcrypt for password hashing.

    Args:
        username (str): The username for the new user.
        password (str): The plaintext password for the new user.
        role (str): The role for the new user (e.g., 'admin').

    Returns:
        bool: True if user creation is successful, False otherwise.
    """
    if not username or not password:
        logging.error("Username and password cannot be empty.")
        return False
    try:
        # Hash the password using bcrypt
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    except Exception as e:
        logging.error(f"Error hashing password with bcrypt: {e}")
        # Fallback to hashlib if bcrypt fails for some reason (e.g. unexpected error)
        # This is a secondary fallback, primary was pip install.
        logging.info("Attempting fallback to hashlib for password hashing.")
        try:
            import hashlib
            salt = os.urandom(16) # Generate a random salt
            hashed_password_bytes = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
            # Store as "salt:hash" to indicate hashlib was used
            hashed_password = f"hashlib_sha256_100000:{salt.hex()}:{hashed_password_bytes.hex()}".encode('utf-8')
        except Exception as hashlib_e:
            logging.error(f"Error hashing password with hashlib fallback: {hashlib_e}")
            return False


    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, hashed_password, role) VALUES (?, ?, ?)",
                (username, hashed_password.decode('utf-8'), role) # Store hash as string
            )
            conn.commit()
            logging.info(f"User '{username}' created successfully with role '{role}'.")
            return True
    except sqlite3.IntegrityError:
        logging.warning(f"Username '{username}' already exists.")
        return False
    except sqlite3.Error as e:
        logging.error(f"Database error creating user '{username}': {e}")
        return False

def verify_user(username: str, password: str) -> bool:
    """
    Verifies a user's credentials.

    Args:
        username (str): The username to verify.
        password (str): The plaintext password to verify.

    Returns:
        bool: True if the username exists and the password matches, False otherwise.
    """
    if not username or not password:
        logging.error("Username and password cannot be empty for verification.")
        return False
        
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT hashed_password FROM users WHERE username = ?", (username,))
            user_record = cursor.fetchone()

            if user_record:
                stored_hash = user_record['hashed_password']
                
                # Check if it's a hashlib fallback hash
                if stored_hash.startswith("hashlib_sha256_100000:"):
                    try:
                        import hashlib
                        parts = stored_hash.split(':')
                        if len(parts) != 3:
                            logging.error(f"Invalid hashlib hash format for user '{username}'.")
                            return False
                        
                        _ , salt_hex, original_hash_hex = parts
                        salt = bytes.fromhex(salt_hex)
                        
                        provided_password_hash_bytes = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
                        
                        if provided_password_hash_bytes.hex() == original_hash_hex:
                            logging.info(f"User '{username}' verified successfully (hashlib).")
                            return True
                        else:
                            logging.warning(f"Password mismatch for user '{username}' (hashlib).")
                            return False
                    except Exception as e:
                        logging.error(f"Error during hashlib verification for user '{username}': {e}")
                        return False
                else:
                    # Assume bcrypt
                    if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                        logging.info(f"User '{username}' verified successfully (bcrypt).")
                        return True
                    else:
                        logging.warning(f"Password mismatch for user '{username}' (bcrypt).")
                        return False
            else:
                logging.warning(f"User '{username}' not found.")
                return False
    except sqlite3.Error as e:
        logging.error(f"Database error verifying user '{username}': {e}")
        return False
    except Exception as e: # Catch potential bcrypt errors if hash is malformed
        logging.error(f"General error during verification for user '{username}': {e}")
        return False

def get_user_count() -> int:
    """
    Counts the total number of users in the 'users' table.

    Returns:
        int: The number of users, or 0 if an error occurs or table is empty.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            count_result = cursor.fetchone()
            if count_result:
                return count_result[0]
            return 0 # Should not happen if query is correct and table exists
    except sqlite3.Error as e:
        logging.error(f"Database error counting users: {e}")
        return 0 # Return 0 on error to allow default user creation if table is missing initially

if __name__ == '__main__':
    logging.info("Running example authentication operations...")
    
    # (Re)Initialize the users table for a clean test
    # In a real app, this is typically done once at setup.
    # For testing, ensure the DB file is in a known state or remove it before running.
    # If student_records.db is managed by database_operations.py, ensure this doesn't conflict.
    # For this test, we assume it's okay to initialize here.
    # To ensure a clean test, one might delete the DB file before running.
    # try:
    #     if os.path.exists(DATABASE_NAME):
    #         os.remove(DATABASE_NAME)
    #         logging.info(f"Removed existing {DATABASE_NAME} for a clean test run.")
    # except OSError as e:
    #     logging.error(f"Error removing database for test: {e}")

    initialize_auth_database() # Make sure users table exists

    # Test user creation
    admin_created = create_user('admin_user', 'securepass123', 'admin')
    if admin_created:
        logging.info("Admin user created (or already existed and failed gracefully).")
    
    # Test duplicate user creation
    admin_duplicate_created = create_user('admin_user', 'anotherpass', 'admin')
    if not admin_duplicate_created:
        logging.info("Correctly failed to create duplicate admin user.")

    # Test get_user_count
    user_count = get_user_count()
    logging.info(f"Current user count: {user_count}")
    if admin_created : # If the first user was indeed created now
        expected_count = 1
        if user_count != expected_count:
             logging.error(f"User count expected {expected_count} but got {user_count}")
    elif user_count == 0 and not admin_created : # User already existed
        logging.warning(f"User count is 0 but admin_user might have existed. Test logic for count might be off if DB wasn't clean.")
    elif user_count > 0:
        logging.info(f"User count is > 0, which is expected if admin_user already existed or other users are present.")


    # Test user verification
    logging.info("Verifying 'admin_user' with correct password...")
    if verify_user('admin_user', 'securepass123'):
        logging.info("Verification successful for 'admin_user'.")
    else:
        logging.error("Verification FAILED for 'admin_user' with correct password.")

    logging.info("Verifying 'admin_user' with incorrect password...")
    if not verify_user('admin_user', 'wrongpass'):
        logging.info("Correctly failed verification for 'admin_user' with incorrect password.")
    else:
        logging.error("Verification succeeded for 'admin_user' with incorrect password (UNEXPECTED).")

    logging.info("Verifying non-existent user 'nouser'...")
    if not verify_user('nouser', 'anypass'):
        logging.info("Correctly failed verification for non-existent user 'nouser'.")
    else:
        logging.error("Verification succeeded for non-existent user 'nouser' (UNEXPECTED).")
    
    # Test user creation with hashlib fallback (manual intervention needed to test this)
    # To test hashlib: temporarily break bcrypt import or make bcrypt.hashpw raise an error
    # For example, by renaming bcrypt to something else temporarily in the import
    # or adding `raise Exception("Simulated bcrypt failure")` in the bcrypt try block.
    # test_hashlib_user = create_user("hashlib_user", "fallback123", "admin")
    # if test_hashlib_user:
    #    logging.info("Hashlib test user created.")
    #    if verify_user("hashlib_user", "fallback123"):
    #        logging.info("Hashlib test user verified.")
    #    else:
    #        logging.error("Hashlib test user FAILED verification.")

    logging.info("Authentication example operations completed.")
    # Note: The student_records.db will now contain a 'users' table.
    # The database_operations.py file's initialize_database() will also run on this
    # same database file, adding its tables if they don't exist. This is fine.
    # The main application would call both initialize_auth_database() and 
    # initialize_database() from database_operations.py at startup.
    
    # To ensure the student_records.db is not deleted if other tests depend on it,
    # the db removal part of this test is commented out.
    # If you want to run this test in complete isolation, uncomment the db removal.
    # For now, it appends/checks the users table in the existing student_records.db.
    
    # Example of how database_operations.py might be used in conjunction:
    # import database_operations
    # database_operations.initialize_database() # Ensures student and grades tables also exist.
    # logging.info("Student and grades tables also initialized if not present.")

    # For this subtask, the focus is on auth.py. The above calls are illustrative.
    # The actual `database_operations.py` is not modified by this step.
    # The subtask description mentions "Ensure the initialize_database() function in 
    # database_operations.py is called to create the new users table if it's added there."
    # However, I've chosen to create auth.py and handle user table creation within 
    # initialize_auth_database() for better separation of concerns.
    # The main application would be responsible for calling both initialization functions.
    # No changes are needed to database_operations.py for this approach.
    # If the users table was to be added in database_operations.py, then that file would be modified.
    # The prompt allows for creating auth.py if it makes more sense, which I've done.I have created the `auth.py` file as requested.

**Summary of `auth.py`:**
1.  **`DATABASE_NAME`**: Set to `student_records.db`.
2.  **`get_db_connection()`**: Standard SQLite connection function.
3.  **`initialize_auth_database()`**:
    *   Creates the `users` table with `id` (PK, AI), `username` (UNIQUE, NOT NULL), `hashed_password` (NOT NULL), and `role` (DEFAULT 'admin', with a CHECK constraint for future roles like 'teacher', 'student_viewer').
4.  **`create_user(username, password, role='admin')`**:
    *   Hashes the password using `bcrypt.hashpw()` after generating a salt with `bcrypt.gensalt()`.
    *   Includes a fallback to `hashlib.pbkdf2_hmac` (SHA256 with 100,000 iterations and a 16-byte salt) if `bcrypt` hashing fails unexpectedly (though `bcrypt` was installed and should be primary). The salt and hash are stored in a `hashlib_sha256_100000:salt_hex:hash_hex` format if `hashlib` is used.
    *   Stores the `username`, `hashed_password` (as string), and `role` in the `users` table.
    *   Returns `True` on success, `False` on failure (e.g., empty credentials, username exists, hashing error, DB error).
5.  **`verify_user(username, password)`**:
    *   Retrieves the user's `hashed_password` from the `users` table.
    *   If the hash string indicates `hashlib` was used (by checking the prefix), it splits the salt and hash, re-hashes the provided password using the stored salt, and compares.
    *   Otherwise, it assumes `bcrypt` and uses `bcrypt.checkpw()` for verification.
    *   Returns `True` if the password matches, `False` otherwise (user not found, password mismatch, or error).
6.  **`if __name__ == '__main__':` block**:
    *   Includes example usage for `initialize_auth_database()`, `create_user()` (including testing duplicate creation), and `verify_user()` (testing correct and incorrect passwords, and non-existent user).
    *   It also logs information about these operations.

**Regarding `database_operations.py`:**
*   No modifications were made to `database_operations.py`. The `users` table and its related functions are fully contained within `auth.py` for better separation of concerns, as allowed by the subtask description ("create a new `auth.py` if it makes more sense for organization").
*   The main application (if it existed) would be responsible for calling both `initialize_auth_database()` from `auth.py` and `initialize_database()` from `database_operations.py` at startup to ensure all necessary tables are created in the `student_records.db` file.

The `bcrypt` library was successfully installed in the previous step and is the primary method for hashing. The `hashlib` fallback is a contingency.
