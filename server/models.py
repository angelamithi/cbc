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


class School(db.Model):
    __tablename__ = 'schools'
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String,nullable=False)
    code=db.Column(db.String,unique=True,nullable=False)
    address = db.Column(db.String)
    contact = db.Column(db.String)
    email=db.Column(db.String)
    students = db.relationship('Student', backref='school')
    categories = db.relationship('Category', backref='school')
    grades = db.relationship('Grade', backref='school')
    streams = db.relationship('Stream', backref='school')
    staffs = db.relationship('Staff', backref='school')
    parents = db.relationship('Parent', backref='school')
    subjects = db.relationship('Subject', backref='school')
    departments = db.relationship('Department', backref='school')
    formative_reports = db.relationship('FormativeReport', backref='school')
    summative_reports= db.relationship('SummativeReport', backref='school')
    behaviour_reports= db.relationship('BehaviourReport', backref='school')


class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    school_id = db.Column(db.String, db.ForeignKey('schools.id'), nullable=False)
    admission_number = db.Column(db.String, unique=True, nullable=False)
    joined_date = db.Column(db.Date, nullable=False)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    date_of_birth = db.Column(db.Date, nullable=False)
    birth_certificate_number = db.Column(db.String)
    photo_url = db.Column(db.String)
    status=db.Column(db.String,nullable=False)
    grade_id = db.Column(db.String, db.ForeignKey('grades.id'), nullable=False)
    stream_id = db.Column(db.String, db.ForeignKey('streams.id'), nullable=False)
    parents = db.relationship('Parent', backref='student')
    formative_reports = db.relationship('FormativeReport', backref='student')
    summative_reports= db.relationship('SummativeReport', backref='student')
    behaviour_reports= db.relationship('BehaviourReport', backref='student')


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    school_id = db.Column(db.String, db.ForeignKey('schools.id'), nullable=False)
    category_name = db.Column(db.String)
    grades = db.relationship('Grade', backref='category')



class Grade(db.Model):
    __tablename__ = 'grades'
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    school_id = db.Column(db.String, db.ForeignKey('schools.id'), nullable=False)
    grade = db.Column(db.String)
    category_id = db.Column(db.String, db.ForeignKey('categories.id'), nullable=False)
    students = db.relationship('Student', backref='grade')
    strands = db.relationship('Strand', backref='grade')
    substrands = db.relationship('SubStrand', backref='grade')
    learning_outcomes = db.relationship('LearningOutcome', backref='grade')
    assessment_rubrics = db.relationship('AssessmentRubic', backref='grade')
    formative_reports = db.relationship('FormativeReport', backref='grade')
    summative_reports= db.relationship('SummativeReport', backref='grade')
    behaviour_reports= db.relationship('BehaviourReport', backref='grade')

    teacher_subject_grade_streams=db.relationship('TeacherSubjectGradeStream',back_populates='grade')
    grade_stream_teacher=db.relationship('GradeStreamClassTeacher', back_populates='grade')
  



   
class Stream(db.Model):
    __tablename__ = 'streams'
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    school_id = db.Column(db.String, db.ForeignKey('schools.id'), nullable=False)
    stream_name = db.Column(db.String)
    students = db.relationship('Student', backref='stream')
    formative_reports = db.relationship('FormativeReport', backref='stream')
    teacher_subject_grade_streams=db.relationship('TeacherSubjectGradeStream',back_populates='stream')
    grade_stream_teacher=db.relationship('GradeStreamClassTeacher', back_populates='stream')
    summative_reports= db.relationship('SummativeReport', backref='stream')

    # Add back_populates for other relationships if needed

class GradeStreamClassTeacher(db.Model):
    __tablename__='grade_stream_class_teacher'
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    staff_id = db.Column(db.String, db.ForeignKey('staffs.id'), nullable=False)
    grade_id = db.Column(db.String, db.ForeignKey('grades.id'), nullable=False)
    stream_id = db.Column(db.String, db.ForeignKey('streams.id'), nullable=False)

    staff = db.relationship('Staff', back_populates='grade_stream_teacher')
    grade = db.relationship('Grade', back_populates='grade_stream_teacher')
    stream = db.relationship('Stream', back_populates='grade_stream_teacher')
    behaviour_reports = db.relationship('BehaviourReport', backref='class_teacher')
    summative_reports = db.relationship('SummativeReport', backref='class_teacher')


class TeacherSubjectGradeStream(db.Model):
    __tablename__ = 'teacher_subject_grade_stream'
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    staff_id = db.Column(db.String, db.ForeignKey('staffs.id'), nullable=False)
    subject_id = db.Column(db.String, db.ForeignKey('subjects.id'), nullable=False)
    grade_id = db.Column(db.String, db.ForeignKey('grades.id'), nullable=False)
    stream_id = db.Column(db.String, db.ForeignKey('streams.id'), nullable=False)
    
    # Define relationships with back_populates
    staff = db.relationship('Staff', back_populates='teacher_subject_grade_streams')
    subject = db.relationship('Subject', back_populates='teacher_subject_grade_streams')
    grade = db.relationship('Grade', back_populates='teacher_subject_grade_streams')
    stream = db.relationship('Stream', back_populates='teacher_subject_grade_streams')
    summative_reports = db.relationship('SummativeReport', backref='subject_teacher')

   
  

class Staff(db.Model):
    __tablename__ = 'staffs'
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    school_id = db.Column(db.String, db.ForeignKey('schools.id'), nullable=False)
    payroll_number = db.Column(db.String)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    date_of_birth = db.Column(db.Date, nullable=False)
    phone_number = db.Column(db.String)
    alternative_contact = db.Column(db.String)
    email_address = db.Column(db.String)
    password = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)
    photo_url = db.Column(db.String)
    designation_id = db.Column(db.String, db.ForeignKey('designations.id'), nullable=False)
    teacher_subject_grade_streams=db.relationship('TeacherSubjectGradeStream',back_populates='staff')
    formative_reports = db.relationship('FormativeReport', backref='staff')
    grade_stream_teacher=db.relationship('GradeStreamClassTeacher', back_populates='staff')



class Designation(db.Model):
    __tablename__ = 'designations'
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    designation_name = db.Column(db.String)
    designation_code = db.Column(db.Integer)
    school_id = db.Column(db.String, db.ForeignKey('schools.id'), nullable=False)
    staff = db.relationship('Staff', backref='designation')


class Parent(db.Model):
    __tablename__ = 'parents_details'
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    school_id = db.Column(db.String, db.ForeignKey('schools.id'), nullable=False)
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
    status=db.Column(db.String,nullable=False)
    student_id = db.Column(db.String, db.ForeignKey('students.id'), nullable=False)


class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    school_id = db.Column(db.String, db.ForeignKey('schools.id'), nullable=False)
    subject_name = db.Column(db.String)
    strands = db.relationship('Strand', backref='subject')
    sub_strands = db.relationship('SubStrand', backref='subject')
    learning_outcomes = db.relationship('LearningOutcome', backref='subject')
    assessment_rubics = db.relationship('AssessmentRubic', backref='subject')
    formative_reports = db.relationship('FormativeReport', backref='subject')
    summative_reports= db.relationship('SummativeReport', backref='subject')
    teacher_subject_grade_streams=db.relationship('TeacherSubjectGradeStream',back_populates='subject')


class Strand(db.Model):
    __tablename__ = 'strands'
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    strand_name = db.Column(db.String)
    subject_id = db.Column(db.String, db.ForeignKey('subjects.id'), nullable=False)
    grade_id = db.Column(db.String, db.ForeignKey('grades.id'), nullable=False)
    sub_strands = db.relationship('SubStrand', backref='strand')
    learning_outcomes = db.relationship('LearningOutcome', backref='strand')


class SubStrand(db.Model):
    __tablename__ = "substrands"
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    substrand_name = db.Column(db.String)
    strand_id = db.Column(db.String, db.ForeignKey('strands.id'), nullable=False)
    subject_id = db.Column(db.String, db.ForeignKey('subjects.id'), nullable=False)
    grade_id = db.Column(db.String, db.ForeignKey('grades.id'), nullable=False)
    learning_outcomes = db.relationship('LearningOutcome', backref='substrand')
    assessment_rubics = db.relationship('AssessmentRubic', backref='substrand')



class LearningOutcome(db.Model):
    __tablename__ = "learning_outcomes"
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    learning_outcomes = db.Column(db.String)
    grade_id = db.Column(db.String, db.ForeignKey('grades.id'), nullable=False)
    subject_id = db.Column(db.String, db.ForeignKey('subjects.id'), nullable=False)
    strand_id = db.Column(db.String, db.ForeignKey('strands.id'), nullable=False)
    sub_strand_id = db.Column(db.String, db.ForeignKey('substrands.id'), nullable=False)
    assessment_rubics = db.relationship('AssessmentRubic', backref='learning_outcome')



class AssessmentRubic(db.Model):
    __tablename__ = "assessment_rubics"
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    assessment_rubics = db.Column(db.String)
    assessment_rubic_mark=db.Column(db.Integer)
    grade_id = db.Column(db.String, db.ForeignKey('grades.id'), nullable=False)
    subject_id = db.Column(db.String, db.ForeignKey('subjects.id'), nullable=False)
    strand_id = db.Column(db.String, db.ForeignKey('strands.id'), nullable=False)
    sub_strand_id = db.Column(db.String, db.ForeignKey('substrands.id'), nullable=False)
    learning_outcome_id = db.Column(db.String, db.ForeignKey('learning_outcomes.id'), nullable=False)
    formative_reports = db.relationship('FormativeReport', backref='assessment_rubic')
   


class Department(db.Model):
    __tablename__ = "departments"
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    school_id = db.Column(db.String, db.ForeignKey('schools.id'), nullable=False)
    department_name = db.Column(db.String)
    department_head = db.Column(db.String)
    dept_staff = db.Column(db.String, db.ForeignKey('staffs.id'), nullable=False)


class Year(db.Model):
    __tablename__ = "years"
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    year_name = db.Column(db.Integer)
    formative_reports = db.relationship('FormativeReport', backref='year')
    summative_reports= db.relationship('SummativeReport', backref='year')
    behaviour_reports= db.relationship('BehaviourReport', backref='year')


class Term(db.Model):
    __tablename__ = "terms"
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    term_name = db.Column(db.String)
    summative_reports= db.relationship('SummativeReport', backref='term')
    


class FormativeReport(db.Model):
    __tablename__ = "formative_reports"
    id = db.Column(db.String, primary_key=True,default=generate_uuid)   
    school_id = db.Column(db.String, db.ForeignKey('schools.id'), nullable=False)
    student_id = db.Column(db.String, db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.String, db.ForeignKey('subjects.id'), nullable=False)
    grade_id = db.Column(db.String, db.ForeignKey('grades.id'), nullable=False)
    year_id = db.Column(db.String, db.ForeignKey('years.id'), nullable=False)
    staff_id = db.Column(db.String, db.ForeignKey('staffs.id'), nullable=False)
    stream_id = db.Column(db.String, db.ForeignKey('streams.id'), nullable=False)
    assessment_rubic_id = db.Column(db.String, db.ForeignKey('assessment_rubics.id'), nullable=False)
    is_selected = db.Column(db.Boolean, nullable=False)
    single_mark = db.Column(db.Integer, nullable=False)

class SummativeReport(db.Model):
    __tablename__ = "summative_reports"
    id = db.Column(db.String, primary_key=True, default=generate_uuid)   
    school_id = db.Column(db.String, db.ForeignKey('schools.id'), nullable=False)
    student_id = db.Column(db.String, db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.String, db.ForeignKey('subjects.id'), nullable=False)
    grade_id = db.Column(db.String, db.ForeignKey('grades.id'), nullable=False)
    year_id = db.Column(db.String, db.ForeignKey('years.id'), nullable=False)
    term_id = db.Column(db.String, db.ForeignKey('terms.id'), nullable=False)
    subject_teacher_id = db.Column(db.String, db.ForeignKey('teacher_subject_grade_stream.id'), nullable=False)
    stream_id = db.Column(db.String, db.ForeignKey('streams.id'), nullable=False)
    class_teacher_id = db.Column(db.String, db.ForeignKey('grade_stream_class_teacher.id'), nullable=False)
    exam_1_marks = db.Column(db.Integer)
    exam_2_marks = db.Column(db.Integer)
    exam_3_marks = db.Column(db.Integer)
    average_grade = db.Column(db.Float)
    general_remarks = db.Column(db.Text)
    class_teachers_comments = db.Column(db.Text)

  


class BehaviourReport(db.Model):
    __tablename__ = "behaviour_reports"
    id = db.Column(db.String, primary_key=True, default=generate_uuid)   
    school_id = db.Column(db.String, db.ForeignKey('schools.id'), nullable=False)
    student_id = db.Column(db.String, db.ForeignKey('students.id'), nullable=False)
    grade_id = db.Column(db.String, db.ForeignKey('grades.id'), nullable=False)
    year_id = db.Column(db.String, db.ForeignKey('years.id'), nullable=False)
    class_teacher_id = db.Column(db.String, db.ForeignKey('grade_stream_class_teacher.id'), nullable=False)
    stream_id = db.Column(db.String, db.ForeignKey('streams.id'), nullable=False)   
    behaviour_goal = db.Column(db.String, nullable=False)
    behaviour_goal_assessment = db.Column(db.Text, nullable=False)
    class_teachers_comments = db.Column(db.Text, nullable=False)





   
  


class TokenBlocklist(db.Model):
    __tablename__ = 'tokenblocklist'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)