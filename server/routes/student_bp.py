from flask import Blueprint, make_response, jsonify,session
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_restful import Api, Resource, abort, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity,get_jwt
from models import Student, db
from serializer import studentSchema
from auth import admin_required,superAdmin_required
from datetime import datetime

student_bp = Blueprint('student_bp', __name__)
api = Api(student_bp)


post_args = reqparse.RequestParser()
post_args.add_argument('school_id', type=str, required=True,
                       help='School Id is required')
post_args.add_argument('admission_number', type=str,
                       required=True, help='Admission Number is required')
post_args.add_argument('joined_date', type=str,
                       required=True, help='Joined Date is required')
post_args.add_argument('first_name', type=str, required=True, help='First Name is required')
post_args.add_argument('last_name', type=str, required=True, help='Last Name is required')
post_args.add_argument('date_of_birth', type=str,
                       required=True, help='Date of Birth is required')
post_args.add_argument('birth_certificate_number', type=str,
                       required=True, help='Birth Certificate Number is required')

post_args.add_argument('photo_url', type=str, help='Photo is required')
post_args.add_argument('grade_id', type=str, required=True, help='Grade Id is required')
post_args.add_argument('stream_id', type=str, required=True, help='Stream Id is required')


patch_args = reqparse.RequestParser()

patch_args.add_argument('school_id', type=str)
patch_args.add_argument('admission_number', type=str)
patch_args.add_argument('joined_date', type=str)
patch_args.add_argument('first_name', type=str)
patch_args.add_argument('last_name', type=str)
patch_args.add_argument('date_of_birth', type=str)
patch_args.add_argument('birth_certificate_number', type=str)
patch_args.add_argument('photo_url', type=str)
patch_args.add_argument('grade_id', type=str)
patch_args.add_argument('stream_id', type=str)



def get_school_id_from_session():
    claims = get_jwt()
    return claims.get("school_id")

class StudentDetails(Resource):
    @jwt_required()
    def get(self):
        school_id = get_school_id_from_session()
        if not school_id:
            return make_response(jsonify({'error': 'School ID not found in session'}), 401)

        students_details = Student.query.filter_by(school_id=school_id).all()
        result = studentSchema.dump(students_details, many=True)
        return make_response(jsonify(result), 200)

    @admin_required()
    def post(self):
        data = post_args.parse_args()

        student = Student.query.filter_by(admission_number=data['admission_number']).first()
        if student:
            return make_response(jsonify({"error": "Student with the same admission number already exists"}), 409)

        joined_date = datetime.strptime(data["joined_date"], "%Y-%m-%d")
        date_of_birth = datetime.strptime(data["date_of_birth"], "%Y-%m-%d")

        new_student = Student(
            school_id=data['school_id'], 
            admission_number=data['admission_number'],
            joined_date=joined_date, 
            date_of_birth=date_of_birth, 
            first_name=data['first_name'],
            last_name=data['last_name'], 
            birth_certificate_number=data['birth_certificate_number'],
            photo_url=data["photo_url"], 
            grade_id=data['grade_id'], 
            stream_id=data['stream_id']
        )
        db.session.add(new_student)
        db.session.commit()

        result = studentSchema.dump(new_student)
        return make_response(jsonify(result), 201)

api.add_resource(StudentDetails, '/students')


class StudentById(Resource):
    @jwt_required()
    def get(self, id):
        school_id = get_school_id_from_session()
        if not school_id:
            return make_response(jsonify({'error': 'School ID not found in session'}), 401)

        single_student = Student.query.filter_by(school_id=school_id, id=id).first()

        if not single_student:
            return make_response(jsonify({"error": f"Student with id {id} does not exist in the specified school"}), 404)

        result = studentSchema.dump(single_student)
        return make_response(jsonify(result), 200)

    @superAdmin_required()
    def delete(self, id):
        school_id = get_school_id_from_session()
        if not school_id:
            return make_response(jsonify({'error': 'School ID not found in session'}), 401)

        single_student = Student.query.filter_by(school_id=school_id, id=id).first()

        if not single_student:
            return make_response(jsonify({"error": f"Student with id {id} does not exist in the specified school"}), 404)

        db.session.delete(single_student)
        db.session.commit()

        return make_response(jsonify({"message": f"Student with id {id} has been deleted"}), 200)

    @admin_required()
    def patch(self, id):
        school_id = get_school_id_from_session()
        if not school_id:
            return make_response(jsonify({'error': 'School ID not found in session'}), 401)

        single_student = Student.query.filter_by(school_id=school_id, id=id).first()

        if not single_student:
            return make_response(jsonify({"error": f"Student with id {id} does not exist in the specified school"}), 404)

        data = patch_args.parse_args()

        for key, value in data.items():
            if value is None:
                continue
            setattr(single_student, key, value)
        db.session.commit()

        result = studentSchema.dump(single_student)
        return make_response(jsonify(result), 200)



api.add_resource(StudentById, '/students/<string:id>')