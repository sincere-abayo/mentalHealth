from apscheduler.schedulers.background import BackgroundScheduler
from app import app, db
from app.models import Survey, Patient
from datetime import datetime, timedelta

def send_survey_reminders():
    with app.app_context():
        patients = Patient.query.all()
        for patient in patients:
            last_survey = Survey.query.filter_by(patient_id=patient.patient_id).order_by(Survey.sent_at.desc()).first()
            if not last_survey or (datetime.utcnow() - last_survey.sent_at) > timedelta(days=7):
                new_survey = Survey(
                    patient_id=patient.patient_id,
                    doctor_id=patient.doctor_id,
                    questions=[{"question": "How are you feeling today?", "type": "scale", "min": 1, "max": 10}]
                )
                db.session.add(new_survey)
        db.session.commit()

scheduler = BackgroundScheduler()
scheduler.add_job(send_survey_reminders, 'interval', days=1)
scheduler.start()
