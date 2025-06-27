from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class InspectionRecords(db.Model):
    __tablename__='inspection_records'
    id = db.Column(db.Integer, nullable=False, unique=True, autoincrement=True, primary_key=True)
    date = db.Column(db.Date)
    inspection_category = db.Column(db.String(100))
    department = db.Column(db.String(100))
    location = db.Column(db.String())
    observation = db.Column(db.String())
    compliance_status = db.Column(db.String(100))
    photo = db.Column(db.String())
    discussed_with = db.Column(db.String())
    target_date = db.Column(db.String(100))
    complied_photo = db.Column(db.String())
    updated_on = db.Column(db.String(100))

class MeetingRecords(db.Model):
    __tablename__='meeting_records'
    id = db.Column(db.Integer, nullable=False, unique=True, autoincrement=True, primary_key=True)
    date = db.Column(db.Date)
    meeting_category = db.Column(db.String(100))
    department = db.Column(db.String(100))
    no_participants = db.Column(db.Integer)
    chaired_by = db.Column(db.String(100))
    photo = db.Column(db.String())

class TrainingRecords(db.Model):
    __tablename__='training_records'
    id = db.Column(db.Integer, nullable=False, unique=True, autoincrement=True, primary_key=True)
    date = db.Column(db.Date)
    training_category = db.Column(db.String(100))
    other_category = db.Column(db.String(100))
    department = db.Column(db.String(100))
    no_participants = db.Column(db.Integer)
    participation_level = db.Column(db.String(100))
    photo = db.Column(db.String())