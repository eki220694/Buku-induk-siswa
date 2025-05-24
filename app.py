from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from functools import wraps # For login_required decorator

# Import user-defined modules
import auth
import database_operations as db_ops # Import with an alias

# Initialize Flask App
app = Flask(__name__)

# Secret Key for session management
# IMPORTANT: Change this to a random, secure value for production!
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'a_very_secure_and_random_secret_key_123!')

# --- Database and Default User Initialization ---
def initialize_app_data():
    """Initializes database tables and creates a default admin user if none exist."""
    with app.app_context():
        # Initialize main database tables (students, grades)
        db_ops.initialize_database()
        # Initialize authentication database table (users)
        auth.initialize_auth_database()
        
        # Create a default admin user if no users exist
        if auth.get_user_count() == 0:
            # In a real app, get password from env var or secure config
            default_admin_username = os.environ.get('ADMIN_USER', 'admin')
            default_admin_password = os.environ.get('ADMIN_PASS', 'password') # Ensure this is strong and not default in prod
            
            if auth.create_user(default_admin_username, default_admin_password, role='admin'):
                app.logger.info(f"Default admin user '{default_admin_username}' created with the specified password.")
            else:
                app.logger.error(f"Failed to create default admin user '{default_admin_username}'.")
        else:
            app.logger.info("User table is not empty. Skipping default admin creation.")

# Call initialization (this will run when the app module is first imported/run)
initialize_app_data()


# --- Login Required Decorator ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please log in to access this page.', 'warning')
            # Store the attempted URL in 'next' query parameter
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


# --- Routes ---
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session: # If already logged in, redirect to dashboard
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Both username and password are required.', 'error')
            return render_template('login.html'), 400

        if auth.verify_user(username, password):
            session['username'] = username
            # session.permanent = True # Optional: make session persistent for some time
            flash('Login successful!', 'success')
            
            next_url = request.args.get('next') # For redirecting after login if 'next' is present
            if next_url:
                return redirect(next_url)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
            return render_template('login.html'), 401 # Unauthorized
            
    return render_template('login.html')

@app.route('/logout')
@login_required # Ensures only logged-in users can access logout
def logout():
    logged_out_user = session.pop('username', None)
    # session.clear() # Use this if you want to clear everything from session
    if logged_out_user:
        flash(f'You have been successfully logged out, {logged_out_user}.', 'success')
    else: # Should not happen if @login_required works
        flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=session.get('username'))

@app.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    if request.method == 'POST':
        # Retrieve student details from form
        student_data = {
            'student_id': request.form.get('student_id'),
            'full_name': request.form.get('full_name'),
            'date_of_birth': request.form.get('date_of_birth') if request.form.get('date_of_birth') else None,
            'gender': request.form.get('gender') if request.form.get('gender') else None,
            'address': request.form.get('address') if request.form.get('address') else None,
            'phone_number': request.form.get('phone_number') if request.form.get('phone_number') else None,
            'email': request.form.get('email') if request.form.get('email') else None,
            'enrollment_year': request.form.get('enrollment_year') if request.form.get('enrollment_year') else None,
            # status will default to 'active' in the DB
        }

        # Basic validation
        if not student_data['student_id'] or not student_data['full_name']:
            flash('Student ID and Full Name are required.', 'error')
            return render_template('add_student.html', student=student_data) # Pass current data back

        # Convert enrollment_year to int if provided, otherwise None
        if student_data['enrollment_year']:
            try:
                student_data['enrollment_year'] = int(student_data['enrollment_year'])
            except ValueError:
                flash('Enrollment Year must be a valid number.', 'error')
                return render_template('add_student.html', student=student_data)
        
        # Attempt to add student
        # db_ops.add_student is expected to handle None for optional fields appropriately
        new_student_id = db_ops.add_student(student_data) 

        if new_student_id:
            flash(f"Student {student_data['full_name']} (ID: {new_student_id}) added successfully!", 'success')
            
            # Process initial grades (example for 2 sets of grade inputs)
            for i in range(1, 3): # For grade inputs 1 and 2
                year_level_str = request.form.get(f'year_level_{i}')
                subject = request.form.get(f'subject_{i}')
                grade_value = request.form.get(f'grade_{i}')

                # Only add if all parts of a grade are present and year_level is a number
                if year_level_str and subject and grade_value:
                    try:
                        year_level = int(year_level_str)
                        grade_data = {
                            'student_id': new_student_id, # Use the returned student_id
                            'year_level': year_level,
                            'subject': subject,
                            'grade': grade_value
                        }
                        grade_added_id = db_ops.add_student_grade(grade_data)
                        if grade_added_id:
                             flash(f"Added grade for {subject} (Year {year_level}).", 'info')
                        else:
                             flash(f"Failed to add grade for {subject} (Year {year_level}). Student ID might be invalid or DB error.", 'error')
                    except ValueError:
                        flash(f"Year Level for grade entry {i} must be a number. Grade not saved.", 'warning')
                elif year_level_str or subject or grade_value: # Partial grade info
                    flash(f"Partial grade information for entry {i} was not saved. All fields (Year, Subject, Grade) are required and Year must be a number.", 'warning')
                            
            return redirect(url_for('view_students')) # Redirect to student list after success
        else:
            flash('Error adding student. Student ID might already exist or other database error.', 'error')
            # Ensure student_data is passed back to re-populate the form
            return render_template('add_student.html', student=student_data) 

    return render_template('add_student.html', student=None) # Pass student=None for GET request

@app.route('/students')
@login_required
def view_students():
    search_term = request.args.get('search_term', '').strip()
    search_by = request.args.get('search_by', 'name') # Default search by name

    if search_term:
        students_list = db_ops.search_students(search_term=search_term, search_by=search_by)
        if not students_list:
            flash(f"No students found matching '{search_term}' by {search_by.capitalize()}. Please try different terms or criteria.", 'warning')
        else:
            flash(f"Displaying students matching '{search_term}' by {search_by.capitalize()}.", 'info')
    else:
        students_list = db_ops.get_all_students()
        if not students_list and not search_term: # Only show "no students added yet" if it's not a failed search
            flash("No students have been added yet. You can add one using the dashboard.", "info")
            
    return render_template('view_students.html', students=students_list, search_term=search_term, search_by=search_by)

@app.route('/student/<student_id>', methods=['GET', 'POST'])
@login_required
def edit_student(student_id):
    if request.method == 'POST':
        # Update student details
        updated_student_data = {
            'full_name': request.form.get('full_name'),
            'date_of_birth': request.form.get('date_of_birth') if request.form.get('date_of_birth') else None,
            'gender': request.form.get('gender') if request.form.get('gender') else None,
            'address': request.form.get('address') if request.form.get('address') else None,
            'phone_number': request.form.get('phone_number') if request.form.get('phone_number') else None,
            'email': request.form.get('email') if request.form.get('email') else None,
            'enrollment_year': request.form.get('enrollment_year') if request.form.get('enrollment_year') else None,
            'status': request.form.get('status'),
            'graduation_year': request.form.get('graduation_year') if request.form.get('graduation_year') else None,
        }

        # Basic validation for full_name
        if not updated_student_data['full_name']:
            flash('Full Name is required.', 'error')
            # Need to reload student data for the template if validation fails
            student_info = db_ops.get_student_details_with_grades(student_id)
            if not student_info:
                flash(f"Student with ID {student_id} not found.", 'error')
                return redirect(url_for('view_students'))
            return render_template('edit_student.html', student=student_info, student_id_from_route=student_id)

        # Convert years to int if provided, otherwise None
        if updated_student_data['enrollment_year']:
            try:
                updated_student_data['enrollment_year'] = int(updated_student_data['enrollment_year'])
            except ValueError:
                flash('Enrollment Year must be a valid number.', 'error')
                student_info = db_ops.get_student_details_with_grades(student_id)
                return render_template('edit_student.html', student=student_info, student_id_from_route=student_id)

        if updated_student_data['graduation_year']:
            try:
                updated_student_data['graduation_year'] = int(updated_student_data['graduation_year'])
            except ValueError:
                flash('Graduation Year must be a valid number.', 'error')
                student_info = db_ops.get_student_details_with_grades(student_id)
                return render_template('edit_student.html', student=student_info, student_id_from_route=student_id)


        if db_ops.update_student(student_id, updated_student_data):
            flash('Student details updated successfully!', 'success')
        else:
            flash('Error updating student details. Student ID might not exist or data was unchanged.', 'error')

        # Process new grade additions
        for i in range(1, 3): # For new_grade_1 and new_grade_2
            year_level_str = request.form.get(f'new_year_level_{i}')
            subject = request.form.get(f'new_subject_{i}')
            grade_value = request.form.get(f'new_grade_{i}')

            if year_level_str and subject and grade_value: # Only if all parts of a new grade are present
                try:
                    year_level = int(year_level_str)
                    new_grade_data = {
                        'student_id': student_id,
                        'year_level': year_level,
                        'subject': subject,
                        'grade': grade_value
                    }
                    grade_added_id = db_ops.add_student_grade(new_grade_data)
                    if grade_added_id:
                        flash(f"Added new grade for {subject} (Year {year_level}).", 'info')
                    else:
                        flash(f"Failed to add new grade for {subject} (Year {year_level}).", 'error')
                except ValueError:
                    flash(f"Year Level for new grade entry {i} must be a number. Grade not saved.", 'warning')
            elif year_level_str or subject or grade_value:
                 flash(f"Partial information for new grade entry {i} was not saved. All fields are required.", 'warning')


        return redirect(url_for('edit_student', student_id=student_id))

    # GET request logic
    student_info = db_ops.get_student_details_with_grades(student_id)
    if not student_info or not student_info['details']:
        flash(f"Student with ID {student_id} not found.", 'error')
        return redirect(url_for('view_students'))
    
    return render_template('edit_student.html', student=student_info, student_id_from_route=student_id)

@app.route('/grade/<int:grade_id>/delete/<student_id_for_redirect>')
@login_required
def delete_grade(grade_id, student_id_for_redirect):
    if db_ops.delete_student_grade(grade_id):
        flash('Grade deleted successfully!', 'success')
    else:
        flash('Error deleting grade. It might have already been deleted or does not exist.', 'error')
    return redirect(url_for('edit_student', student_id=student_id_for_redirect))

@app.route('/student/<student_id>/delete')
@login_required
def delete_student(student_id):
    # Fetch student name before deleting for the flash message
    student_details = db_ops.get_student_by_id(student_id)
    student_name = student_details['full_name'] if student_details else f"ID {student_id}"
    
    if db_ops.delete_student(student_id):
        flash(f"Student record for {student_name} and all associated grades deleted successfully!", 'success')
        return redirect(url_for('view_students'))
    else:
        flash(f"Error deleting student {student_name}. Student might not exist.", 'error')
        return redirect(url_for('view_students'))


@app.route('/graduated_access') # This one is public, no @login_required
def graduated_student_search():
    student_id_query = request.args.get('student_id', '').strip()
    student_data_result = None
    message_to_display = None 

    if student_id_query:
        # Using the existing get_graduated_student_record function
        student_data_result = db_ops.get_graduated_student_record(student_id=student_id_query)
        if not student_data_result:
            message_to_display = "Record not found. Please ensure your Student ID is correct and that you have graduated."
        # No specific success message here; the presence of data is the success indication.
    # else:
        # Optional: Could add a message if the page is loaded without a query,
        # but the template already handles this by showing "Enter your student ID..."
        # message_to_display = "Please enter your Student ID to view your record."

    return render_template('graduated_access.html', 
                           student_data=student_data_result, 
                           searched_id=student_id_query,
                           message=message_to_display)


# Example of another protected route (profile) - can be kept or removed if not central to current task
@app.route('/profile')
@login_required
def profile():
    return f"""
    <h1>User Profile: {session.get('username')}</h1>
    <p>This is your profile page.</p>
    <p><a href='{url_for('dashboard')}'>Dashboard</a> | <a href='{url_for('logout')}'>Logout</a></p>
    """

if __name__ == '__main__':
    # Note: In a production environment, use a WSGI server like Gunicorn or uWSGI
    # The debug mode should be disabled in production.
    # The host '0.0.0.0' makes it accessible from network, useful for containers/VMs
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5001)))
