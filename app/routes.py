from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app import app, db
from app.models import Patient, Doctor, UserLog, Admin, Position, Questionnaire, DoctorPatientAssignment, Message, ProgressLog
from datetime import datetime, date
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/questions')


def questions():
    if 'patient_id' not in session:
        flash('Please log in to access the questionnaire.', 'register')
        return redirect(url_for('index'))
    return render_template('questions.html')

def questions():
    return render_template('questions.html')

# register new patint
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # Get form data
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            dob = datetime.strptime(request.form['dob'], '%Y-%m-%d').date()
            email = request.form['email']
            password = request.form['password']
            gender = request.form['gender']
            address = request.form['address']
            phone = request.form['phone']
            contactprefer = request.form['contactprefer']

            # Validate age (18-35 years old)
            age = (datetime.now().date() - dob).days // 365
            if age < 18 or age > 35:
                flash('You must be between 18 and 35 years old to register.', 'register')
                return redirect(url_for('register'))
 
  # Check if user with same email or phone exists
            existing_user = Patient.query.filter((Patient.email == email) | (Patient.contact == phone)).first()
            if existing_user:
                flash('A user with this email or phone number already exists.', 'register')
                return redirect(url_for('register'))

            # Create new patient
            new_patient = Patient(
                firstname=firstname,
                lastname=lastname,
                email=email,
                password=password,
                contact=phone,
                contact_prefer=contactprefer,
                address=address,
                dob=dob,
                gender=gender,
                status='inactive'  # Set default status to inactive
            )

            db.session.add(new_patient)
            db.session.commit()
              # Store the patient_id in the session
            session['patient_id'] = new_patient.patient_id
            session['patient_email'] = new_patient.email

            flash('Registration successful! Please continue with the questions.', 'reg_success')
            return redirect(url_for('questions'))   #Redirect to the steps page

        except ValueError as e:
            db.session.rollback()
            flash(f'Invalid data: {str(e)}', 'error')
        except IntegrityError as e:
            db.session.rollback()           
            flash('A database error occurred. Please try again.', 'register')
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f'Database error during registration: {str(e)}')
            flash('A database error occurred. Please try again.', 'register')

    return render_template('index.html')  # Render the registration form for GET requests
 

# save patient answers and generate related terapiste 
@app.route('/submit_questionnaire', methods=['POST'])
def submit_questionnaire():
    if request.method == 'POST':
        # Process the form data here
            # You can access form data using request.form
         # Process the form data here
        qn1 = request.form.get('qn1') == '1'
        qn2 = request.form.get('qn2') == '1'
        qn3 = request.form.get('qn3') == '1'
        qn4 = request.form.get('qn4') == '1'
        qn5 = request.form.get('qn5') == '1'
        
       # Determine the doctor position based on answers
        if qn1 == 1 and qn2 == 1 and qn3 == 1 and qn4 == 1:
            position_name = "Therapist Case Manager"
        elif qn3 == 1 and qn5 == 1 and qn2 == 1 and qn4 == 1:
            position_name = "Social Worker Team Leader Program Director"
        elif qn1 == 1 and qn2 == 1 and qn3 == 1 and qn5 == 1:
            position_name = "Therapist Clinician Case Manager"
        elif qn1 == 1 and qn2 == 1 and qn5 == 1:
            position_name = "Clinician Clinical Supervisor Nursing Director" 
        elif qn1 == 1 and qn5 == 1:
            position_name = "Therapist Case Manager Nursing Director"     
        else:
            position_name = "General Practitioner"

        try:
            # Find the position_id based on the position_name
            position = Position.query.filter_by(position_name=position_name).first()
            if not position:
                flash('Position not found. Please contact support.', 'error')
                return redirect(url_for('questions'))

            # Update the patient record in the database
            patient = Patient.query.filter_by(patient_id=session.get('patient_id')).first()
            if patient:
                patient.position_id = position.position_id
                                
                # Create and insert new Questionnaire entry
                new_questionnaire = Questionnaire(
                    patient_id=patient.patient_id,
                    qn1=qn1,
                    qn2=qn2,
                    qn3=qn3,
                    qn4=qn4,
                    qn5=qn5
                )
                db.session.add(new_questionnaire)
                

                db.session.commit()
                flash(f'{position_name}.', 'successfull',)
                return render_template('success.html')
            else:
                flash('Patient record not found. Please try again.', 'error')
                # insert into questionaire 
                
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f'Database error during questionnaire submission: {str(e)}')
            flash('A database error occurred. Please try again.', 'error')

        flash('Error occured pleas try again', 'success')
        return redirect(url_for('questions'))
    
    # If not a POST request, redirect back to the steps page
    return redirect(url_for('questions'))

@app.route('/get_patient_questionnaire/<int:patient_id>')
def get_patient_questionnaire(patient_id):
    questionnaire = Questionnaire.query.filter_by(patient_id=patient_id).order_by(Questionnaire.created_at.desc()).first()
    
    if questionnaire:
        questionnaire_data = {
            'created_at': questionnaire.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'qn1': questionnaire.qn1,
            'qn2': questionnaire.qn2,
            'qn3': questionnaire.qn3,
            'qn4': questionnaire.qn4,
            'qn5': questionnaire.qn5
        }
        return jsonify({'questionnaire': questionnaire_data})
    else:
        return jsonify({'questionnaire': None}) 
    

@app.route('/doctor-patient-dashboard/<int:patient_id>')
def doctor_patient_dashboard(patient_id):
    if 'doctor_id' not in session:
        flash('Please log in to access the questionnaire.', 'register')
        return redirect('/doctorlogin')
    patient = Patient.query.get(patient_id)
    doctor = Doctor.query.get(session['doctor_id'])
#    get patient progress log ProgressLog 
    progressLogs = ProgressLog.query.filter_by(patient_id=patient_id).order_by(ProgressLog.timestamp.desc()).all()

    return render_template('doctor/doctor_patient_dashboard.html',doctor=doctor, doctor_id=session['doctor_id'], patient_id=patient_id,patient=patient, progressLogs=progressLogs)
   
@app.route('/update_patient_progress', methods=['POST'])
def update_patient_progress():
    data = request.json
    patient = Patient.query.get(data['patient_id'])
    patient.progress = data['progress']
    db.session.commit()
    return jsonify({"message": "Progress updated successfully"}), 200

    
@app.route('/payment')
def payment():
    if 'patient_id' not in session:
        flash('Please log in to access the questionnaire.', 'register')
        return redirect('/')
    return render_template('success.html')

@app.route('/payment_pending')
def payment_success():
    if 'patient_id' not in session:
        flash('Please log in to access the questionnaire.', 'register')
        return redirect('/')
    return render_template('payment_pending.html')

@app.route('/payment_failure')
def payment_failure():
    if 'patient_id' not in session:
        flash('Please log in to access the questionnaire.', 'register')
        return redirect('/')
    return render_template('payment_failure.html')

@app.route('/edit_doctor', methods=['GET', 'POST'])
def edit_doctor():
    doctor_id = request.args.get('doctor_id', type=int)    
    doctor = Doctor.query.get_or_404(doctor_id)
    positions = Position.query.all()
    

    if request.method == 'POST':
        doctor_id = request.form['doctor_id']
        doctor = Doctor.query.get_or_404(doctor_id)
        doctor.fullname = request.form['fullname']
        doctor.position_id = request.form['doctor_position']
        doctor.contact = request.form['doctor_phone']
        doctor.email = request.form['doctor_email']
        doctor.gender = request.form['doctor_gender']

        db.session.commit()
        flash('Doctor information updated successfully', 'success')
        return redirect(url_for('doctors'))

    return render_template('admin/edit_doctor.html', doctor=doctor, positions=positions)


@app.route('/doctorlogin', methods=['GET', 'POST'])
def doctorlogin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        doctor = Doctor.query.filter_by(email=email, password=password).first()
        
        if doctor:
            session['doctor_id'] = doctor.doctor_id
            session['name'] = doctor.fullname
            session['email'] = doctor.email
            
            # Create a new UserLog entry
            new_log = UserLog(user_id=doctor.doctor_id, loginTime=datetime.utcnow())
            db.session.add(new_log)
            db.session.commit()
            
            return redirect(url_for('doctor_dashboard'))
        else:
            flash('Invalid email or password', 'doctor_login_error')
    
    return render_template('doctorlogin.html')

@app.route('/doctor_dashboard')
def doctor_dashboard():
    if 'doctor_id' not in session:
        return redirect(url_for('doctorlogin'))
    
    doctor = Doctor.query.get(session['doctor_id'])
    
    # Query pending patients with matching position_id
    pending_patients = Patient.query.filter_by(
        status='pending',
        position_id=doctor.position_id
    ).order_by(Patient.patient_id.asc()).all()
    
    return render_template('doctor/doctor_dashboard.html', doctor=doctor, patients=pending_patients)

@app.route('/doctor_confirmed_patients')
def doctor_confirmed_patients():
    if 'doctor_id' not in session:
        return redirect(url_for('doctorlogin'))
    
    doctor = Doctor.query.get(session['doctor_id'])
    
    # Query pending patients with matching position_id
    comfirmed_patients = Patient.query.filter_by(
        status='confirmed',
        position_id=doctor.position_id
    ).order_by(Patient.patient_id.asc()).all()
    
    return render_template('doctor/doctor_confirmed_patients.html', doctor=doctor, patients=comfirmed_patients)

@app.route('/doctor_taken_patients')
def doctor_taken_patients():
    if 'doctor_id' not in session:
        return redirect(url_for('doctorlogin'))
    
    doctor = Doctor.query.get(session['doctor_id'])
    current_date = datetime.now().date()  # Get the current date
    # Query pending patients with matching position_id
    assigned_patients = Patient.query.join(DoctorPatientAssignment).filter(
    DoctorPatientAssignment.doctor_id == doctor.doctor_id,
    DoctorPatientAssignment.status == 'accepted'
    ).all()
    
    return render_template('doctor/doctor_taken_patients.html',today=date.today(), doctor=doctor, patients=assigned_patients)



# @app.route('/doctor_confirmed_patients')
# def doctor_confirmed_patients():
#     doctor_confirmed_patients = Patient.query.filter_by(status='confirmed').order_by(Patient.patient_id.asc()).all()
#     return render_template('doctor/doctor_confirmed_patients.html', patients=doctor_confirmed_patients)


@app.route('/confirm_patient/<int:patient_id>')
def confirm_patient(patient_id):
    
    if 'doctor_id' not in session:
        return redirect(url_for('doctorlogin'))
    
    patient = Patient.query.get_or_404(patient_id)
    patient.status = 'confirmed'
    db.session.commit()
    flash('Patient confirmed successfully', 'success')
    return redirect(url_for('doctor_dashboard'))


@app.route('/take_patient/<int:patient_id>')
def take_patient(patient_id):
    if 'doctor_id' not in session:
        return redirect(url_for('doctorlogin'))
    
    patient = Patient.query.get_or_404(patient_id)
    doctor_id = session['doctor_id']

    # Create a new DoctorPatientAssignment
    assignment = DoctorPatientAssignment(
        doctor_id=doctor_id,
        patient_id=patient_id,
        status='accepted'
    )
    # Add the assignment to the database
    db.session.add(assignment)

    # Update patient status
    patient.status = 'taken'
    db.session.commit()
    flash('Patient taken successfully', 'taken')
    return redirect(url_for('doctor_taken_patients'))



@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        admin = Admin.query.filter_by(email=email, password=password).first()
        
        if admin:
            session['admin_id'] = admin.admin_id
            session['name'] = admin.fullname
            session['email'] = admin.email
            
                     
            # You might want to add logic here to determine if it's an admin or regular admin
            # For now, we'll assume there's only one type of dashboard
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid email or password', 'admin_login_error')
    
    return render_template('adminlogin.html')

@app.route('/patientlogin', methods=['GET', 'POST'])
def patientlogin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        patient = Patient.query.filter_by(email=email, password=password).first()
        
        if patient:
            session['patient_id'] = patient.patient_id
            session['patient_email'] = patient.email
            
                     
            # You might want to add logic here to determine if it's an admin or regular admin
            # For now, we'll assume there's only one type of dashboard
            return redirect(url_for('patient_dashboard'))
        else:
            flash('Invalid email or password', 'patient_login_error')
    
    return render_template('patientlogin.html')


@app.route('/patient_dashboard') 
def patient_dashboard():
    if 'patient_id' not in session:
        flash('Please log in to access the system.', 'register')
        return redirect('/')
   
    patient = Patient.query.get(session['patient_id'])
    position = Position.query.filter_by(position_id=patient.position_id).first()
    questionnaire = Questionnaire.query.filter_by(patient_id=patient.patient_id).order_by(Questionnaire.created_at.desc()).first()
    assigned_doctor_id = DoctorPatientAssignment.query.filter_by(patient_id=patient.patient_id).first()
    doctor = Doctor.query.get(assigned_doctor_id.doctor_id)

    if patient.status == "pending" : 
        flash('Your registration is pending. Please wait for confirmation.', 'patient_pending')
        return redirect('/patient_pending')
        
    return render_template('patient/patient_dashboard.html',position=position, doctor=doctor, patient=patient, questionnaire=questionnaire)


# ptient progress log 
@app.route('/patient_progress_report') 

def patient_progress_report():
    if 'patient_id' not in session:
        flash('Please log in to access the system.', 'register')
        return redirect('/')
   
    patient = Patient.query.get(session['patient_id'])
    position = Position.query.filter_by(position_id=patient.position_id).first()
    questionnaire = Questionnaire.query.filter_by(patient_id=patient.patient_id).order_by(Questionnaire.created_at.desc()).first()
    assigned_doctor_id = DoctorPatientAssignment.query.filter_by(patient_id=patient.patient_id).first()
    doctor = Doctor.query.get(assigned_doctor_id.doctor_id)

    if patient.status == "pending" : 
        flash('Your registration is pending. Please wait for confirmation.', 'patient_pending')
        return redirect('/patient_pending')
        
    return render_template('patient/patient_progress_report.html',position=position, doctor=doctor, patient=patient, questionnaire=questionnaire)


@app.route('/patient_pending')
def patient_pending():
 
    if 'patient_id' not in session:
        flash('Please log in to access the questionnaire.', 'register')
        return redirect('/')
   
    patient = Patient.query.get(session['patient_id'])
     
    if patient.status == "taken" : 
        
        return redirect('/patient_dashboard')
    position = Position.query.filter_by(position_id=patient.position_id).first()
    questionnaire = Questionnaire.query.filter_by(patient_id=patient.patient_id).order_by(Questionnaire.created_at.desc()).first()
    
    return render_template('patient/patient_pending.html',position=position, patient=patient, questionnaire=questionnaire)


@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('adminlogin'))
    
    patients = Patient.query.all()
    patients_count = Patient.query.count()

    # Count doctors
    doctor_count = Doctor.query.count()
    
    # Count inactive patients
    inactive_patient_count = Patient.query.filter_by(status='inactive').count()
    # Count pending patients
    pending_patient_count = Patient.query.filter_by(status='pending').count()
    
    # Count confirmed patients
    confirmed_patient_count = Patient.query.filter_by(status='confirmed').count()
    
     # Count taken patients
    taken_patient_count = Patient.query.filter_by(status='taken').count()
    
    return render_template('admin/admin_dashboard.html', 
                           doctor_count=doctor_count,
                           pending_patient_count=pending_patient_count,
                           taken_patient_count=taken_patient_count,
                           confirmed_patient_count=confirmed_patient_count,
                           patients_count=patients_count,
                           patients=patients,inactive_patient_count=inactive_patient_count)



@app.route('/patients')
def patients():
    patients = Patient.query.order_by(Patient.patient_id.asc()).all()
    return render_template('admin/patient.html', patients=patients)

@app.route('/taken_patients')
def taken_patients():
    taken_patients = Patient.query.filter_by(status='taken').order_by(Patient.patient_id.asc()).all()
    
    patient_data = []
    for patient in taken_patients:
        # Get the assigned doctor
        assignment = DoctorPatientAssignment.query.filter_by(patient_id=patient.patient_id, status='accepted').first()
        doctor_name = assignment.doctor.fullname if assignment else "No doctor assigned"
        doctor_id = assignment.doctor.doctor_id
        
        # Get the assigned doctor full detail
        # doctor_full_detail = Doctor.query.filter_by(doctor_id=assignment.doctor.doctor_id).first()
        
        # get therapiste department position
        position = Position.query.filter_by(position_id=patient.position_id).first()
        # Get the latest questionnaire
        questionnaire = Questionnaire.query.filter_by(patient_id=patient.patient_id).order_by(Questionnaire.created_at.desc()).first()
        
        patient_data.append({
            'patient': patient,
            'doctor_name': doctor_name,
            'questionnaire': questionnaire,
            'position': position,
            'doctor_id': doctor_id
        })
    
    return render_template('admin/taken_patient.html', patient_data=patient_data)

@app.route('/get_therapist_info/<int:doctor_id>', methods=['GET'])
def get_therapist_info(doctor_id):
    therapist = Doctor.query.get_or_404(doctor_id)
    position = Position.query.get(therapist.position_id)
    
    therapist_info = {
        'fullname': therapist.fullname,
        'email': therapist.email,
        'contact': therapist.contact,
        'gender': therapist.gender,
        'position': position.position_name if position else 'Unknown'
    }
    
    return jsonify(therapist_info)

def taken_patients():
    taken_patients = Patient.query.filter_by(status='taken').order_by(Patient.patient_id.asc()).all()
    
    return render_template('admin/taken_patient.html', patients=taken_patients)
    

@app.route('/confirmed_patients')
def confirmed_patients():
    confirmed_patients = Patient.query.filter_by(status='confirmed').order_by(Patient.patient_id.asc()).all()
    return render_template('admin/confirmed_patient.html', patients=confirmed_patients)

@app.route('/pending_patients')
def pending_patients():
    pending_patients = Patient.query.filter_by(status='pending').order_by(Patient.patient_id.asc()).all()
    return render_template('admin/pending_patient.html', patients=pending_patients)

@app.route('/inactive_patients')
def inactive_patients():
    inactive_patients = Patient.query.filter_by(status='inactive').order_by(Patient.patient_id.asc()).all()
    return render_template('admin/inactive_patients.html', patients=inactive_patients)

@app.route('/doctors')
def doctors():
    doctors = Doctor.query.order_by(Doctor.doctor_id.asc()).all()
    return render_template('admin/doctor.html', doctors=doctors)


from flask import render_template, request, redirect, url_for, flash
from app import app, db
from app.models import Doctor, Position

@app.route('/add_doctor', methods=['GET', 'POST'])
def add_doctor():
    positions = Position.query.all()
    
    if request.method == 'POST':
        fullname = request.form.get('doctor_name')
        position_id = request.form.get('doctor_position')
        contact = request.form.get('doctor_phone')
        email = request.form.get('doctor_email')
        password = request.form.get('doctor_pswd')
        gender = request.form.get('doctor_gender')

        # Check if email already exists
        existing_doctor = Doctor.query.filter_by(email=email).first()
        if existing_doctor:
            flash('Email already exists', 'error')
            return redirect(url_for('add_doctor'))

        new_doctor = Doctor(
            fullname=fullname,
            position_id=position_id,
            email=email,
            gender=gender,
            contact=contact,
            password=password  # Storing password as plain text
        )

        try:
            db.session.add(new_doctor)
            db.session.commit()
            flash('Doctor successfully added', 'success')
            return redirect(url_for('doctors'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding doctor: {str(e)}', 'error')

    return render_template('admin/add_doctor.html', positions=positions)


@app.route('/add_admin', methods=['GET', 'POST'])
def add_admin():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        phone = request.form.get('phone')
        email = request.form.get('email')
        password = request.form.get('pswd')

        # Check if email already exists
        existing_admin = Admin.query.filter_by(email=email).first()
        if existing_admin:
            flash('Email already exists', 'error')
            return redirect(url_for('add_admin'))

        new_admin = Admin(
            fullname=fullname,
            email=email,
            password=password
        )

        try:
            db.session.add(new_admin)
            db.session.commit()
            flash('Admin successfully added', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding admin: {str(e)}', 'error')

    return render_template('admin/add_admin.html')


@app.route('/admin/delete_doctor/<int:doctor_id>', methods=['POST'])
def delete_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    try:
        db.session.delete(doctor)
        db.session.commit()
        flash('Doctor successfully deleted', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting doctor: {str(e)}', 'error')
    return redirect(url_for('doctors'))


@app.route('/logout')
def logout():
    user_id = session.get('admin_id') or session.get('doctor_id')
    user_type = 'admin' if 'admin_id' in session else 'doctor'

    if user_id:
        # Update the UserLog entry with logout time
        latest_log = UserLog.query.filter_by(user_id=user_id, logoutTime=None).order_by(UserLog.loginTime.desc()).first()
        if latest_log:
            latest_log.logoutTime = datetime.utcnow()
            db.session.commit()
        
        # Clear the session
        session.clear()
    
    # Redirect based on user type
    if user_type == 'admin':
        return redirect(url_for('adminlogin'))
    else:
        return redirect(url_for('doctorlogin'))
    

@app.route('/patient-logout')
def patientLogout():
        # Clear the session
        session.clear()
    
    # Redirect based on user type
   
        return redirect(url_for('questions'))
    
# message block

@app.route('/send_message', methods=['POST'])
def send_message():
     try:
         data = request.json
         new_message = Message(
             sender_type=data['sender_type'],
             sender_id=data['sender_id'],
             receiver_type=data['receiver_type'],
             receiver_id=data['receiver_id'],
             content=data['content']
         )
         db.session.add(new_message)
         db.session.commit()
         return jsonify({"message": "Message sent successfully"})
     except Exception as e:
         db.session.rollback()
         return jsonify({"error": str(e)})

@app.route('/get_messages/<string:user_type>/<int:user_id>', methods=['GET'])
def get_messages(user_type, user_id):
    messages = Message.query.filter(
        ((Message.sender_type == user_type) & (Message.sender_id == user_id)) |
        ((Message.receiver_type == user_type) & (Message.receiver_id == user_id))
    ).order_by(Message.timestamp.desc()).all()
    return jsonify([{
        "id": msg.message_id,
        "sender_type": msg.sender_type,
        "sender_id": msg.sender_id,
        "receiver_type": msg.receiver_type,
        "receiver_id": msg.receiver_id,
        "content": msg.content,
        "timestamp": msg.timestamp.isoformat()
    } for msg in messages]), 200


@app.route('/get_messages/doctor/<string:doctor_id>/patient/<string:patient_id>', methods=['GET'])
def get_doctor_messages(doctor_id, patient_id):
    messages = Message.query.filter(
        (
            (Message.sender_type == 'doctor') & 
            (Message.sender_id == doctor_id) & 
            (Message.receiver_type == 'patient') & 
            (Message.receiver_id == patient_id)
        ) | (
            (Message.sender_type == 'patient') & 
            (Message.sender_id == patient_id) & 
            (Message.receiver_type == 'doctor') & 
            (Message.receiver_id == doctor_id)
        )
    ).order_by(Message.timestamp.desc()).all()

    return jsonify([{
        "id": msg.message_id,
        "sender_type": msg.sender_type,
        "sender_id": msg.sender_id,
        "receiver_type": msg.receiver_type,
        "receiver_id": msg.receiver_id,
        "content": msg.content,
        "timestamp": msg.timestamp.isoformat()
    } for msg in messages]), 200


# patient progress route

@app.route('/log_progress', methods=['POST'])
def log_progress():
    data = request.json
    new_log = ProgressLog(
        patient_id=data['patient_id'],
        mood=data['mood'],
        symptoms=data['symptoms'],
        notes=data['notes']
    )
    db.session.add(new_log)
    db.session.commit()
    return jsonify({"message": "Progress logged successfully"}), 200

@app.route('/get_progress/<int:patient_id>', methods=['GET'])
def get_progress(patient_id):
    logs = ProgressLog.query.filter_by(patient_id=patient_id).order_by(ProgressLog.timestamp).all()
    return jsonify([{
        "log_id": log.log_id,
        "mood": log.mood,
        "symptoms": log.symptoms,
        "notes": log.notes,
        "timestamp": log.timestamp.isoformat()
    } for log in logs]), 200


