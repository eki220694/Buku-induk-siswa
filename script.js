// Firebase SDK version 9.x
import { initializeApp } from "https://www.gstatic.com/firebasejs/9.22.1/firebase-app.js";
// Import Firestore (DB)
// Added getDocs, query, orderBy, doc, deleteDoc, updateDoc for current and future steps
import { getFirestore, collection, addDoc, serverTimestamp, getDocs, query, orderBy, where, doc, deleteDoc, updateDoc } from "https://www.gstatic.com/firebasejs/9.22.1/firebase-firestore.js";
// Import Auth functions
import { 
    getAuth,
    createUserWithEmailAndPassword, 
    signInWithEmailAndPassword, 
    signOut, 
    onAuthStateChanged 
} from "https://www.gstatic.com/firebasejs/9.22.1/firebase-auth.js";


// IMPORTANT: TODO: User must replace these with their actual Firebase project configuration!
const firebaseConfig = {
  apiKey: "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX_PLACEHOLDER",
  authDomain: "your-project-id-placeholder.firebaseapp.com",
  projectId: "your-project-id-placeholder",
  storageBucket: "your-project-id-placeholder.appspot.com",
  messagingSenderId: "123456789012_PLACEHOLDER",
  appId: "1:123456789012:web:abcdef1234567890abcdef_PLACEHOLDER",
  measurementId: "G-XXXXXXXXXX_PLACEHOLDER" // Optional, but often included
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app); // Firebase Authentication instance. This line should be here.
const db = getFirestore(app); // Firestore Database instance

// Log to console to confirm initialization (optional)
console.log("Firebase App initialized. Auth and Firestore services ready.");

// --- DOM Element References ---
const emailInput = document.getElementById('auth-email');
const passwordInput = document.getElementById('auth-password');
const btnSignup = document.getElementById('btn-signup');
const btnLogin = document.getElementById('btn-login');
const btnLogout = document.getElementById('btn-logout');
const authStatusMessage = document.getElementById('auth-status-message');
const authErrorMessage = document.getElementById('auth-error-message');
const userDisplayEmail = document.getElementById('user-display-email');
const authSection = document.getElementById('auth-section');
const appSection = document.getElementById('app-section');

// --- Add Student Form Element References (will be populated when user logs in) ---
let formAddStudent;
let addStudentFeedback;
let sIdInput, sFullnameInput, sDobInput, sGenderInput, sAddressInput, sPhoneInput, sEmailInput, sEnrollmentYearInput, sStatusInput, sGraduationYearInput;

// --- View Student Elements ---
let btnRefreshStudents;
let studentTableContainer;
let viewStudentsFeedback;

// --- Edit Student Elements ---
let editStudentModule;
let formEditStudent;
let editDocIdInput;
let editStudentIdDisplay;
let editSFullnameInput, editSDobInput, editSGenderInput, editSAddressInput, editSPhoneInput, editSEmailInput, editSEnrollmentYearInput, editSStatusInput, editSGraduationYearInput;
let btnCancelEditStudent;
let editStudentFeedback;

// --- Graduated Student Access Elements ---
let formGraduatedSearch;
let gradStudentIdInput;
let graduatedStudentInfoDisplay;
let graduatedAccessModuleFeedback;


// --- Event Listeners ---

// Sign Up Button
if (btnSignup) {
    btnSignup.addEventListener('click', async () => {
        const email = emailInput.value;
        const password = passwordInput.value;
        if(authErrorMessage) {
            authErrorMessage.textContent = ''; 
            authErrorMessage.className = 'feedback-message'; // Reset class
        }
        try {
            const userCredential = await createUserWithEmailAndPassword(auth, email, password);
            console.log("Admin signed up:", userCredential.user);
            // User will be automatically logged in, onAuthStateChanged will handle UI
        } catch (error) {
            console.error("Error signing up:", error.message);
            if(authErrorMessage) {
                authErrorMessage.textContent = `Sign Up Error: ${error.message}`;
                authErrorMessage.className = 'feedback-message feedback-error';
            }
        }
    });
} else {
    console.error("Sign Up button not found.");
}


// Login Button
if (btnLogin) {
    btnLogin.addEventListener('click', async () => {
        const email = emailInput.value;
        const password = passwordInput.value;
        if(authErrorMessage) {
            authErrorMessage.textContent = '';
            authErrorMessage.className = 'feedback-message';
        }
        try {
            const userCredential = await signInWithEmailAndPassword(auth, email, password);
            console.log("Admin logged in:", userCredential.user);
            // onAuthStateChanged will handle UI
        } catch (error) {
            console.error("Error logging in:", error.message);
            if(authErrorMessage) {
                authErrorMessage.textContent = `Login Error: ${error.message}`;
                authErrorMessage.className = 'feedback-message feedback-error';
            }
        }
    });
} else {
    console.error("Login button not found.");
}

// Logout Button
if (btnLogout) {
    btnLogout.addEventListener('click', async () => {
        if(authErrorMessage) {
            authErrorMessage.textContent = '';
            authErrorMessage.className = 'feedback-message';
        }
        try {
            await signOut(auth);
            console.log("User logged out");
            // onAuthStateChanged will handle UI
        } catch (error) {
            console.error("Error logging out:", error.message);
            if(authErrorMessage) {
                authErrorMessage.textContent = `Logout Error: ${error.message}`;
                authErrorMessage.className = 'feedback-message feedback-error';
            }
        }
    });
} else {
    console.error("Logout button not found.");
}


// --- Auth State Observer ---
onAuthStateChanged(auth, (user) => {
    if (user) {
        // User is signed in
        console.log("Auth state changed: User is signed in - ", user.email);
        if (authStatusMessage) authStatusMessage.textContent = `Logged in as: ${user.email}`;
        if (userDisplayEmail) userDisplayEmail.textContent = user.email;
        if (appSection) appSection.style.display = 'block'; // Show main app content
        if (btnLogout) btnLogout.style.display = 'inline-block'; // Show logout button
        if (authSection) authSection.style.display = 'none'; // Hide the entire auth form section

        // Initialize Add Student Form elements & listener now that user is logged in and #app-section is visible
        formAddStudent = document.getElementById('form-add-student');
        addStudentFeedback = document.getElementById('add-student-feedback');
        sIdInput = document.getElementById('s-id');
        sFullnameInput = document.getElementById('s-fullname');
        sDobInput = document.getElementById('s-dob');
        sGenderInput = document.getElementById('s-gender');
        sAddressInput = document.getElementById('s-address');
        sPhoneInput = document.getElementById('s-phone');
        sEmailInput = document.getElementById('s-email');
        sEnrollmentYearInput = document.getElementById('s-enrollmentyear');
        sStatusInput = document.getElementById('s-status');
        sGraduationYearInput = document.getElementById('s-graduationyear');

        // Initialize View Student elements
        btnRefreshStudents = document.getElementById('btn-refresh-students');
        studentTableContainer = document.getElementById('student-table-container');
        viewStudentsFeedback = document.getElementById('view-students-feedback');

        // Initialize Edit Student elements
        editStudentModule = document.getElementById('edit-student-module');
        formEditStudent = document.getElementById('form-edit-student');
        editDocIdInput = document.getElementById('edit-doc-id');
        editStudentIdDisplay = document.getElementById('edit-s-id-display');
        editSFullnameInput = document.getElementById('edit-s-fullname');
        editSDobInput = document.getElementById('edit-s-dob');
        editSGenderInput = document.getElementById('edit-s-gender');
        editSAddressInput = document.getElementById('edit-s-address');
        editSPhoneInput = document.getElementById('edit-s-phone');
        editSEmailInput = document.getElementById('edit-s-email');
        editSEnrollmentYearInput = document.getElementById('edit-s-enrollmentyear');
        editSStatusInput = document.getElementById('edit-s-status');
        editSGraduationYearInput = document.getElementById('edit-s-graduationyear');
        btnCancelEditStudent = document.getElementById('btn-cancel-edit-student');
        editStudentFeedback = document.getElementById('edit-student-feedback');


        if (formAddStudent) {
            formAddStudent.addEventListener('submit', async (e) => {
                e.preventDefault(); // Prevent page reload
                if(addStudentFeedback) {
                    addStudentFeedback.textContent = ''; 
                    addStudentFeedback.className = 'feedback-message';
                }

                const currentUser = auth.currentUser;
                if (!currentUser) {
                    if(addStudentFeedback) {
                        addStudentFeedback.textContent = 'Error: You must be logged in to add a student.';
                        addStudentFeedback.className = 'feedback-message feedback-error';
                    }
                    return;
                }

                // Collect data from form fields
                const studentData = {
                    studentId: sIdInput.value,
                    fullName: sFullnameInput.value,
                    dateOfBirth: sDobInput.value || null, // Ensure empty string becomes null
                    gender: sGenderInput.value,
                    address: sAddressInput.value || null,
                    phoneNumber: sPhoneInput.value || null,
                    email: sEmailInput.value || null,
                    enrollmentYear: sEnrollmentYearInput.value ? parseInt(sEnrollmentYearInput.value) : null,
                    status: sStatusInput.value,
                    graduationYear: sGraduationYearInput.value ? parseInt(sGraduationYearInput.value) : null,
                    createdBy: currentUser.uid, // Link to the admin who created it
                    createdAt: serverTimestamp() // Firestore server timestamp
                };

                // Basic Validation
                if (!studentData.studentId || !studentData.fullName) {
                    if(addStudentFeedback) {
                        addStudentFeedback.textContent = 'Student ID and Full Name are required.';
                        addStudentFeedback.className = 'feedback-message feedback-error';
                    }
                    return;
                }

                try {
                    const docRef = await addDoc(collection(db, "students"), studentData);
                    console.log("Student document written with ID: ", docRef.id);
                    if(addStudentFeedback) {
                        addStudentFeedback.textContent = `Student ${studentData.fullName} (ID: ${studentData.studentId}) added successfully!`;
                        addStudentFeedback.className = 'feedback-message feedback-success';
                    }
                    formAddStudent.reset(); // Clear the form
                } catch (error) {
                    console.error("Error adding student document: ", error);
                    if(addStudentFeedback) {
                        addStudentFeedback.textContent = `Error adding student: ${error.message}`;
                        addStudentFeedback.className = 'feedback-message feedback-error';
                    }
                }
            });
        } else {
            console.error("Add Student Form not found after login.");
        }

        // Event Listener for Refresh Student List button
        if (btnRefreshStudents) {
            btnRefreshStudents.addEventListener('click', loadStudents);
        } else {
            console.error("Refresh Student List button not found.");
        }

        // Event Delegation for Edit and Delete buttons in student table
        if (studentTableContainer) {
            // Check if listener already attached to prevent duplicates if onAuthStateChanged fires multiple times
            if (!studentTableContainer.dataset.listenerAttached) {
                studentTableContainer.addEventListener('click', (e) => {
                    if (e.target.classList.contains('btn-edit-student')) {
                        const studentDocId = e.target.getAttribute('data-id');
                        populateEditForm(studentDocId); 
                    } else if (e.target.classList.contains('btn-delete-student')) {
                        const studentDocId = e.target.getAttribute('data-id');
                        deleteStudent(studentDocId); 
                    }
                });
                studentTableContainer.dataset.listenerAttached = 'true'; // Mark listener as attached
            }
        } else {
            console.error("Student table container not found for edit/delete button delegation.");
        }

        // Event Listener for Cancel Edit button
        if (btnCancelEditStudent) {
            btnCancelEditStudent.addEventListener('click', () => {
                if(editStudentModule) editStudentModule.style.display = 'none';
                if(formEditStudent) formEditStudent.reset();
                // Show other relevant modules, e.g., view and create
                const createModule = document.getElementById('create-student-module');
                const viewModule = document.getElementById('view-students-module');
                if(createModule) createModule.style.display = 'block';
                if(viewModule) viewModule.style.display = 'block';
            });
        } else {
            console.error("Cancel Edit button not found.");
        }
        
        // Event Listener for Edit Form Submission
        if (formEditStudent) {
            formEditStudent.addEventListener('submit', async (e) => {
                e.preventDefault();
                const studentDocId = editDocIdInput.value;
                if (!studentDocId) {
                    if(editStudentFeedback) {
                        editStudentFeedback.textContent = "Error: No student record selected for update.";
                        editStudentFeedback.className = 'feedback-message feedback-error';
                    }
                    return;
                }

                const updatedData = {
                    fullName: editSFullnameInput.value,
                    dateOfBirth: editSDobInput.value || null,
                    gender: editSGenderInput.value,
                    address: editSAddressInput.value || null,
                    phoneNumber: editSPhoneInput.value || null,
                    email: editSEmailInput.value || null,
                    enrollmentYear: editSEnrollmentYearInput.value ? parseInt(editSEnrollmentYearInput.value) : null,
                    status: editSStatusInput.value,
                    graduationYear: editSGraduationYearInput.value ? parseInt(editSGraduationYearInput.value) : null,
                    updatedAt: serverTimestamp() // Add timestamp for update
                };
                // Note: studentId (original ID from studentData.studentId) is not updated.

                try {
                    const studentRef = doc(db, "students", studentDocId);
                    await updateDoc(studentRef, updatedData);
                    if(editStudentFeedback) {
                        editStudentFeedback.textContent = "Student record updated successfully!";
                        editStudentFeedback.className = 'feedback-message feedback-success';
                    }
                    if(formEditStudent) formEditStudent.reset();
                    if(editStudentModule) editStudentModule.style.display = 'none';
                    
                    const createModule = document.getElementById('create-student-module');
                    const viewModule = document.getElementById('view-students-module');
                    if(createModule) createModule.style.display = 'block';
                    if(viewModule) viewModule.style.display = 'block';
                    
                    loadStudents(); // Refresh the student list
                } catch (error) {
                    console.error("Error updating student:", error);
                    if(editStudentFeedback) {
                        editStudentFeedback.textContent = "Error updating record: " + error.message;
                        editStudentFeedback.className = 'feedback-message feedback-error';
                    }
                }
            });
        } else {
             console.error("Edit Student Form not found.");
        }


        // Initial load of students when user logs in
        loadStudents(); 

    } else {
        // User is signed out
        console.log("Auth state changed: User is signed out.");
        if (authStatusMessage) authStatusMessage.textContent = 'Current Status: Logged Out';
        if (userDisplayEmail) userDisplayEmail.textContent = '';
        if (appSection) appSection.style.display = 'none'; // Hide main app content
        if (btnLogout) btnLogout.style.display = 'none'; // Hide logout button
        if (authSection) authSection.style.display = 'block'; // Show auth form section
        if (emailInput) emailInput.value = ''; // Clear email input on logout
        if (passwordInput) passwordInput.value = ''; // Clear password input on logout
        if (authErrorMessage) {
            authErrorMessage.textContent = ''; // Clear any previous error messages
            authErrorMessage.className = 'feedback-message';
        }
        
        // If formAddStudent was previously initialized, its event listener will be inactive
        // because the form itself is hidden. No need to explicitly remove if the parent is hidden.
    }
});

// --- Firestore Data Functions ---

// Initialize Graduated Student Search Form (called once when script loads)
function initializeGraduatedStudentSearch() {
    formGraduatedSearch = document.getElementById('form-graduated-search');
    gradStudentIdInput = document.getElementById('grad-student-id-input');
    graduatedStudentInfoDisplay = document.getElementById('graduated-student-info-display');
    graduatedAccessModuleFeedback = document.getElementById('graduated-access-module-feedback');

    if (formGraduatedSearch) {
        formGraduatedSearch.addEventListener('submit', async (e) => {
            e.preventDefault();
            const studentIdToSearch = gradStudentIdInput.value.trim();
            graduatedStudentInfoDisplay.innerHTML = ''; // Clear previous results
            
            if (!graduatedAccessModuleFeedback) {
                console.error("Graduated access feedback element not found.");
                return;
            }
            graduatedAccessModuleFeedback.textContent = 'Searching...';
            graduatedAccessModuleFeedback.className = 'feedback-message feedback-info';


            if (!studentIdToSearch) {
                graduatedAccessModuleFeedback.textContent = 'Please enter a Student ID.';
                graduatedAccessModuleFeedback.className = 'feedback-message feedback-warning';
                return;
            }

            try {
                const q = query(
                    collection(db, "students"),
                    where("studentId", "==", studentIdToSearch),
                    where("status", "==", "graduated")
                );
                const querySnapshot = await getDocs(q);

                if (querySnapshot.empty) {
                    graduatedAccessModuleFeedback.textContent = 'No record found for this Student ID, or student has not graduated.';
                    graduatedAccessModuleFeedback.className = 'feedback-message feedback-warning'; // Changed from orange to warning class
                } else {
                    const studentDoc = querySnapshot.docs[0]; // Assuming studentId is unique
                    const studentData = studentDoc.data();
                    
                    let displayHtml = `<h4>Record for: ${studentData.fullName}</h4>`;
                    displayHtml += `<p><strong>Student ID:</strong> ${studentData.studentId}</p>`;
                    displayHtml += `<p><strong>Full Name:</strong> ${studentData.fullName}</p>`;
                    displayHtml += `<p><strong>Enrollment Year:</strong> ${studentData.enrollmentYear || 'N/A'}</p>`;
                    displayHtml += `<p><strong>Graduation Year:</strong> ${studentData.graduationYear || 'N/A'}</p>`;
                    displayHtml += `<p><strong>Status:</strong> ${studentData.status}</p>`;
                    // Add other fields as needed, e.g., DOB, Gender, but be mindful of privacy.
                    // For this example, we'll stick to less sensitive info for public view.

                    graduatedStudentInfoDisplay.innerHTML = displayHtml;
                    graduatedAccessModuleFeedback.textContent = 'Record found.';
                    graduatedAccessModuleFeedback.className = 'feedback-message feedback-success';
                }
            } catch (error) {
                console.error("Error searching graduated student:", error);
                graduatedAccessModuleFeedback.textContent = `Error: ${error.message}`;
                graduatedAccessModuleFeedback.className = 'feedback-message feedback-error';
            }
        });
    } else {
        console.error("Graduated student search form not found.");
    }
}

// Call the initialization for the graduated student search form when the script loads
initializeGraduatedStudentSearch();


// Delete Student Function
async function deleteStudent(studentDocId) {
    if (!confirm('Are you sure you want to delete this student record? This action cannot be undone.')) {
        return; // Abort if user cancels
    }

    const feedbackEl = document.getElementById('view-students-feedback'); 
    if (!feedbackEl) {
        console.error('Feedback element not found for delete status.');
        return;
    }

    feedbackEl.textContent = 'Deleting student record...';
    feedbackEl.className = 'feedback-message feedback-warning'; 

    try {
        await deleteDoc(doc(db, "students", studentDocId));
        feedbackEl.textContent = 'Student record deleted successfully.';
        feedbackEl.className = 'feedback-message feedback-success';
        console.log('Student deleted:', studentDocId);
        loadStudents(); // Refresh the list of students
    } catch (error) {
        console.error('Error deleting student:', error);
        feedbackEl.textContent = `Error deleting student: ${error.message}`;
        feedbackEl.className = 'feedback-message feedback-error';
    }
}


// Populate Edit Form Function
async function populateEditForm(studentDocId) {
    if(editStudentFeedback) {
        editStudentFeedback.textContent = '';
        editStudentFeedback.className = 'feedback-message'; 
    }
    try {
        const studentRef = doc(db, "students", studentDocId);
        const docSnap = await getDoc(studentRef);

        if (docSnap.exists()) {
            const data = docSnap.data();
            if(editDocIdInput) editDocIdInput.value = studentDocId; 
            if(editStudentIdDisplay) editStudentIdDisplay.textContent = data.studentId; 
            
            if(editSFullnameInput) editSFullnameInput.value = data.fullName || '';
            if(editSDobInput) editSDobInput.value = data.dateOfBirth || '';
            if(editSGenderInput) editSGenderInput.value = data.gender || 'Male';
            if(editSAddressInput) editSAddressInput.value = data.address || '';
            if(editSPhoneInput) editSPhoneInput.value = data.phoneNumber || '';
            if(editSEmailInput) editSEmailInput.value = data.email || '';
            if(editSEnrollmentYearInput) editSEnrollmentYearInput.value = data.enrollmentYear || '';
            if(editSStatusInput) editSStatusInput.value = data.status || 'active';
            if(editSGraduationYearInput) editSGraduationYearInput.value = data.graduationYear || '';

            // Show edit form, hide others
            const createModule = document.getElementById('create-student-module');
            const viewModule = document.getElementById('view-students-module');
            if(editStudentModule) editStudentModule.style.display = 'block';
            if(createModule) createModule.style.display = 'none';
            if(viewModule) viewModule.style.display = 'none';
        } else {
            console.log("No such student document for editing!");
            if(editStudentFeedback) {
                 editStudentFeedback.textContent = "Student record not found.";
                 editStudentFeedback.className = 'feedback-message feedback-error';
            }
        }
    } catch (error) {
        console.error("Error fetching student for edit:", error);
        if(editStudentFeedback) {
            editStudentFeedback.textContent = "Error fetching student data: " + error.message;
            editStudentFeedback.className = 'feedback-message feedback-error';
        }
    }
}


// Render Students Table Function
function renderStudentsTable(studentsArray) {
    if (!studentTableContainer) {
        console.error("Student table container not found for rendering.");
        return;
    }
    studentTableContainer.innerHTML = ''; // Clear previous table
    
    if (!viewStudentsFeedback) {
        console.error("View students feedback element not found.");
    } else {
        viewStudentsFeedback.textContent = ''; // Clear previous feedback
        viewStudentsFeedback.className = 'feedback-message'; 
    }


    if (studentsArray.length === 0) {
        if (viewStudentsFeedback) {
            viewStudentsFeedback.textContent = 'No student records found.';
            viewStudentsFeedback.className = 'feedback-message feedback-info';
        }
        return;
    }

    const table = document.createElement('table');
    // Removed inline styles, should be handled by style.css

    // Create table header
    const thead = table.createTHead();
    const headerRow = thead.insertRow();
    const headers = ['Student ID', 'Full Name', 'Email', 'Status', 'Enrollment Year', 'Actions'];
    headers.forEach(text => {
        const th = document.createElement('th');
        th.textContent = text;
        headerRow.appendChild(th);
    });

    // Create table body
    const tbody = table.createTBody();
    studentsArray.forEach(student => {
        const row = tbody.insertRow();
        row.insertCell().textContent = student.data.studentId || 'N/A';
        row.insertCell().textContent = student.data.fullName || 'N/A';
        row.insertCell().textContent = student.data.email || 'N/A';
        row.insertCell().textContent = student.data.status || 'N/A';
        row.insertCell().textContent = student.data.enrollmentYear || 'N/A';
        
        const actionsCell = row.insertCell();
        const editButton = document.createElement('button');
        editButton.textContent = 'Edit';
        editButton.setAttribute('data-id', student.id); // Store Firestore doc ID
        editButton.classList.add('btn-edit-student', 'btn-sm'); // Added btn-sm
        actionsCell.appendChild(editButton);

        const deleteButton = document.createElement('button');
        deleteButton.textContent = 'Delete';
        deleteButton.setAttribute('data-id', student.id);
        deleteButton.classList.add('btn-delete-student', 'btn-danger', 'btn-sm'); // Added btn-danger and btn-sm
        deleteButton.style.marginLeft = '5px';
        actionsCell.appendChild(deleteButton);
    });

    studentTableContainer.appendChild(table);
}

// Load Students Function
async function loadStudents() {
    if (!auth.currentUser) {
        if (viewStudentsFeedback) {
            viewStudentsFeedback.textContent = 'Please login to view students.';
            viewStudentsFeedback.className = 'feedback-message feedback-warning';
        }
        return;
    }
    if (viewStudentsFeedback) {
        viewStudentsFeedback.textContent = 'Loading students...';
        viewStudentsFeedback.className = 'feedback-message feedback-info'; // Use info for loading
    }
    
    try {
        const q = query(collection(db, "students"), orderBy("createdAt", "desc")); // Order by most recently created
        const querySnapshot = await getDocs(q);
        const studentsArray = querySnapshot.docs.map(doc => ({ id: doc.id, data: doc.data() }));
        renderStudentsTable(studentsArray); // renderStudentsTable handles empty array by showing message
    } catch (error) {
        console.error("Error loading students: ", error);
        if (viewStudentsFeedback) {
            viewStudentsFeedback.textContent = `Error loading students: ${error.message}`;
            viewStudentsFeedback.className = 'feedback-message feedback-error';
        }
    }
}
