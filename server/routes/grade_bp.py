from flask import Blueprint, make_response, jsonify
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required
from models import Grade, db
from serializer import gradeSchema
from auth import admin_required, superAdmin_required

grade_bp = Blueprint('grade_bp', __name__)
api = Api(grade_bp)

post_args = reqparse.RequestParser()
post_args.add_argument('school_id', type=str, required=True, help='School Id is required')
post_args.add_argument('grade', type=str, required=True, help='Grade is required')
post_args.add_argument('class_teacher_id', type=str, required=True, help='Class Teacher ID is required')
post_args.add_argument('category_id', type=str, required=True, help='Category ID is required')

patch_args = reqparse.RequestParser()
patch_args.add_argument('school_id', type=str)
patch_args.add_argument('grade', type=str)
patch_args.add_argument('class_teacher_id', type=str)
patch_args.add_argument('category_id', type=str)

class GradeDetails(Resource):
    @jwt_required()
    def get(self):
        grades = Grade.query.all()
        result = gradeSchema.dump(grades, many=True)
        return make_response(jsonify(result), 200)

    @admin_required()
    def post(self):
        data = post_args.parse_args()

        # Check if the grade already exists
        existing_grade = Grade.query.filter_by(school_id=data['school_id'], grade=data['grade']).first()
        if existing_grade:
            return make_response(jsonify({"error": "Grade already exists for this school"}), 409)

        new_grade = Grade(school_id=data['school_id'], grade=data['grade'],
                          class_teacher_id=data['class_teacher_id'], category_id=data['category_id'])
        db.session.add(new_grade)
        db.session.commit()

        result = gradeSchema.dump(new_grade)
        return make_response(jsonify(result), 201)

api.add_resource(GradeDetails, '/grades')

class GradeById(Resource):
    @jwt_required()
    def get(self, id):
        grade = Grade.query.get(id)
        if not grade:
            return make_response(jsonify({"error": "Grade not found"}), 404)

        result = gradeSchema.dump(grade)
        return make_response(jsonify(result), 200)

    @superAdmin_required()
    def delete(self, id):
        grade = Grade.query.get(id)
        if not grade:
            return make_response(jsonify({"error": "Grade not found"}), 404)

        db.session.delete(grade)
        db.session.commit()
        return make_response(jsonify({"message": "Grade deleted successfully"}), 200)

    @superAdmin_required()
    def patch(self, id):
        grade = Grade.query.get(id)
        if not grade:
            return make_response(jsonify({"error": "Grade not found"}), 404)

        data = patch_args.parse_args()
        for key, value in data.items():
            if value is not None:
                setattr(grade, key, value)

        db.session.commit()
        result = gradeSchema.dump(grade)
        return make_response(jsonify(result), 200)

api.add_resource(GradeById, '/grades/<string:id>')
