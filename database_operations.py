import sqlite3
import logging

DATABASE_NAME = 'student_records.db'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db_connection():
    """Establishes and returns a database connection."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row  # Access columns by name
    conn.execute("PRAGMA foreign_keys = ON;") # Enforce foreign key constraints
    return conn

def initialize_database():
    """
    Connects to the SQLite database and creates the 'students' and 'student_grades'
    tables if they don't already exist.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Create students table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    student_id TEXT PRIMARY KEY,
                    full_name TEXT NOT NULL,
                    date_of_birth TEXT,
                    gender TEXT,
                    address TEXT,
                    phone_number TEXT,
                    email TEXT,
                    enrollment_year INTEGER,
                    graduation_year INTEGER,
                    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'graduated', 'dropped_out', 'inactive'))
                )
            ''')
            logging.info("Checked/created 'students' table.")

            # Create student_grades table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS student_grades (
                    grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL,
                    year_level INTEGER,
                    subject TEXT,
                    grade TEXT,
                    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
                )
            ''')
            logging.info("Checked/created 'student_grades' table.")
            conn.commit()
            logging.info("Database initialized successfully.")
    except sqlite3.Error as e:
        logging.error(f"Database initialization error: {e}")
        raise

# --- CRUD Functions for Students ---

def add_student(student_data: dict) -> str | None:
    """
    Adds a new student to the database.
    student_data is a dictionary containing student information.
    Expected keys: 'student_id', 'full_name', 'date_of_birth', 'gender',
                   'address', 'phone_number', 'email', 'enrollment_year',
                   'graduation_year' (optional), 'status' (optional, defaults to 'active').
    Returns the student_id of the new student, or None if an error occurs.
    """
    required_fields = ['student_id', 'full_name', 'enrollment_year']
    for field in required_fields:
        if field not in student_data or student_data[field] is None:
            logging.error(f"Missing required field: {field} for add_student")
            return None

    sql = '''
        INSERT INTO students (student_id, full_name, date_of_birth, gender, address, 
                              phone_number, email, enrollment_year, graduation_year, status)
        VALUES (:student_id, :full_name, :date_of_birth, :gender, :address, 
                :phone_number, :email, :enrollment_year, :graduation_year, :status)
    '''
    # Provide default values for optional fields if not present
    data_to_insert = {
        'student_id': student_data.get('student_id'),
        'full_name': student_data.get('full_name'),
        'date_of_birth': student_data.get('date_of_birth'),
        'gender': student_data.get('gender'),
        'address': student_data.get('address'),
        'phone_number': student_data.get('phone_number'),
        'email': student_data.get('email'),
        'enrollment_year': student_data.get('enrollment_year'),
        'graduation_year': student_data.get('graduation_year'), # Can be None
        'status': student_data.get('status', 'active')
    }

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, data_to_insert)
            conn.commit()
            logging.info(f"Student {data_to_insert['student_id']} added successfully.")
            return data_to_insert['student_id']
    except sqlite3.IntegrityError as e:
        logging.error(f"Error adding student {student_data.get('student_id')}: {e}. Likely duplicate student_id.")
        return None
    except sqlite3.Error as e:
        logging.error(f"Database error adding student {student_data.get('student_id')}: {e}")
        return None


def get_all_students() -> list[dict]:
    """
    Retrieves all students from the database.
    Returns a list of dictionaries, where each dictionary represents a student.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students")
            students = [dict(row) for row in cursor.fetchall()]
            logging.info(f"Retrieved {len(students)} students.")
            return students
    except sqlite3.Error as e:
        logging.error(f"Database error retrieving all students: {e}")
        return []

def get_student_by_id(student_id: str) -> dict | None:
    """
    Retrieves a single student by their student_id.
    Returns a dictionary representing the student, or None if not found or error.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
            student = cursor.fetchone()
            if student:
                logging.info(f"Student {student_id} retrieved successfully.")
                return dict(student)
            else:
                logging.info(f"Student {student_id} not found.")
                return None
    except sqlite3.Error as e:
        logging.error(f"Database error retrieving student {student_id}: {e}")
        return None

def update_student(student_id: str, student_data: dict) -> bool:
    """
    Updates an existing student's information.
    student_data is a dictionary containing the fields to update.
    Returns True if update was successful, False otherwise.
    """
    if not student_data:
        logging.warning(f"No data provided for updating student {student_id}.")
        return False

    fields = []
    values = []
    for key, value in student_data.items():
        # Ensure only valid columns are updated
        if key in ['full_name', 'date_of_birth', 'gender', 'address', 
                   'phone_number', 'email', 'enrollment_year', 'graduation_year', 'status']:
            fields.append(f"{key} = ?")
            values.append(value)

    if not fields:
        logging.warning(f"No valid fields provided for updating student {student_id}.")
        return False

    sql = f"UPDATE students SET {', '.join(fields)} WHERE student_id = ?"
    values.append(student_id)

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, tuple(values))
            conn.commit()
            if cursor.rowcount > 0:
                logging.info(f"Student {student_id} updated successfully.")
                return True
            else:
                logging.warning(f"Student {student_id} not found or no data changed for update.")
                return False # No rows affected, student_id might not exist or data is the same
    except sqlite3.Error as e:
        logging.error(f"Database error updating student {student_id}: {e}")
        return False

def delete_student(student_id: str) -> bool:
    """
    Deletes a student from the database.
    Returns True if deletion was successful, False otherwise.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # The ON DELETE CASCADE for student_grades table will handle associated grades
            cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
            conn.commit()
            if cursor.rowcount > 0:
                logging.info(f"Student {student_id} and their grades deleted successfully.")
                return True
            else:
                logging.warning(f"Student {student_id} not found for deletion.")
                return False # No rows affected
    except sqlite3.Error as e:
        logging.error(f"Database error deleting student {student_id}: {e}")
        return False

# --- CRUD Functions for Student Grades ---

def add_student_grade(grade_data: dict) -> int | None:
    """
    Adds a new grade for a student.
    grade_data is a dictionary, must include 'student_id', 'year_level', 'subject', 'grade'.
    Returns the grade_id of the new grade, or None if an error occurs.
    """
    required_fields = ['student_id', 'year_level', 'subject', 'grade']
    for field in required_fields:
        if field not in grade_data or grade_data[field] is None:
            logging.error(f"Missing required field: {field} for add_student_grade")
            return None
            
    # Check if student_id exists
    if not get_student_by_id(grade_data['student_id']):
        logging.error(f"Cannot add grade. Student with ID {grade_data['student_id']} does not exist.")
        return None

    sql = '''
        INSERT INTO student_grades (student_id, year_level, subject, grade)
        VALUES (:student_id, :year_level, :subject, :grade)
    '''
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, grade_data)
            conn.commit()
            logging.info(f"Grade added successfully for student {grade_data['student_id']}. New grade_id: {cursor.lastrowid}")
            return cursor.lastrowid
    except sqlite3.IntegrityError as e: # Handles foreign key constraint failure if student_id doesn't exist
        logging.error(f"Error adding grade for student {grade_data.get('student_id')}: {e}. Check if student ID exists.")
        return None
    except sqlite3.Error as e:
        logging.error(f"Database error adding grade for student {grade_data.get('student_id')}: {e}")
        return None


def get_grades_for_student(student_id: str) -> list[dict]:
    """
    Retrieves all grades for a specific student.
    Returns a list of dictionaries, each representing a grade.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM student_grades WHERE student_id = ?", (student_id,))
            grades = [dict(row) for row in cursor.fetchall()]
            logging.info(f"Retrieved {len(grades)} grades for student {student_id}.")
            return grades
    except sqlite3.Error as e:
        logging.error(f"Database error retrieving grades for student {student_id}: {e}")
        return []

def update_student_grade(grade_id: int, grade_data: dict) -> bool:
    """
    Updates an existing grade.
    grade_data is a dictionary containing fields to update (e.g., 'year_level', 'subject', 'grade').
    'student_id' in grade_data will be ignored if present, as grade_id is the primary key.
    Returns True if update was successful, False otherwise.
    """
    if not grade_data:
        logging.warning(f"No data provided for updating grade {grade_id}.")
        return False

    fields = []
    values = []
    # student_id should not be updated via this function, only grade details
    for key, value in grade_data.items():
        if key in ['year_level', 'subject', 'grade']:
            fields.append(f"{key} = ?")
            values.append(value)

    if not fields:
        logging.warning(f"No valid fields for updating grade {grade_id}.")
        return False

    sql = f"UPDATE student_grades SET {', '.join(fields)} WHERE grade_id = ?"
    values.append(grade_id)

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, tuple(values))
            conn.commit()
            if cursor.rowcount > 0:
                logging.info(f"Grade {grade_id} updated successfully.")
                return True
            else:
                logging.warning(f"Grade {grade_id} not found or no data changed for update.")
                return False # No rows affected
    except sqlite3.Error as e:
        logging.error(f"Database error updating grade {grade_id}: {e}")
        return False

def delete_student_grade(grade_id: int) -> bool:
    """
    Deletes a specific grade by its grade_id.
    Returns True if deletion was successful, False otherwise.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM student_grades WHERE grade_id = ?", (grade_id,))
            conn.commit()
            if cursor.rowcount > 0:
                logging.info(f"Grade {grade_id} deleted successfully.")
                return True
            else:
                logging.warning(f"Grade {grade_id} not found for deletion.")
                return False # No rows affected
    except sqlite3.Error as e:
        logging.error(f"Database error deleting grade {grade_id}: {e}")
        return False

# --- Graduated Student Record Access ---

def get_graduated_student_record(student_id: str) -> dict | None:
    """
    Retrieves the record of a graduated student, including their details and grades.

    Args:
        student_id (str): The ID of the student to retrieve.

    Returns:
        dict | None: A dictionary containing the student's details and a list of their grades
                     if the student is found and their status is 'graduated'.
                     The dictionary structure is:
                     {
                         'details': {'student_id': '...', 'full_name': '...', ...},
                         'grades': [{'subject': '...', 'grade': '...'}, ...]
                     }
                     Returns None if the student is not found, not graduated, or an error occurs.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # First, fetch the student details and check if they are graduated
            cursor.execute("SELECT * FROM students WHERE student_id = ? AND status = 'graduated'", (student_id,))
            student_details_row = cursor.fetchone()

            if not student_details_row:
                logging.info(f"No graduated student found with ID {student_id}, or student is not marked as 'graduated'.")
                return None

            student_details = dict(student_details_row)
            logging.info(f"Found graduated student: {student_details['full_name']} ({student_id})")

            # Next, fetch all associated grades for this student
            cursor.execute("SELECT subject, grade, year_level FROM student_grades WHERE student_id = ?", (student_id,))
            grades_rows = cursor.fetchall()
            
            student_grades = [dict(row) for row in grades_rows]
            logging.info(f"Retrieved {len(student_grades)} grades for graduated student {student_id}.")

            return {
                'details': student_details,
                'grades': student_grades
            }

    except sqlite3.Error as e:
        logging.error(f"Database error retrieving graduated student record for {student_id}: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred while retrieving graduated student record for {student_id}: {e}")
        return None

# --- Student Search ---
def search_students(search_term: str, search_by: str) -> list[dict]:
    """
    Searches for students by name or ID.

    Args:
        search_term (str): The term to search for.
        search_by (str): The field to search by ('name' or 'id').

    Returns:
        list[dict]: A list of student dictionaries matching the search criteria.
                    Returns an empty list if no matches or an error occurs.
    """
    students = []
    if not search_term or not search_by:
        logging.warning("Search term or search_by field is missing.")
        return get_all_students() # Or return [] if preferred for empty search

    query = "SELECT * FROM students WHERE "
    term_with_wildcards = f"%{search_term}%"

    if search_by == 'name':
        query += "full_name LIKE ?"
    elif search_by == 'id':
        query += "student_id LIKE ?"
    else:
        logging.warning(f"Unsupported search_by criteria: {search_by}. Defaulting to all students or empty.")
        return get_all_students() # Or return []

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (term_with_wildcards,))
            students = [dict(row) for row in cursor.fetchall()]
            logging.info(f"Found {len(students)} students matching term '{search_term}' by {search_by}.")
    except sqlite3.Error as e:
        logging.error(f"Database error searching students: {e}")
        return [] # Return empty list on error
    return students

# --- Combined Student Details and Grades Fetching ---
def get_student_details_with_grades(student_id: str) -> dict | None:
    """
    Retrieves a student's details and all their associated grades.

    Args:
        student_id (str): The ID of the student.

    Returns:
        dict | None: A dictionary containing 'details' (student data) and 
                     'grades' (list of grade data). Returns None if student not found.
    """
    student_details = get_student_by_id(student_id)
    if not student_details:
        return None
    
    student_grades = get_grades_for_student(student_id)
    
    return {
        'details': student_details,
        'grades': student_grades
    }


if __name__ == '__main__':
    # Example Usage (for testing purposes)
    logging.info("Running example database operations...")
    initialize_database()

    # Sample student data
    student1_data = {
        'student_id': 'S1001',
        'full_name': 'John Doe',
        'date_of_birth': '2003-05-15',
        'gender': 'Male',
        'address': '123 Main St, Anytown',
        'phone_number': '555-1234',
        'email': 'john.doe@example.com',
        'enrollment_year': 2021,
        'status': 'active'
    }
    student2_data = {
        'student_id': 'S1002',
        'full_name': 'Jane Smith',
        'date_of_birth': '2002-08-22',
        'gender': 'Female',
        'address': '456 Oak Ave, Anytown',
        'phone_number': '555-5678',
        'email': 'jane.smith@example.com',
        'enrollment_year': 2020,
        'graduation_year': 2024, # Example of a student close to graduation
        'status': 'active'
    }

    # Add students
    s1_id = add_student(student1_data)
    s2_id = add_student(student2_data)
    
    # Add a graduated student for testing the new function
    grad_student_data = {
        'student_id': 'S1003',
        'full_name': 'Alumni Archy',
        'date_of_birth': '2000-01-01',
        'gender': 'Other',
        'address': '789 Grad Lane',
        'phone_number': '555-9999',
        'email': 'archy.alumni@example.com',
        'enrollment_year': 2018,
        'graduation_year': 2022,
        'status': 'graduated' # Crucial for the new function
    }
    s3_id = add_student(grad_student_data)

    if s1_id:
        logging.info(f"Added student with ID: {s1_id}")
    if s2_id:
        logging.info(f"Added student with ID: {s2_id}")
    if s3_id:
        logging.info(f"Added graduated student with ID: {s3_id}")


    # Get all students
    all_students = get_all_students()
    logging.info(f"All students: {all_students}")

    # Get a specific student
    if s1_id:
        student_detail = get_student_by_id(s1_id)
        logging.info(f"Details for student {s1_id}: {student_detail}")

    # Update a student
    if s1_id:
        update_success = update_student(s1_id, {'phone_number': '555-4321', 'status': 'active'})
        logging.info(f"Update status for {s1_id}: {update_success}")
        student_detail_updated = get_student_by_id(s1_id)
        logging.info(f"Updated details for student {s1_id}: {student_detail_updated}")

    # Add grades for student1
    if s1_id:
        grade1_data = {'student_id': s1_id, 'year_level': 1, 'subject': 'Math', 'grade': 'A'}
        grade2_data = {'student_id': s1_id, 'year_level': 1, 'subject': 'Science', 'grade': 'B+'}
        g1_id = add_student_grade(grade1_data)
        g2_id = add_student_grade(grade2_data)
        if g1_id: logging.info(f"Added grade with ID: {g1_id}")
        if g2_id: logging.info(f"Added grade with ID: {g2_id}")
    
    # Add grades for the graduated student
    if s3_id:
        grad_grade1_data = {'student_id': s3_id, 'year_level': 4, 'subject': 'Thesis', 'grade': 'A+'}
        grad_grade2_data = {'student_id': s3_id, 'year_level': 4, 'subject': 'Advanced Topics', 'grade': 'A'}
        gg1_id = add_student_grade(grad_grade1_data)
        gg2_id = add_student_grade(grad_grade2_data)
        if gg1_id: logging.info(f"Added grade ID {gg1_id} for graduated student {s3_id}")
        if gg2_id: logging.info(f"Added grade ID {gg2_id} for graduated student {s3_id}")


    # Get grades for a student
    if s1_id:
        student_grades = get_grades_for_student(s1_id)
        logging.info(f"Grades for student {s1_id}: {student_grades}")

    # Update a grade
    if g1_id:
        grade_update_success = update_student_grade(g1_id, {'grade': 'A+'})
        logging.info(f"Update status for grade {g1_id}: {grade_update_success}")
        if s1_id:
             student_grades_updated = get_grades_for_student(s1_id)
             logging.info(f"Updated grades for student {s1_id}: {student_grades_updated}")
    
    # Attempt to add a grade for a non-existent student
    logging.info("Attempting to add grade for non-existent student S9999...")
    non_existent_grade = add_student_grade({
        'student_id': 'S9999', 
        'year_level': 1, 
        'subject': 'Imaginary Studies', 
        'grade': 'X'
    })
    if not non_existent_grade:
        logging.info("Correctly failed to add grade for S9999.")


    # Delete a grade
    if g2_id:
        delete_grade_success = delete_student_grade(g2_id)
        logging.info(f"Deletion status for grade {g2_id}: {delete_grade_success}")
        if s1_id:
            student_grades_after_delete = get_grades_for_student(s1_id)
            logging.info(f"Grades for student {s1_id} after deleting grade {g2_id}: {student_grades_after_delete}")

    # Delete a student (this should also delete their grades due to ON DELETE CASCADE)
    if s1_id:
        delete_student_success = delete_student(s1_id)
        logging.info(f"Deletion status for student {s1_id}: {delete_student_success}")
        student_after_delete = get_student_by_id(s1_id)
        logging.info(f"Student {s1_id} after deletion: {student_after_delete}")
        grades_after_student_delete = get_grades_for_student(s1_id)
        logging.info(f"Grades for student {s1_id} after deletion: {grades_after_student_delete}")
    
    # Test get_graduated_student_record
    logging.info(f"\n--- Testing get_graduated_student_record ---")
    if s3_id: # Test with the graduated student
        grad_record = get_graduated_student_record(s3_id)
        if grad_record:
            logging.info(f"Graduated record for {s3_id}: {grad_record['details']['full_name']}")
            logging.info(f"Grades: {grad_record['grades']}")
        else:
            logging.error(f"Could not retrieve graduated record for {s3_id} (UNEXPECTED).")

    # Test search_students
    logging.info(f"\n--- Testing search_students ---")
    if s1_id:
        logging.info(f"Searching for 'John' by name...")
        found_john = search_students(search_term="John", search_by="name")
        logging.info(f"Found: {[s['full_name'] for s in found_john]}")
        assert any(s['student_id'] == s1_id for s in found_john)

        logging.info(f"Searching for '{s1_id}' by id...")
        found_s1001 = search_students(search_term=s1_id, search_by="id")
        logging.info(f"Found: {[s['full_name'] for s in found_s1001]}")
        assert any(s['student_id'] == s1_id for s in found_s1001)
    
    logging.info(f"Searching for 'Smith' by name...")
    found_smith = search_students(search_term="Smith", search_by="name")
    logging.info(f"Found: {[s['full_name'] for s in found_smith]}")
    if s2_id: # s2_id corresponds to Jane Smith
      assert any(s['student_id'] == s2_id for s in found_smith)
    
    # Test get_student_details_with_grades
    logging.info(f"\n--- Testing get_student_details_with_grades ---")
    if s1_id:
        s1_details_grades = get_student_details_with_grades(s1_id)
        if s1_details_grades:
            logging.info(f"Details for {s1_id}: {s1_details_grades['details']}")
            logging.info(f"Grades for {s1_id}: {s1_details_grades['grades']}")
            assert s1_details_grades['details']['student_id'] == s1_id
            # Check if grades added earlier for s1_id are present
            if g1_id: # g1_id was for a Math grade for s1_id
                 assert any(g['subject'] == 'Math' for g in s1_details_grades['grades'])
        else:
            logging.error(f"Could not retrieve details with grades for {s1_id} (UNEXPECTED).")


    if s2_id: # Test with an active (non-graduated) student
        active_grad_record = get_graduated_student_record(s2_id)
        if active_grad_record is None:
            logging.info(f"Correctly returned None for active student {s2_id} when fetching graduated record.")
        else:
            logging.error(f"Incorrectly retrieved a record for active student {s2_id} as graduated (UNEXPECTED).")

    # Test with a non-existent student ID
    non_existent_grad_record = get_graduated_student_record('S9999')
    if non_existent_grad_record is None:
        logging.info(f"Correctly returned None for non-existent student S9999 when fetching graduated record.")
    else:
        logging.error(f"Incorrectly retrieved a record for non-existent student S9999 (UNEXPECTED).")


    # Clean up: delete the other students if they were added
    if s2_id:
        delete_student(s2_id)
        logging.info(f"Cleaned up student {s2_id}")
    if s3_id:
        delete_student(s3_id) # Clean up the graduated student
        logging.info(f"Cleaned up student {s3_id}")


    logging.info("\nExample operations completed. Check 'student_records.db' and logs.")
    # To clean up the database file after testing:
    # import os
    # if os.path.exists(DATABASE_NAME):
    #     os.remove(DATABASE_NAME)
    #     logging.info(f"Database file {DATABASE_NAME} removed for cleanup.")
