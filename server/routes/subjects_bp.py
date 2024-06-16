from flask import Blueprint, make_response, jsonify
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required
from models import Subject, db
from serializer import subjectSchema
from auth import admin_required, superAdmin_required

subjects_bp = Blueprint('subjects_bp', __name__)
api = Api(subjects_bp)

post_args = reqparse.RequestParser()
post_args.add_argument('school_id', type=str, required=True, help='School Id is required')
post_args.add_argument('subject_name', type=str, required=True, help='Subject Name is required')

patch_args = reqparse.RequestParser()
patch_args.add_argument('school_id', type=str)
patch_args.add_argument('subject_name', type=str)

class SubjectDetails(Resource):
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

api.add_resource(SubjectDetails, '/subjects')

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
