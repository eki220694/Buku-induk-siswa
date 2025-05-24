import unittest
import logging
import sys

# --- Monkey-patching DATABASE_NAME before importing modules ---
# This is a common way to redirect database operations to an in-memory DB for tests.
# We need to do this before `auth` and `database_operations` are imported.

# Add a mock for 'auth' and 'database_operations' to sys.modules
# This ensures that when we import them later, they are fresh and will use the patched DB_NAME
# This is more robust than just setting a global if the modules were already imported somewhere.
class MockDbModule:
    DATABASE_NAME = ':memory:'

sys.modules['auth_config'] = MockDbModule()
sys.modules['db_config'] = MockDbModule()

# Now, we can import the modules. They should pick up the patched DATABASE_NAME.
import auth
import database_operations

# Set the DATABASE_NAME in the actual modules to :memory:
auth.DATABASE_NAME = ':memory:'
database_operations.DATABASE_NAME = ':memory:'
# --- End of monkey-patching ---


# Suppress logging from the modules being tested during test execution
# Store original logging level
original_logging_level = logging.getLogger().getEffectiveLevel()

class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Suppress logging from the modules being tested
        logging.disable(logging.CRITICAL)
        
        # Ensure a clean start for each test class using in-memory DB
        # The monkey-patching of DATABASE_NAME to ':memory:' handles this.
        # Initialize both databases
        auth.initialize_auth_database()
        database_operations.initialize_database()

    @classmethod
    def tearDownClass(cls):
        # Restore logging
        logging.disable(original_logging_level)

    def setUp(self):
        # For each test method, we want a completely fresh database.
        # Since it's in-memory, re-initializing effectively clears it.
        # Closing previous connections first if any remained open (though get_db_connection should manage this)
        conn_auth = auth.get_db_connection()
        if conn_auth:
            conn_auth.close()
        conn_db_ops = database_operations.get_db_connection()
        if conn_db_ops:
            conn_db_ops.close()
            
        auth.initialize_auth_database() # Re-create tables in the in-memory DB
        database_operations.initialize_database() # Re-create tables in the in-memory DB

class TestAuth(BaseTestCase):

    def test_create_user_successful(self):
        self.assertTrue(auth.create_user('testuser', 'password123', 'admin'), "User creation should succeed.")
        # Verify user is in DB (implicitly tested by verify_user, but direct check is good)
        conn = auth.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE username = 'testuser'")
        self.assertIsNotNone(cursor.fetchone(), "User should exist in the database.")
        conn.close()

    def test_create_user_existing_username(self):
        auth.create_user('testuser', 'password123', 'admin')
        self.assertFalse(auth.create_user('testuser', 'anotherpassword', 'admin'), "Creating user with existing username should fail.")

    def test_verify_user_successful(self):
        auth.create_user('testuser', 'password123', 'admin')
        self.assertTrue(auth.verify_user('testuser', 'password123'), "User verification should succeed with correct credentials.")

    def test_verify_user_incorrect_password(self):
        auth.create_user('testuser', 'password123', 'admin')
        self.assertFalse(auth.verify_user('testuser', 'wrongpassword'), "User verification should fail with incorrect password.")

    def test_verify_user_non_existent_username(self):
        self.assertFalse(auth.verify_user('nonexistentuser', 'password123'), "User verification should fail for non-existent username.")
    
    def test_create_user_empty_credentials(self):
        self.assertFalse(auth.create_user('', 'password'), "Should not create user with empty username.")
        self.assertFalse(auth.create_user('user', ''), "Should not create user with empty password.")

    def test_verify_user_empty_credentials(self):
        self.assertFalse(auth.verify_user('', 'password'), "Should not verify with empty username.")
        self.assertFalse(auth.verify_user('user', ''), "Should not verify with empty password.")


class TestStudentOperations(BaseTestCase):
    def setUp(self):
        super().setUp() # Calls BaseTestCase.setUp to re-init DBs
        self.student1_data = {
            'student_id': 'S001', 'full_name': 'Alice Wonderland', 'enrollment_year': 2022,
            'date_of_birth': '2004-07-12', 'gender': 'Female', 'address': '123 Fantasy Lane',
            'phone_number': '555-0001', 'email': 'alice@example.com', 'status': 'active'
        }
        self.student2_data = {
            'student_id': 'S002', 'full_name': 'Bob The Builder', 'enrollment_year': 2021,
            'date_of_birth': '2003-03-10', 'gender': 'Male', 'address': '456 Tool Street',
            'phone_number': '555-0002', 'email': 'bob@example.com', 'status': 'active'
        }

    def test_add_student(self):
        student_id = database_operations.add_student(self.student1_data)
        self.assertEqual(student_id, self.student1_data['student_id'], "add_student should return the correct student_id.")
        retrieved_student = database_operations.get_student_by_id(self.student1_data['student_id'])
        self.assertIsNotNone(retrieved_student, "Student should be retrievable after adding.")
        self.assertEqual(retrieved_student['full_name'], self.student1_data['full_name'])

    def test_add_student_missing_required_fields(self):
        incomplete_data = {'full_name': 'Test', 'enrollment_year': 2023} # Missing student_id
        student_id = database_operations.add_student(incomplete_data)
        self.assertIsNone(student_id, "Adding student with missing required fields should fail.")

    def test_get_all_students_empty(self):
        students = database_operations.get_all_students()
        self.assertEqual(len(students), 0, "get_all_students should return an empty list if no students.")

    def test_get_all_students(self):
        database_operations.add_student(self.student1_data)
        database_operations.add_student(self.student2_data)
        students = database_operations.get_all_students()
        self.assertEqual(len(students), 2, "get_all_students should retrieve all added students.")
        student_ids = [s['student_id'] for s in students]
        self.assertIn(self.student1_data['student_id'], student_ids)
        self.assertIn(self.student2_data['student_id'], student_ids)

    def test_get_student_by_id_non_existent(self):
        student = database_operations.get_student_by_id('S999')
        self.assertIsNone(student, "get_student_by_id should return None for non-existent student.")

    def test_update_student(self):
        database_operations.add_student(self.student1_data)
        update_data = {'full_name': 'Alice In Chains', 'phone_number': '555-9999'}
        update_result = database_operations.update_student(self.student1_data['student_id'], update_data)
        self.assertTrue(update_result, "update_student should return True on successful update.")
        updated_student = database_operations.get_student_by_id(self.student1_data['student_id'])
        self.assertEqual(updated_student['full_name'], update_data['full_name'])
        self.assertEqual(updated_student['phone_number'], update_data['phone_number'])
        self.assertEqual(updated_student['email'], self.student1_data['email']) # Check unchanged field

    def test_update_student_non_existent(self):
        update_data = {'full_name': 'Ghost User'}
        update_result = database_operations.update_student('S999', update_data)
        self.assertFalse(update_result, "update_student should return False for non-existent student.")

    def test_update_student_no_data_change(self):
        database_operations.add_student(self.student1_data)
        # Attempt to update with the same data (or empty data)
        # The function currently returns False if rowcount is 0, which can happen if data is identical.
        # This behavior is acceptable.
        update_result = database_operations.update_student(self.student1_data['student_id'], 
                                                           {'full_name': self.student1_data['full_name']})
        self.assertFalse(update_result, "update_student should return False if no data actually changed or student not found.")

    def test_delete_student(self):
        database_operations.add_student(self.student1_data)
        delete_result = database_operations.delete_student(self.student1_data['student_id'])
        self.assertTrue(delete_result, "delete_student should return True on successful deletion.")
        self.assertIsNone(database_operations.get_student_by_id(self.student1_data['student_id']), "Student should be gone after deletion.")

    def test_delete_student_non_existent(self):
        delete_result = database_operations.delete_student('S999')
        self.assertFalse(delete_result, "delete_student should return False for non-existent student.")


class TestGradeOperations(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.student_data = {
            'student_id': 'S001', 'full_name': 'Charlie Brown', 'enrollment_year': 2020,
            'email': 'charlie@example.com', 'status': 'active'
        }
        # Add student first, as grades depend on a student existing
        self.student_id = database_operations.add_student(self.student_data)
        self.assertIsNotNone(self.student_id, "Setup: Failed to add student for grade tests.")

        self.grade1_data = {'student_id': self.student_id, 'year_level': 1, 'subject': 'Math', 'grade': 'C'}
        self.grade2_data = {'student_id': self.student_id, 'year_level': 1, 'subject': 'Art', 'grade': 'A'}

    def test_add_student_grade(self):
        grade_id = database_operations.add_student_grade(self.grade1_data)
        self.assertIsNotNone(grade_id, "add_student_grade should return a grade_id.")
        grades = database_operations.get_grades_for_student(self.student_id)
        self.assertEqual(len(grades), 1)
        self.assertEqual(grades[0]['subject'], self.grade1_data['subject'])
        self.assertEqual(grades[0]['grade_id'], grade_id)

    def test_add_grade_for_non_existent_student(self):
        invalid_grade_data = {'student_id': 'S999', 'year_level': 1, 'subject': 'Ghost Studies', 'grade': 'X'}
        grade_id = database_operations.add_student_grade(invalid_grade_data)
        self.assertIsNone(grade_id, "add_student_grade should fail for a non-existent student.")

    def test_get_grades_for_student_empty(self):
        grades = database_operations.get_grades_for_student(self.student_id)
        self.assertEqual(len(grades), 0, "Should return empty list if no grades for student.")

    def test_get_grades_for_student(self):
        database_operations.add_student_grade(self.grade1_data)
        database_operations.add_student_grade(self.grade2_data)
        grades = database_operations.get_grades_for_student(self.student_id)
        self.assertEqual(len(grades), 2)
        subjects = [g['subject'] for g in grades]
        self.assertIn(self.grade1_data['subject'], subjects)
        self.assertIn(self.grade2_data['subject'], subjects)

    def test_update_student_grade(self):
        grade_id = database_operations.add_student_grade(self.grade1_data)
        self.assertIsNotNone(grade_id)
        update_data = {'subject': 'Advanced Math', 'grade': 'A+'}
        update_result = database_operations.update_student_grade(grade_id, update_data)
        self.assertTrue(update_result, "update_student_grade should return True on success.")
        
        grades = database_operations.get_grades_for_student(self.student_id)
        updated_grade = next((g for g in grades if g['grade_id'] == grade_id), None)
        self.assertIsNotNone(updated_grade)
        self.assertEqual(updated_grade['subject'], update_data['subject'])
        self.assertEqual(updated_grade['grade'], update_data['grade'])

    def test_update_student_grade_non_existent(self):
        update_result = database_operations.update_student_grade(9999, {'grade': 'A'})
        self.assertFalse(update_result, "update_student_grade should return False for non-existent grade_id.")

    def test_delete_student_grade(self):
        grade_id = database_operations.add_student_grade(self.grade1_data)
        self.assertIsNotNone(grade_id)
        delete_result = database_operations.delete_student_grade(grade_id)
        self.assertTrue(delete_result, "delete_student_grade should return True on success.")
        grades = database_operations.get_grades_for_student(self.student_id)
        self.assertEqual(len(grades), 0, "Grade should be gone after deletion.")

    def test_delete_student_grade_non_existent(self):
        delete_result = database_operations.delete_student_grade(9999)
        self.assertFalse(delete_result, "delete_student_grade should return False for non-existent grade_id.")

    def test_on_delete_cascade_student_grades(self):
        g1_id = database_operations.add_student_grade(self.grade1_data)
        g2_id = database_operations.add_student_grade(self.grade2_data)
        self.assertIsNotNone(g1_id)
        self.assertIsNotNone(g2_id)
        
        # Verify grades exist
        grades_before_delete = database_operations.get_grades_for_student(self.student_id)
        self.assertEqual(len(grades_before_delete), 2, "Two grades should exist before student deletion.")

        # Delete the student
        delete_student_result = database_operations.delete_student(self.student_id)
        self.assertTrue(delete_student_result, "Student deletion should be successful.")

        # Verify grades associated with the student are also deleted
        grades_after_delete = database_operations.get_grades_for_student(self.student_id)
        self.assertEqual(len(grades_after_delete), 0, "Grades should be deleted due to ON DELETE CASCADE when student is deleted.")
        
        # Also check if student is gone
        self.assertIsNone(database_operations.get_student_by_id(self.student_id))


class TestGraduatedStudent(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.grad_student_data = {
            'student_id': 'S_GRAD', 'full_name': 'Grace Hopper', 'enrollment_year': 2018,
            'graduation_year': 2022, 'status': 'graduated', 'email': 'grace@example.com'
        }
        self.active_student_data = {
            'student_id': 'S_ACTIVE', 'full_name': 'Active Andy', 'enrollment_year': 2023,
            'status': 'active', 'email': 'andy@example.com'
        }
        
        # Add students
        self.grad_student_id = database_operations.add_student(self.grad_student_data)
        self.active_student_id = database_operations.add_student(self.active_student_data)
        self.assertIsNotNone(self.grad_student_id, "Setup: Failed to add graduated student.")
        self.assertIsNotNone(self.active_student_id, "Setup: Failed to add active student.")

        # Add grades for graduated student
        self.grad_grade1 = {'student_id': self.grad_student_id, 'year_level': 4, 'subject': 'Compilers', 'grade': 'A+'}
        self.grad_grade2 = {'student_id': self.grad_student_id, 'year_level': 4, 'subject': 'Algorithms', 'grade': 'A'}
        database_operations.add_student_grade(self.grad_grade1)
        database_operations.add_student_grade(self.grad_grade2)

    def test_get_graduated_student_record_successful(self):
        record = database_operations.get_graduated_student_record(self.grad_student_id)
        self.assertIsNotNone(record, "Should retrieve record for a graduated student.")
        self.assertIn('details', record)
        self.assertIn('grades', record)
        self.assertEqual(record['details']['student_id'], self.grad_student_id)
        self.assertEqual(record['details']['status'], 'graduated')
        self.assertEqual(len(record['grades']), 2)
        grade_subjects = [g['subject'] for g in record['grades']]
        self.assertIn('Compilers', grade_subjects)
        self.assertIn('Algorithms', grade_subjects)

    def test_get_graduated_student_record_for_active_student(self):
        record = database_operations.get_graduated_student_record(self.active_student_id)
        self.assertIsNone(record, "Should return None for an active (non-graduated) student.")

    def test_get_graduated_student_record_for_non_existent_student(self):
        record = database_operations.get_graduated_student_record('S_NONEXIST')
        self.assertIsNone(record, "Should return None for a non-existent student.")


if __name__ == '__main__':
    # You can run the tests from the command line using:
    # python -m unittest test_backend.py
    # Or, if test_backend.py is executable:
    # ./test_backend.py
    unittest.main(verbosity=2)
