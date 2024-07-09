from flask import Blueprint, make_response, jsonify
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required
from models import Subject, db,TeacherSubjectGradeStream
from serializer import subjectSchema
from auth import admin_required, superAdmin_required
from sqlalchemy.orm import joinedload

subjects_bp = Blueprint('subjects_bp', __name__)
api = Api(subjects_bp)

post_args = reqparse.RequestParser()
post_args.add_argument('school_id', type=str, required=True, help='School Id is required')
post_args.add_argument('subject_name', type=str, required=True, help='Subject Name is required')

patch_args = reqparse.RequestParser()
patch_args.add_argument('school_id', type=str)
patch_args.add_argument('subject_name', type=str)

class Subjects(Resource):
    @jwt_required()
    def get(self):
        subjects = Subject.query.all()
        result = subjectSchema.dump(subjects, many=True)
        return make_response(jsonify(result), 200)

    


    @superAdmin_required()
    def post(self):
        data = post_args.parse_args()

        # Check if the subject already exists
        existing_subject = Subject.query.filter_by(school_id=data['school_id'], subject_name=data['subject_name']).first()
        if existing_subject:
            return make_response(jsonify({"error": "Subject already exists for this school"}), 409)

        new_subject = Subject(school_id=data['school_id'], subject_name=data['subject_name'])
        db.session.add(new_subject)
        db.session.commit()

        result = subjectSchema.dump(new_subject)
        return make_response(jsonify(result), 201)

api.add_resource(Subjects, '/subjects')

class SubjectsByGrade(Resource):
    @jwt_required()
    def get(self, grade_id):
        # Fetch teacher subject grade streams based on the grade_id
        teacher_subject_grade_streams = TeacherSubjectGradeStream.query.filter_by(grade_id=grade_id).all()
        
        # Extract the subject_ids from the above records
        subject_ids = [tsgs.subject_id for tsgs in teacher_subject_grade_streams]
        
        # Fetch the subjects based on the subject_ids
        subjects = Subject.query.filter(Subject.id.in_(subject_ids)).all()
        
        # Serialize the results
        result = subjectSchema.dump(subjects, many=True)
        
        return make_response(jsonify(result), 200)

api.add_resource(SubjectsByGrade, '/subjects/grade/<string:grade_id>')


class SubjectsAndTeachersByGrade(Resource):
    @jwt_required()
    def get(self, grade_id):
        # Query to get subjects and their respective teachers for a specific grade
        teacher_subject_grade_streams = db.session.query(
            TeacherSubjectGradeStream
        ).options(
            joinedload(TeacherSubjectGradeStream.subject),
            joinedload(TeacherSubjectGradeStream.staff)
        ).filter(
            TeacherSubjectGradeStream.grade_id == grade_id
        ).all()
        
        # Prepare the result
        result = []
        for tsgs in teacher_subject_grade_streams:
            result.append({
                'subject_id': tsgs.subject.id,
                'subject_name': tsgs.subject.subject_name,
                'teacher_id': tsgs.staff.id,
                'teacher_name': f"{tsgs.staff.first_name} {tsgs.staff.last_name}"
            })
        
        return make_response(jsonify(result), 200)

api.add_resource(SubjectsAndTeachersByGrade, '/subjects-teachers/grade/<string:grade_id>')

class SubjectsByTeacherAndGrade(Resource):
    @jwt_required()
    def get(self, teacher_id, grade_id=None):
        # Query to get subjects taught by a specific teacher
        query = db.session.query(
            TeacherSubjectGradeStream
        ).options(
            joinedload(TeacherSubjectGradeStream.subject),
            joinedload(TeacherSubjectGradeStream.grade),
            joinedload(TeacherSubjectGradeStream.stream)
        ).filter(
            TeacherSubjectGradeStream.staff_id == teacher_id
        )
        
        if grade_id:
            query = query.filter(
                TeacherSubjectGradeStream.grade_id == grade_id
            )
        
        teacher_subjects = query.all()
        
        # Prepare the result
        result = []
        for tsgs in teacher_subjects:
            result.append({
                'subject_id': tsgs.subject.id,
                'subject_name': tsgs.subject.subject_name,
                'grade_id': tsgs.grade.id,
                'grade_name': tsgs.grade.grade,
                'stream_id': tsgs.stream.id,
                'stream_name': tsgs.stream.stream_name if tsgs.stream else None
            })
        
        return make_response(jsonify(result), 200)

api.add_resource(SubjectsByTeacherAndGrade, '/subjects/teacher/<string:teacher_id>/grade/<string:grade_id>')

class SubjectById(Resource):
    @jwt_required()
    def get(self, id):
        subject = Subject.query.get(id)
        if not subject:
            return make_response(jsonify({"error": "Subject not found"}), 404)

        result = subjectSchema.dump(subject)
        return make_response(jsonify(result), 200)

    @superAdmin_required()
    def delete(self, id):
        subject = Subject.query.get(id)
        if not subject:
            return make_response(jsonify({"error": "Subject not found"}), 404)

        db.session.delete(subject)
        db.session.commit()
        return make_response(jsonify({"message": "Subject deleted successfully"}), 200)

    @superAdmin_required()
    def patch(self, id):
        subject = Subject.query.get(id)
        if not subject:
            return make_response(jsonify({"error": "Subject not found"}), 404)

        data = patch_args.parse_args()
        for key, value in data.items():
            if value is not None:
                setattr(subject, key, value)

        db.session.commit()
        result = subjectSchema.dump(subject)
        return make_response(jsonify(result), 200)

api.add_resource(SubjectById, '/subjects/<string:id>')
