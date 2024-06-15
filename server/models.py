from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, Enum
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
import uuid

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})
db = SQLAlchemy(metadata=metadata)


def generate_uuid():
    return str(uuid.uuid4())


class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    admission_number = db.Column(db.String, unique=True, nullable=False)
    joined_date=db.Column(db.Date, nullable=False)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    date_of_birth = db.Column(db.Date, nullable=False)
    birth_certificate_number = db.Column(db.String)
    photo_url = db.Column(db.String)
    grade_id = db.Column(db.String, db.ForeignKey('grades.id'), nullable=False)
    stream_id=db.Column(db.String, db.ForeignKey('streams.id'), nullable=False)
    parents = db.relationship('Parent', backref='student')
    

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    category_name=db.Column(db.String)
    grades = db.relationship('Grade', backref='category')


class Grade(db.Model):
    __tablename__ = 'grades'
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    grade = db.Column(db.String)
    class_teacher_id = db.Column(db.String, db.ForeignKey('staffs.id'), nullable=False)
    category_id = db.Column(db.String, db.ForeignKey('categories.id'), nullable=False)
    

    students = db.relationship('Student', backref='grade')
    # subjects = db.relationship('Subject', backref='grade')
    strands = db.relationship('Strand', backref='grade')
    substrands = db.relationship('SubStrand', backref='grade')
    learning_outcomes = db.relationship('LearningOutcome', backref='grade')
    assessment_rubics = db.relationship('AssessmentRubic', backref='grade')
    reports = db.relationship('Report', backref='grade')



class Stream(db.Model):
    __tablename__ = 'streams'
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    stream_name=db.Column(db.String)
    students = db.relationship('Student', backref='stream')
    reports= db.relationship('Report', backref='stream')
    
    


class Staff(db.Model):
    __tablename__ = 'staffs'
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    payroll_number = db.Column(db.String)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    date_of_birth = db.Column(db.Date, nullable=False)
    phone_number = db.Column(db.String)
    alternative_contact = db.Column(db.String)
    email_address = db.Column(db.String)
    password = db.Column(db.String, nullable=False)
    designation_id = db.Column(db.String, db.ForeignKey('designations.id'), nullable=False)
    grades = db.relationship('Grade', backref='staff')
    # subjects = db.relationship('Subject', backref='staff')
    departments = db.relationship('Department', backref='staff')
    reports = db.relationship('Report', backref='staff')


class Designation(db.Model):
    __tablename__ = 'designations'
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    designation_name = db.Column(db.String)
    designation_code = db.Column(db.Integer)  


class Parent(db.Model):
    __tablename__ = 'parents_details'
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    mothers_first_name = db.Column(db.String)
    mothers_last_name = db.Column(db.String)
    mothers_contact = db.Column(db.String)
    mothers_email = db.Column(db.String)
    fathers_first_name = db.Column(db.String)
    fathers_last_name = db.Column(db.String)
    fathers_contact = db.Column(db.String)
    fathers_email = db.Column(db.String)
    guardian_first_name = db.Column(db.String)
    guardian_last_name = db.Column(db.String)
    guardian_contact = db.Column(db.String)
    guardian_email = db.Column(db.String)
    student_id = db.Column(db.String, db.ForeignKey('students.id'), nullable=False)


class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    subject_name = db.Column(db.String)
    # grade_id = db.Column(db.String, db.ForeignKey('grades.id'), nullable=False)
    # subject_teacher = db.Column(db.String, db.ForeignKey('staffs.id'), nullable=False)
    strands = db.relationship('Strand', backref='subject')
    sub_strands = db.relationship('SubStrand', backref='subject')
    learning_outcomes = db.relationship('LearningOutcome', backref='subject')
    assessment_rubics = db.relationship('AssessmentRubic', backref='subject')
    reports = db.relationship('Report', backref='subject')


class Strand(db.Model):
    __tablename__ = 'strands'
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    strand_name = db.Column(db.String)
    subject_id = db.Column(db.String, db.ForeignKey('subjects.id'), nullable=False)
    grade_id = db.Column(db.String, db.ForeignKey('grades.id'), nullable=False)
    sub_strands = db.relationship('SubStrand', backref='strand')
    learning_outcomes = db.relationship('LearningOutcome', backref='strand')
    assessment_rubics = db.relationship('AssessmentRubic', backref='strand')
    reports = db.relationship('Report', backref='strand')


class SubStrand(db.Model):
    __tablename__="substrands"
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    substrand_name=db.Column(db.String)
    strand_id = db.Column(db.String, db.ForeignKey('strands.id'), nullable=False)
    subject_id = db.Column(db.String, db.ForeignKey('subjects.id'), nullable=False)
    grade_id = db.Column(db.String, db.ForeignKey('grades.id'), nullable=False)
    learning_outcomes = db.relationship('LearningOutcome', backref='substrand')
    assessment_rubics = db.relationship('AssessmentRubic', backref='substrand')
    reports = db.relationship('Report', backref='substrand')



class LearningOutcome(db.Model):
    __tablename__="learning_outcomes"
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    learning_outcomes=db.Column(db.String)
    grade_id = db.Column(db.String, db.ForeignKey('grades.id'), nullable=False)    
    subject_id = db.Column(db.String, db.ForeignKey('subjects.id'), nullable=False)
    strand_id = db.Column(db.String, db.ForeignKey('strands.id'), nullable=False)
    sub_strand_id = db.Column(db.String, db.ForeignKey('substrands.id'), nullable=False)
    assessment_rubics = db.relationship('AssessmentRubic', backref='learning_outcome')
    reports = db.relationship('Report', backref='learning_outcome')



class AssessmentRubic(db.Model):
    __tablename__="assessment_rubics"
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    assessment_rubics=db.Column(db.String)
    assessment_rubic_mark=db.Column(db.Integer)
    grade_id = db.Column(db.String, db.ForeignKey('grades.id'), nullable=False)    
    subject_id = db.Column(db.String, db.ForeignKey('subjects.id'), nullable=False)
    strand_id = db.Column(db.String, db.ForeignKey('strands.id'), nullable=False)
    sub_strand_id = db.Column(db.String, db.ForeignKey('substrands.id'), nullable=False)
    learning_outcome_id = db.Column(db.String, db.ForeignKey('learning_outcomes.id'), nullable=False)
    reports = db.relationship('Report', backref='assessment_rubic')



class Department(db.Model):
    __tablename__="departments"
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    department_name=db.Column(db.String)
    department_head=db.Column(db.String)
    dept_staff=db.Column(db.String, db.ForeignKey('staffs.id'), nullable=False)

class Year(db.Model):
    __tablename__="years"
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    year_name=db.Column(db.Integer)
    reports = db.relationship('Report', backref='year')
    
    
class Term(db.Model):
    __tablename__="terms"
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    term_name=db.Column(db.String)
    reports = db.relationship('Report', backref='term')

class Report(db.Model):
    __tablename__="reports"
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    staff_id=db.Column(db.String, db.ForeignKey('staffs.id'), nullable=False)
    year_id=db.Column(db.String, db.ForeignKey('years.id'), nullable=False)
    term_id=db.Column(db.String, db.ForeignKey('terms.id'), nullable=False)
    grade_id=db.Column(db.String, db.ForeignKey('grades.id'), nullable=False)
    stream_id=db.Column(db.String, db.ForeignKey('streams.id'), nullable=False)
    student_id=db.Column(db.String, db.ForeignKey('students.id'), nullable=False)
    subject_id=db.Column(db.String, db.ForeignKey('subjects.id'), nullable=False)
    strand_id=db.Column(db.String, db.ForeignKey('strands.id'), nullable=False)
    substrand_id=db.Column(db.String, db.ForeignKey('substrands.id'), nullable=False)
    learning_outcomes_id=db.Column(db.String, db.ForeignKey('learning_outcomes.id'), nullable=False)
    assessment_rubics_id=db.Column(db.String, db.ForeignKey('assessment_rubics.id'), nullable=False)
    single_mark=db.Column(db.Integer)
    grade_ee = db.Column(db.Boolean, default=False)
    grade_me = db.Column(db.Boolean, default=False)
    grade_ae = db.Column(db.Boolean, default=False)
    grade_be = db.Column(db.Boolean, default=False)




class TokenBlocklist(db.Model):
    __tablename__ = 'tokenblocklist'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)
