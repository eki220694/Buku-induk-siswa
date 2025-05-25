// Firebase SDK version 9.x
import { initializeApp } from "https://www.gstatic.com/firebasejs/9.22.1/firebase-app.js";
// Ensure getAuth is imported if not already, plus the functions below
import { 
    getAuth, 
    createUserWithEmailAndPassword, 
    signInWithEmailAndPassword, 
    signOut, 
    onAuthStateChanged 
} from "https://www.gstatic.com/firebasejs/9.22.1/firebase-auth.js";
// Import Firestore functions
import { 
    getFirestore,
    collection, 
    addDoc, 
    serverTimestamp,
    getDocs, 
    query, 
    orderBy,
    where,    
    doc,      
    getDoc,   
    updateDoc,
    deleteDoc 
} from "https://www.gstatic.com/firebasejs/9.22.1/firebase-firestore.js";

// IMPORTANT: TODO: User must replace these with their actual Firebase project configuration!
const firebaseConfig = {
  <script type="module">
  // Import the functions you need from the SDKs you need
  import { initializeApp } from "https://www.gstatic.com/firebasejs/11.8.1/firebase-app.js";
  import { getAnalytics } from "https://www.gstatic.com/firebasejs/11.8.1/firebase-analytics.js";
  // TODO: Add SDKs for Firebase products that you want to use
  // https://firebase.google.com/docs/web/setup#available-libraries

  // Your web app's Firebase configuration
  // For Firebase JS SDK v7.20.0 and later, measurementId is optional
  const firebaseConfig = {
    apiKey: "AIzaSyBh-ArVTAd3sYQBkGyRyGn_t-dd3LKJLkI",
    authDomain: "bukuinduksiswa-c26a1.firebaseapp.com",
    projectId: "bukuinduksiswa-c26a1",
    storageBucket: "bukuinduksiswa-c26a1.firebasestorage.app",
    messagingSenderId: "309663744157",
    appId: "1:309663744157:web:e8c08da5025e5070711474",
    measurementId: "G-R2FYDEF7F4"
  };

  // Initialize Firebase
  const app = initializeApp(firebaseConfig);
  const analytics = getAnalytics(app);
</script>

};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app); // Firebase Authentication instance
const db = getFirestore(app); // Firestore Database instance

console.log("Firebase SDK initialized. Auth and Firestore services are ready.");

// Get DOM Elements
const emailField = document.getElementById('email-field');
const passwordField = document.getElementById('password-field');
const buttonSignup = document.getElementById('button-signup');
const buttonLogin = document.getElementById('button-login');
const buttonLogout = document.getElementById('button-logout');
const authMessageFeedback = document.getElementById('auth-message-feedback');
const userInfoDisplay = document.getElementById('user-info-display');
const authContainer = document.getElementById('auth-container');
const appContainer = document.getElementById('app-container');

// Add Student Form Element References (will be defined in onAuthStateChanged)
let formAddNewStudent, feedbackAddStudent;

// View Student Elements (will be defined in onAuthStateChanged)
let btnFetchStudents, studentsDataTableDiv, feedbackLoadStudents;

// Edit Student Elements (will be defined in onAuthStateChanged)
let editStudentModuleContainer, formUpdateStudent, updateDocIdField, textEditStudentId;
let fieldEditFullName, fieldEditDateOfBirth, selectEditGender, areaEditAddress, fieldEditPhoneNumber;
let fieldEditStudentEmail, fieldEditEnrollmentYear, selectEditStudentStatus, fieldEditGraduationYear;
let buttonCancelUpdate, feedbackUpdateStudent;

// Other module containers (will be defined in onAuthStateChanged)
let addStudentFormContainer, viewAllStudentsContainer;

// Graduated Student Access Elements
const formPublicGradSearch = document.getElementById('form-public-grad-search');
const inputPublicGradId = document.getElementById('input-public-grad-id');
const outputGraduatedStudentDetails = document.getElementById('output-graduated-student-details');
const feedbackPublicGradSearch = document.getElementById('feedback-public-grad-search');


// Sign Up Button Event Listener
if (buttonSignup) {
    buttonSignup.addEventListener('click', async () => {
        const email = emailField.value;
        const password = passwordField.value;
        if(authMessageFeedback) authMessageFeedback.textContent = ''; 
        try {
            const userCredential = await createUserWithEmailAndPassword(auth, email, password);
            if(authMessageFeedback) {
                authMessageFeedback.textContent = `Signed up and logged in as ${userCredential.user.email}`;
                authMessageFeedback.className = 'feedback-message feedback-success';
            }
        } catch (error) {
            if(authMessageFeedback) {
                authMessageFeedback.textContent = `Error signing up: ${error.message}`;
                authMessageFeedback.className = 'feedback-message feedback-error';
            }
        }
    });
} else {
    console.error("Sign Up button not found");
}

// Login Button Event Listener
if (buttonLogin) {
    buttonLogin.addEventListener('click', async () => {
        const email = emailField.value;
        const password = passwordField.value;
        if(authMessageFeedback) authMessageFeedback.textContent = '';
        try {
            const userCredential = await signInWithEmailAndPassword(auth, email, password);
            if(authMessageFeedback) {
                authMessageFeedback.textContent = `Logged in as ${userCredential.user.email}`;
                authMessageFeedback.className = 'feedback-message feedback-success';
            }
        } catch (error) {
            if(authMessageFeedback) {
                authMessageFeedback.textContent = `Error logging in: ${error.message}`;
                authMessageFeedback.className = 'feedback-message feedback-error';
            }
        }
    });
} else {
    console.error("Login button not found");
}

// Logout Button Event Listener
if (buttonLogout) {
    buttonLogout.addEventListener('click', async () => {
        if(authMessageFeedback) authMessageFeedback.textContent = '';
        try {
            await signOut(auth);
        } catch (error) {
            if(authMessageFeedback) {
                authMessageFeedback.textContent = `Error logging out: ${error.message}`;
                authMessageFeedback.className = 'feedback-message feedback-error';
            }
        }
    });
} else {
    console.error("Logout button not found");
}

// onAuthStateChanged Observer
onAuthStateChanged(auth, (user) => {
    if (user) { 
        if(userInfoDisplay) userInfoDisplay.textContent = user.email;
        if(authContainer) authContainer.style.display = 'none';
        if(appContainer) appContainer.style.display = 'block';
        if(authMessageFeedback) authMessageFeedback.textContent = ''; 

        formAddNewStudent = document.getElementById('form-add-student-entry');
        feedbackAddStudent = document.getElementById('feedback-add-student');
        
        btnFetchStudents = document.getElementById('btn-fetch-students');
        studentsDataTableDiv = document.getElementById('students-data-table-div'); 
        feedbackLoadStudents = document.getElementById('feedback-load-students');
        
        editStudentModuleContainer = document.getElementById('edit-student-module-container');
        formUpdateStudent = document.getElementById('form-update-student');
        updateDocIdField = document.getElementById('update-doc-id-field');
        textEditStudentId = document.getElementById('text-edit-student-id');
        fieldEditFullName = document.getElementById('field-edit-full-name');
        fieldEditDateOfBirth = document.getElementById('field-edit-date-of-birth');
        selectEditGender = document.getElementById('select-edit-gender');
        areaEditAddress = document.getElementById('area-edit-address');
        fieldEditPhoneNumber = document.getElementById('field-edit-phone-number');
        fieldEditStudentEmail = document.getElementById('field-edit-student-email');
        fieldEditEnrollmentYear = document.getElementById('field-edit-enrollment-year');
        selectEditStudentStatus = document.getElementById('select-edit-student-status');
        fieldEditGraduationYear = document.getElementById('field-edit-graduation-year');
        buttonCancelUpdate = document.getElementById('button-cancel-update');
        feedbackUpdateStudent = document.getElementById('feedback-update-student');

        addStudentFormContainer = document.getElementById('add-student-form-container');
        viewAllStudentsContainer = document.getElementById('view-all-students-container');

        if (formAddNewStudent) {
            formAddNewStudent.addEventListener('submit', async (e) => {
                e.preventDefault();
                if(feedbackAddStudent) {
                    feedbackAddStudent.textContent = ''; 
                    feedbackAddStudent.className = 'feedback-message';
                }
                const currentUser = auth.currentUser; 
                if (!currentUser) {
                    if(feedbackAddStudent) {
                        feedbackAddStudent.textContent = 'Error: No authenticated user. Please re-login.';
                        feedbackAddStudent.className = 'feedback-message feedback-error';
                    }
                    return;
                }
                const studentData = {
                    studentId: document.getElementById('input-student-id').value.trim(),
                    fullName: document.getElementById('input-full-name').value.trim(),
                    dateOfBirth: document.getElementById('input-date-of-birth').value || null,
                    gender: document.getElementById('input-gender').value,
                    address: document.getElementById('input-address').value.trim() || null,
                    phoneNumber: document.getElementById('input-phone-number').value.trim() || null,
                    email: document.getElementById('input-student-email').value.trim() || null,
                    enrollmentYear: document.getElementById('input-enrollment-year').value ? parseInt(document.getElementById('input-enrollment-year').value) : null,
                    status: document.getElementById('input-student-status').value,
                    graduationYear: document.getElementById('input-graduation-year').value ? parseInt(document.getElementById('input-graduation-year').value) : null,
                    createdBy: currentUser.uid,
                    createdAt: serverTimestamp()
                };
                if (!studentData.studentId || !studentData.fullName) {
                    if(feedbackAddStudent) {
                        feedbackAddStudent.textContent = 'Student ID and Full Name are required.';
                        feedbackAddStudent.className = 'feedback-message feedback-error';
                    }
                    return;
                }
                try {
                    const docRef = await addDoc(collection(db, "students"), studentData);
                    console.log("Student record created with ID: ", docRef.id);
                    if(feedbackAddStudent) {
                        feedbackAddStudent.textContent = `Student "${studentData.fullName}" (ID: ${studentData.studentId}) added successfully.`;
                        feedbackAddStudent.className = 'feedback-message feedback-success';
                    }
                    formAddNewStudent.reset(); 
                } catch (error) {
                    console.error("Error adding student record: ", error);
                    if(feedbackAddStudent) {
                        feedbackAddStudent.textContent = `Error adding student: ${error.message}`;
                        feedbackAddStudent.className = 'feedback-message feedback-error';
                    }
                }
            });
        } else {
            console.error("Add student form ('form-add-student-entry') not found.");
        }

        if (btnFetchStudents) {
            btnFetchStudents.addEventListener('click', loadAndDisplayStudents);
        } else {
            console.error("Button 'btn-fetch-students' not found.");
        }

        if (studentsDataTableDiv) {
            if (!studentsDataTableDiv.dataset.listenerAttached) { 
                studentsDataTableDiv.addEventListener('click', (e) => {
                    if (e.target.classList.contains('action-edit-student')) {
                        const studentDocId = e.target.getAttribute('data-doc-id');
                        if (studentDocId) populateAndShowEditForm(studentDocId);
                    } else if (e.target.classList.contains('action-delete-student')) { 
                        const studentDocId = e.target.getAttribute('data-doc-id');
                        if (studentDocId) handleDeleteStudent(studentDocId); 
                    }
                });
                studentsDataTableDiv.dataset.listenerAttached = 'true';
            }
        } else {
            console.error("Student data table div ('students-data-table-div') not found for event delegation.");
        }

        if (buttonCancelUpdate) {
            buttonCancelUpdate.addEventListener('click', () => {
                if(editStudentModuleContainer) editStudentModuleContainer.style.display = 'none';
                if(formUpdateStudent) formUpdateStudent.reset();
                if(addStudentFormContainer) addStudentFormContainer.style.display = 'block';
                if(viewAllStudentsContainer) viewAllStudentsContainer.style.display = 'block';
            });
        } else {
            console.error("Button 'button-cancel-update' not found.");
        }
        
        if (formUpdateStudent) {
            formUpdateStudent.addEventListener('submit', async (e) => {
                e.preventDefault();
                const studentDocId = updateDocIdField.value;
                if (!studentDocId) {
                    if(feedbackUpdateStudent) {
                        feedbackUpdateStudent.textContent = "ERROR: No document ID for update.";
                        feedbackUpdateStudent.className = 'feedback-message feedback-error';
                    }
                    return;
                }
                const updatedData = {
                    fullName: fieldEditFullName.value.trim(),
                    dateOfBirth: fieldEditDateOfBirth.value || null,
                    gender: selectEditGender.value,
                    address: areaEditAddress.value.trim() || null,
                    phoneNumber: fieldEditPhoneNumber.value.trim() || null,
                    email: fieldEditStudentEmail.value.trim() || null,
                    enrollmentYear: fieldEditEnrollmentYear.value ? parseInt(fieldEditEnrollmentYear.value) : null,
                    status: selectEditStudentStatus.value,
                    graduationYear: fieldEditGraduationYear.value ? parseInt(fieldEditGraduationYear.value) : null,
                    updatedAt: serverTimestamp()
                };
                try {
                    const studentDocRef = doc(db, "students", studentDocId);
                    await updateDoc(studentDocRef, updatedData);
                    if(feedbackUpdateStudent) {
                        feedbackUpdateStudent.textContent = "Student record updated successfully!";
                        feedbackUpdateStudent.className = 'feedback-message feedback-success';
                    }
                    loadAndDisplayStudents(); 
                } catch (error) {
                    console.error("Error updating student record: ", error);
                    if(feedbackUpdateStudent) {
                        feedbackUpdateStudent.textContent = `Error updating: ${error.message}`;
                        feedbackUpdateStudent.className = 'feedback-message feedback-error';
                    }
                }
            });
        } else {
            console.error("Form 'form-update-student' not found.");
        }
        
        loadAndDisplayStudents(); 

    } else { 
        if(userInfoDisplay) userInfoDisplay.textContent = '';
        if(authContainer) authContainer.style.display = 'block';
        if(appContainer) appContainer.style.display = 'none';
        if(emailField) emailField.value = ''; 
        if(passwordField) passwordField.value = '';
        if(authMessageFeedback) {
            authMessageFeedback.textContent = '';
        }
    }
});

// --- Graduated Student Search Form Event Listener ---
if (formPublicGradSearch) {
    formPublicGradSearch.addEventListener('submit', async (e) => {
        e.preventDefault();
        const studentIdToFind = inputPublicGradId.value.trim();
        if(outputGraduatedStudentDetails) outputGraduatedStudentDetails.innerHTML = ''; 
        if(feedbackPublicGradSearch) {
            feedbackPublicGradSearch.textContent = '';
            feedbackPublicGradSearch.className = 'feedback-message';
        }

        if (!studentIdToFind) {
            if(feedbackPublicGradSearch) {
                feedbackPublicGradSearch.textContent = 'Please enter your Student ID to search.';
                feedbackPublicGradSearch.className = 'feedback-message feedback-warning';
            }
            return;
        }

        if(feedbackPublicGradSearch) {
            feedbackPublicGradSearch.textContent = 'Searching record...';
            feedbackPublicGradSearch.className = 'feedback-message feedback-info';
        }

        try {
            const studentsRef = collection(db, "students");
            const q = query(
                studentsRef,
                where("studentId", "==", studentIdToFind), 
                where("status", "==", "graduated")
            );
            const querySnapshot = await getDocs(q);

            if (querySnapshot.empty) {
                if(feedbackPublicGradSearch) {
                    feedbackPublicGradSearch.textContent = 'No record found with that Student ID, or the student has not graduated. Please check the ID and try again.';
                    feedbackPublicGradSearch.className = 'feedback-message feedback-warning';
                }
            } else {
                const studentData = querySnapshot.docs[0].data();
                
                let detailsHtml = `<h4>Student Record Found</h4>`;
                detailsHtml += `<p><strong>Name:</strong> ${studentData.fullName || 'N/A'}</p>`;
                detailsHtml += `<p><strong>Student ID:</strong> ${studentData.studentId || 'N/A'}</p>`;
                detailsHtml += `<p><strong>Status:</strong> ${studentData.status || 'N/A'}</p>`;
                if (studentData.graduationYear) {
                    detailsHtml += `<p><strong>Graduation Year:</strong> ${studentData.graduationYear}</p>`;
                }
                if (studentData.enrollmentYear) {
                    detailsHtml += `<p><strong>Enrollment Year:</strong> ${studentData.enrollmentYear}</p>`;
                }
                
                if(outputGraduatedStudentDetails) outputGraduatedStudentDetails.innerHTML = detailsHtml;
                if(feedbackPublicGradSearch) {
                    feedbackPublicGradSearch.textContent = 'Record displayed.';
                    feedbackPublicGradSearch.className = 'feedback-message feedback-success';
                }
            }
        } catch (error) {
            console.error("Error searching for graduated student:", error);
            if(feedbackPublicGradSearch) {
                feedbackPublicGradSearch.textContent = `An error occurred while searching: ${error.message}`;
                feedbackPublicGradSearch.className = 'feedback-message feedback-error';
            }
        }
    });
} else {
    console.error("Public graduated student search form not found.");
}


// --- Helper Functions for Student Data ---

async function handleDeleteStudent(studentDocId) {
    if (!confirm('Are you absolutely sure you want to delete this student record? This action cannot be undone.')) {
        return; 
    }
    const feedbackElement = feedbackLoadStudents || document.getElementById('feedback-load-students'); 
    if (!feedbackElement) {
        console.error("Feedback element 'feedback-load-students' not found.");
        alert("Could not display deletion status. Check console."); 
        return;
    }
    feedbackElement.textContent = 'Deleting student record...';
    feedbackElement.className = 'feedback-message feedback-info'; 
    try {
        const studentDocRef = doc(db, "students", studentDocId);
        await deleteDoc(studentDocRef);
        feedbackElement.textContent = 'Student record deleted successfully.';
        feedbackElement.className = 'feedback-message feedback-success';
        console.log('Student record deleted:', studentDocId);
        loadAndDisplayStudents(); 
    } catch (error) {
        console.error('Error deleting student record:', error);
        feedbackElement.textContent = `Error deleting record: ${error.message}`;
        feedbackElement.className = 'feedback-message feedback-error';
    }
}

async function populateAndShowEditForm(studentDocId) {
    const feedbackUpdateStudent = document.getElementById('feedback-update-student'); 
    const updateDocIdField = document.getElementById('update-doc-id-field');
    const textEditStudentId = document.getElementById('text-edit-student-id');
    const addStudentFormContainer = document.getElementById('add-student-form-container');
    const viewAllStudentsContainer = document.getElementById('view-all-students-container');
    const editStudentModuleContainer = document.getElementById('edit-student-module-container');

    if(feedbackUpdateStudent) {
        feedbackUpdateStudent.textContent = '';
        feedbackUpdateStudent.className = 'feedback-message';
    }
    try {
        const studentDocRef = doc(db, "students", studentDocId);
        const docSnap = await getDoc(studentDocRef);
        if (docSnap.exists()) {
            const data = docSnap.data();
            if(updateDocIdField) updateDocIdField.value = studentDocId;
            if(textEditStudentId) textEditStudentId.textContent = data.studentId; 
            if(fieldEditFullName) fieldEditFullName.value = data.fullName || '';
            if(fieldEditDateOfBirth) fieldEditDateOfBirth.value = data.dateOfBirth || '';
            if(selectEditGender) selectEditGender.value = data.gender || 'Male';
            if(areaEditAddress) areaEditAddress.value = data.address || '';
            if(fieldEditPhoneNumber) fieldEditPhoneNumber.value = data.phoneNumber || '';
            if(fieldEditStudentEmail) fieldEditStudentEmail.value = data.email || '';
            if(fieldEditEnrollmentYear) fieldEditEnrollmentYear.value = data.enrollmentYear || '';
            if(selectEditStudentStatus) selectEditStudentStatus.value = data.status || 'active';
            if(fieldEditGraduationYear) fieldEditGraduationYear.value = data.graduationYear || '';
            
            if(addStudentFormContainer) addStudentFormContainer.style.display = 'none';
            if(viewAllStudentsContainer) viewAllStudentsContainer.style.display = 'none';
            if(editStudentModuleContainer) editStudentModuleContainer.style.display = 'block';
        } else {
            if(feedbackUpdateStudent) {
                feedbackUpdateStudent.textContent = "Error: Student record not found for editing.";
                feedbackUpdateStudent.className = 'feedback-message feedback-error';
            }
        }
    } catch (error) {
        console.error("Error fetching student for edit: ", error);
        if(feedbackUpdateStudent) {
            feedbackUpdateStudent.textContent = `Error fetching data: ${error.message}`;
            feedbackUpdateStudent.className = 'feedback-message feedback-error';
        }
    }
}


function displayStudentsInTable(studentList) {
    const studentsDataTableDiv = document.getElementById('students-data-table-div'); 
    const feedbackLoadStudents = document.getElementById('feedback-load-students'); 

    if (!studentsDataTableDiv || !feedbackLoadStudents) {
        console.error("Required DOM elements for displaying students are missing.");
        return;
    }
    studentsDataTableDiv.innerHTML = ''; 
    if(feedbackLoadStudents) {
        feedbackLoadStudents.textContent = '';
        feedbackLoadStudents.className = 'feedback-message';
    }
    if (!studentList || studentList.length === 0) {
        if(feedbackLoadStudents) {
            feedbackLoadStudents.textContent = 'No student records found in the database.';
            feedbackLoadStudents.className = 'feedback-message feedback-info';
        }
        return;
    }
    const table = document.createElement('table');
    const thead = table.createTHead();
    const headerRow = thead.insertRow();
    const headers = ['Student ID', 'Full Name', 'Email', 'Status', 'Enrollment', 'Actions'];
    headers.forEach(headerText => {
        const th = document.createElement('th');
        th.textContent = headerText;
        headerRow.appendChild(th);
    });
    const tbody = table.createTBody();
    studentList.forEach(student => {
        const tr = tbody.insertRow();
        tr.insertCell().textContent = student.data.studentId || 'N/A';
        tr.insertCell().textContent = student.data.fullName || 'N/A';
        tr.insertCell().textContent = student.data.email || 'N/A';
        tr.insertCell().textContent = student.data.status || 'N/A';
        tr.insertCell().textContent = student.data.enrollmentYear || 'N/A';
        const actionsCell = tr.insertCell();
        const editBtn = document.createElement('button');
        editBtn.textContent = 'Edit';
        editBtn.setAttribute('data-doc-id', student.id); 
        editBtn.classList.add('action-edit-student', 'btn-sm'); 
        editBtn.style.marginRight = '5px';
        actionsCell.appendChild(editBtn);
        const deleteBtn = document.createElement('button');
        deleteBtn.textContent = 'Delete';
        deleteBtn.setAttribute('data-doc-id', student.id);
        deleteBtn.classList.add('action-delete-student', 'btn-danger', 'btn-sm'); 
        actionsCell.appendChild(deleteBtn);
    });
    studentsDataTableDiv.appendChild(table);
}

async function loadAndDisplayStudents() {
    const feedbackLoadStudents = document.getElementById('feedback-load-students'); 
    if (!auth.currentUser) { 
        if (feedbackLoadStudents) {
            feedbackLoadStudents.textContent = 'Authentication error. Please re-login.';
            feedbackLoadStudents.className = 'feedback-message feedback-error';
        }
        return;
    }
    if (feedbackLoadStudents) {
        feedbackLoadStudents.textContent = 'Loading student records...';
        feedbackLoadStudents.className = 'feedback-message feedback-info';
    }
    try {
        const studentsCollection = collection(db, "students");
        const q = query(studentsCollection, orderBy("createdAt", "desc")); 
        const querySnapshot = await getDocs(q);
        const studentList = [];
        querySnapshot.forEach(doc => {
            studentList.push({ id: doc.id, data: doc.data() });
        });
        displayStudentsInTable(studentList);
        if (feedbackLoadStudents) { 
            if (studentList.length > 0) {
               feedbackLoadStudents.textContent = `Loaded ${studentList.length} student(s).`;
               feedbackLoadStudents.className = 'feedback-message feedback-success';
            }
            // If studentList is empty, displayStudentsInTable handles the "No records" message
        }
    } catch (error) {
        console.error("Error fetching student records: ", error);
        if (feedbackLoadStudents) {
            feedbackLoadStudents.textContent = `Error loading records: ${error.message}`;
            feedbackLoadStudents.className = 'feedback-message feedback-error';
        }
    }
}
