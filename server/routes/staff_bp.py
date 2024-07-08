from flask import Blueprint, make_response, jsonify
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required,get_jwt
from models import Staff, db,Designation,Subject,Grade,Stream,TeacherSubjectGradeStream,teacher_grade_stream
from serializer import staffSchema,gradeSchema,streamSchema
from auth import admin_required, superAdmin_required
from datetime import datetime
from flask_bcrypt import Bcrypt

staff_bp = Blueprint('staff_bp', __name__)

bcrypt = Bcrypt()
api = Api(staff_bp)

post_args = reqparse.RequestParser()
post_args.add_argument('school_id', type=str, required=True, help='School Id is required')
post_args.add_argument('payroll_number', type=str, required=True, help='Payroll Number is required')
post_args.add_argument('first_name', type=str, required=True, help='First Name is required')
post_args.add_argument('last_name', type=str, required=True, help='Last Name is required')
post_args.add_argument('date_of_birth', type=str, required=True, help='Date of Birth is required')
post_args.add_argument('phone_number', type=str)
post_args.add_argument('alternative_contact', type=str)
post_args.add_argument('email_address', type=str)
post_args.add_argument('password', type=str, required=True, help='Password is required')
post_args.add_argument('designation_id', type=str, required=True, help='Designation ID is required')
post_args.add_argument('status', type=str, required=True, help='Status is required')
post_args.add_argument('photo_url', type=str, required=True, help='Photo is required')

patch_args = reqparse.RequestParser()
patch_args.add_argument('school_id', type=str)
patch_args.add_argument('payroll_number', type=str)
patch_args.add_argument('first_name', type=str)
patch_args.add_argument('last_name', type=str)
patch_args.add_argument('date_of_birth', type=str)
patch_args.add_argument('phone_number', type=str)
patch_args.add_argument('alternative_contact', type=str)
patch_args.add_argument('email_address', type=str)
patch_args.add_argument('password', type=str)
patch_args.add_argument('designation_id', type=str)
patch_args.add_argument('status', type=str)
patch_args.add_argument('photo_url', type=str)


post_args1 = reqparse.RequestParser()
post_args1.add_argument('staff_id', type=str, required=True, help='Teacher ID is required')
post_args1.add_argument('grade_id', type=str, required=True, help='Grade ID is required')
post_args1.add_argument('stream_id', type=str, required=True, help='Stream ID is required')
post_args1.add_argument('subject_id', type=str, required=True, help='Subject ID is required')

post_args2 = reqparse.RequestParser()
post_args2.add_argument('staff_id', type=str, required=True, help='Teacher ID is required')
post_args2.add_argument('grade_id', type=str, required=True, help='Grade ID is required')
post_args2.add_argument('stream_id', type=str, required=True, help='Stream ID is required')

patch_args1 = reqparse.RequestParser()
patch_args1.add_argument('staff_id', type=str, required=True, help='Staff ID is required')
patch_args1.add_argument('subject_id', type=str, required=True, help='Subject ID is required')
patch_args1.add_argument('grade_id', type=str, required=True, help='Grade ID is required')
patch_args1.add_argument('stream_id', type=str, required=True, help='Stream ID is required')

patch_args2 = reqparse.RequestParser()
patch_args2.add_argument('staff_id', type=str, required=True, help='Staff ID is required')
patch_args2.add_argument('grade_id', type=str, required=True, help='Grade ID is required')
patch_args2.add_argument('stream_id', type=str, required=True, help='Stream ID is required')

def get_school_id_from_session():
    claims = get_jwt()
    return claims.get("school_id")

class StaffDetails(Resource):
    @admin_required()
    def get(self):
        school_id = get_school_id_from_session()
        if not school_id:
            return make_response(jsonify({'error': 'School ID not found in session'}), 401)
        
        staff = Staff.query.filter_by(school_id=school_id).all()
        result = staffSchema.dump(staff, many=True)
        return make_response(jsonify(result), 200)

   
    def post(self):
        data = post_args.parse_args()

        # Check if the staff already exists
        existing_staff = Staff.query.filter_by(school_id=data['school_id'], payroll_number=data['payroll_number']).first()
        if existing_staff:
            return make_response(jsonify({"error": "Staff with the same payroll number already exists"}), 409)
        
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')

             

        date_of_birth = datetime.strptime(data["date_of_birth"], "%Y-%m-%d")
        new_staff = Staff(school_id=data['school_id'], payroll_number=data['payroll_number'],
                          first_name=data['first_name'], last_name=data['last_name'],
                          date_of_birth=date_of_birth, phone_number=data['phone_number'],
                          alternative_contact=data['alternative_contact'], email_address=data['email_address'],
                          password=hashed_password, designation_id=data['designation_id'],status=data['status'], photo_url=data['photo_url'])
        db.session.add(new_staff)
        db.session.commit()

        result = staffSchema.dump(new_staff)
        return make_response(jsonify(result), 201)

api.add_resource(StaffDetails, '/staffs')

class TeachersDetails(Resource):
    @admin_required()
    def get(self):
        school_id = get_school_id_from_session()
        if not school_id:
            return make_response(jsonify({'error': 'School ID not found in session'}), 401)
        
        teachers = Staff.query.join(Designation).filter(
            Designation.designation_code == 102,
            Staff.school_id == school_id
        ).all()
        
        teacher_list = []
        for teacher in teachers:
            teacher_data = {
                'id': teacher.id,
                'first_name': teacher.first_name,
                'last_name': teacher.last_name,
                'phone_number': teacher.phone_number,
                'email_address': teacher.email_address,
                'photo_url': teacher.photo_url,
                'subjects_grades_streams': [{
                    'subject_id': sgs.subject_id,
                    'subject_name': sgs.subject.subject_name,
                    'grade_id': sgs.grade_id,
                    'grade': sgs.grade.grade,
                    'stream_id': sgs.stream_id,
                    'stream': sgs.stream.stream_name
                } for sgs in teacher.teacher_subject_grade_streams]
            }
            teacher_list.append(teacher_data)
        
        return make_response(jsonify(teacher_list), 200)

api.add_resource(TeachersDetails, '/teachers')

class AssignTeacherSubject(Resource):
    @jwt_required()
    def post(self):
        school_id = get_school_id_from_session()
        if not school_id:
            return make_response(jsonify({'error': 'School ID not found in session'}), 401)
        data = post_args1.parse_args()

        # Check if the teacher exists
        teacher = Staff.query.get(data['staff_id'])
        if not teacher:
            return make_response(jsonify({"error": "Teacher not found"}), 404)

        # Check if the subject exists
        subject = Subject.query.get(data['subject_id'])
        if not subject:
            return make_response(jsonify({"error": "Subject not found"}), 404)

        # Check if the grade exists
        grade = Grade.query.get(data['grade_id'])
        if not grade:
            return make_response(jsonify({"error": "Grade not found"}), 404)

        # Check if the stream exists
        stream = Stream.query.get(data['stream_id'])
        if not stream:
            return make_response(jsonify({"error": "Stream not found"}), 404)

        # Check if the assignment already exists
        existing_assignment = TeacherSubjectGradeStream.query.filter_by(
            staff_id=data['staff_id'],
            subject_id=data['subject_id'],
            grade_id=data['grade_id'],
            stream_id=data['stream_id']
        ).first()

        if existing_assignment:
            return make_response(jsonify({"error": "Assignment already exists"}), 409)

        # Create a new assignment
        new_assignment = TeacherSubjectGradeStream(
            staff_id=data['staff_id'],
            subject_id=data['subject_id'],
            grade_id=data['grade_id'],
            stream_id=data['stream_id']
        )

        db.session.add(new_assignment)
        db.session.commit()

        return make_response(jsonify({"message": "Teacher assigned to subject successfully"}), 201)

api.add_resource(AssignTeacherSubject, '/assign-teacher-subject')


class UpdateTeacherSubject(Resource):
    @jwt_required()
    def patch(self):
        school_id = get_school_id_from_session()
        if not school_id:
            return make_response(jsonify({'error': 'School ID not found in session'}), 401)
        
        data = patch_args.parse_args()

        # Check if the teacher exists
        teacher = Staff.query.get(data['staff_id'])
        if not teacher:
            return make_response(jsonify({"error": "Teacher not found"}), 404)

        # Check if the subject exists
        subject = Subject.query.get(data['subject_id'])
        if not subject:
            return make_response(jsonify({"error": "Subject not found"}), 404)

        # Check if the grade exists
        grade = Grade.query.get(data['grade_id'])
        if not grade:
            return make_response(jsonify({"error": "Grade not found"}), 404)

        # Check if the stream exists
        stream = Stream.query.get(data['stream_id'])
        if not stream:
            return make_response(jsonify({"error": "Stream not found"}), 404)

        # Check if the assignment already exists
        existing_assignment = TeacherSubjectGradeStream.query.filter_by(
            staff_id=data['staff_id'],
            subject_id=data['subject_id'],
            grade_id=data['grade_id'],
            stream_id=data['stream_id']
        ).first()

        if not existing_assignment:
            return make_response(jsonify({"error": "Assignment does not exist"}), 404)

        # Update the existing assignment
        existing_assignment.staff_id = data['staff_id']
        existing_assignment.subject_id = data['subject_id']
        existing_assignment.grade_id = data['grade_id']
        existing_assignment.stream_id = data['stream_id']

        db.session.commit()

        return make_response(jsonify({"message": "Teacher assignment updated successfully"}), 200)



api.add_resource(UpdateTeacherSubject, '/update-teacher-subject')



class UpdateTeacherGradeStream(Resource):
    @jwt_required()
    def patch(self):
        data = patch_args2.parse_args()

        # Check if the teacher exists
        teacher = Staff.query.get(data['staff_id'])
        if not teacher:
            return make_response(jsonify({"error": "Teacher not found"}), 404)

        # Check if the grade exists
        grade = Grade.query.get(data['grade_id'])
        if not grade:
            return make_response(jsonify({"error": "Grade not found"}), 404)

        # Check if the stream exists
        stream = Stream.query.get(data['stream_id'])
        if not stream:
            return make_response(jsonify({"error": "Stream not found"}), 404)

        # Check if the assignment already exists
        existing_assignment = db.session.query(teacher_grade_stream).filter_by(
            staff_id=data['staff_id'],
            grade_id=data['grade_id'],
            stream_id=data['stream_id']
        ).first()

        if not existing_assignment:
            return make_response(jsonify({"error": "Assignment not found"}), 404)

        # Update the existing assignment
        existing_assignment.staff_id = data['staff_id']
        existing_assignment.grade_id = data['grade_id']
        existing_assignment.stream_id = data['stream_id']

        db.session.commit()

        return make_response(jsonify({"message": "Teacher assignment updated successfully"}), 200)

# Assign route to resource
api.add_resource(UpdateTeacherGradeStream, '/update-teacher-grade-stream')

class StaffById(Resource):
    # @admin_required()
    def get(self, id):
        staff = Staff.query.get(id)
        if not staff:
            return make_response(jsonify({"error": "Staff not found"}), 404)

        result = staffSchema.dump(staff)
        return make_response(jsonify(result), 200)

    @admin_required()
    def delete(self, id):
        staff = Staff.query.get(id)
        if not staff:
            return make_response(jsonify({"error": "Staff not found"}), 404)

        db.session.delete(staff)
        db.session.commit()
        return make_response(jsonify({"message": "Staff deleted successfully"}), 200)

    @admin_required()
    def patch(self, id):
        staff = Staff.query.get(id)
        if not staff:
            return make_response(jsonify({"error": "Staff not found"}), 404)

        data = patch_args.parse_args()
        for key, value in data.items():
            if value is not None:
                setattr(staff, key, value)

        db.session.commit()
        result = staffSchema.dump(staff)
        return make_response(jsonify(result), 200)

api.add_resource(StaffById, '/staffs/<string:id>')
