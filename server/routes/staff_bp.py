from flask import Blueprint, make_response, jsonify
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required,get_jwt
from models import Staff, db,Designation,Subject,Grade,Stream,TeacherSubjectGradeStream
from serializer import staffSchema,gradeSchema,streamSchema,teacher_subject_grade_schema
from auth import admin_required, superAdmin_required
from datetime import datetime
from flask_bcrypt import Bcrypt
from sqlalchemy import text,update
from sqlalchemy.exc import SQLAlchemyError


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
post_args2.add_argument('stream_id', type=str, required=True, help='Sream ID is required')
post_args2.add_argument('grade_id', type=str, help='Grade ID is required', required=True)



patch_args1 = reqparse.RequestParser()
patch_args1.add_argument('staff_id', type=str, required=True, help='Staff ID is required')
patch_args1.add_argument('subject_id', type=str, required=True, help='Subject ID is required')
patch_args1.add_argument('grade_id', type=str, required=True, help='Grade ID is required')
patch_args1.add_argument('stream_id', type=str, required=True, help='Stream ID is required')



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
         # Check if designation_id exists
        designation = Designation.query.filter_by(id=data['designation_id']).first()
        if not designation:
            return make_response(jsonify({"error": "Designation ID does not exist"}), 404)
        
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
               }
            teacher_list.append(teacher_data)
        
        return make_response(jsonify(teacher_list), 200)

api.add_resource(TeachersDetails, '/teachers')

class GetClassTeachersDetails(Resource):
   
    @jwt_required()
    def get(self, stream_id, grade_id):
        # Fetch the specific TeacherSubjectGradeStream instance
        school_id = get_school_id_from_session()
        if not school_id:
            return make_response(jsonify({'error': 'School ID not found in session'}), 401)
        tsgs_instance = TeacherSubjectGradeStream.query.filter_by(
            stream_id=stream_id, grade_id=grade_id
        ).first()

        if not tsgs_instance:
            return {'message': 'Stream or Grade not found'}, 404

        # Fetch the specific stream
        stream = Stream.query.filter_by(id=stream_id, school_id=school_id).first()

        if not stream:
            return {'message': 'Stream not found in the specified school'}, 404

        # Fetch the class teacher details from the stream
        class_teacher = stream.class_teacher

        if not class_teacher:
            return {'message': 'Class teacher not found'}, 404

        return {
            'class_teacher_id': class_teacher.id,
            'class_teacher_first_name': class_teacher.first_name,
            'class_teacher_last_name': class_teacher.last_name,
            'class_teacher_email': class_teacher.email_address,
            'class_teacher_phone': class_teacher.phone_number,
        }



api.add_resource(GetClassTeachersDetails, '/class_teacher/<string:grade_id>/<string:stream_id>')


class AssignClassTeacher(Resource):
    def post(self):
        data = post_args.parse_args()
        stream_id = data['stream_id']
        staff_id = data['staff_id']
        grade_id = data['grade_id']
        
        # Get the school_id from session (replace with your actual session logic)
        school_id = get_school_id_from_session()
        if not school_id:
            return jsonify({"message": "School ID not found in session"}), 400
        
        if not (staff_id and grade_id and stream_id):
            return jsonify({'error': 'Missing parameters'}), 400

        # Fetch the staff member
        staff = Staff.query.get(staff_id)
        if not staff:
            return jsonify({'error': 'Staff not found'}), 404

        # Fetch the grade
        grade = Grade.query.get(grade_id)
        if not grade:
            return jsonify({'error': 'Grade not found'}), 404

        # Fetch the stream
        stream = Stream.query.get(stream_id)
        if not stream:
            return jsonify({'error': 'Stream not found'}), 404

        # Update the class_teacher_id in the Stream model
        stream.class_teacher_id = staff_id
        db.session.commit()

        return jsonify({'message': 'Class teacher assigned successfully'}), 200

# # Register the resource with your API
api.add_resource(AssignClassTeacher, '/assign_class_teacher')



class TeachersByGrade(Resource):
    @admin_required()
    def get(self, grade_id):
        school_id = get_school_id_from_session()
        if not school_id:
            return make_response(jsonify({'error': 'School ID not found in session'}), 401)
        
        teachers = Staff.query \
            .join(Staff.teacher_subject_grade_streams) \
            .filter(
                Staff.school_id == school_id,
                TeacherSubjectGradeStream.grade_id == grade_id
            ) \
            .all()
    
        teacher_list = []
        for teacher in teachers:
            teacher_data = {
                'id': teacher.id,
                'first_name': teacher.first_name,
                'last_name': teacher.last_name,
                'phone_number': teacher.phone_number,
                'email_address': teacher.email_address,
                'photo_url': teacher.photo_url,
            }
            teacher_list.append(teacher_data)
        
        return make_response(jsonify(teacher_list), 200)




api.add_resource(TeachersByGrade, '/teachers/grades/<string:grade_id>')



class TeachersByGradeAndStream(Resource):
    @admin_required()
    def get(self, grade_id, stream_id):
        school_id = get_school_id_from_session()
        if not school_id:
            return make_response(jsonify({'error': 'School ID not found in session'}), 401)
        
        teachers = Staff.query \
            .join(Staff.teacher_subject_grade_streams) \
            .filter(
                Staff.school_id == school_id,
                TeacherSubjectGradeStream.grade_id == grade_id,
                TeacherSubjectGradeStream.stream_id == stream_id
            ) \
            .all()
    
        teacher_list = []
        for teacher in teachers:
            teacher_data = {
                'id': teacher.id,
                'first_name': teacher.first_name,
                'last_name': teacher.last_name,
                'phone_number': teacher.phone_number,
                'email_address': teacher.email_address,
                'photo_url': teacher.photo_url,
            }
            teacher_list.append(teacher_data)
        
        return make_response(jsonify(teacher_list), 200)

api.add_resource(TeachersByGradeAndStream, '/teachers/grades/<string:grade_id>/streams/<string:stream_id>')

class AssignTeacherSubject(Resource):
    @jwt_required()
    def post(self):
        try:
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

        except SQLAlchemyError as e:
            db.session.rollback()
            return make_response(jsonify({"error": "Database error"}), 500)

        except Exception as e:
            return make_response(jsonify({"error": str(e)}), 500)

api.add_resource(AssignTeacherSubject, '/assign-teacher-subject')

        #




class UpdateTeacherAssignment(Resource):
     @jwt_required()
     def patch(self,id):
        
            school_id = get_school_id_from_session()
            if not school_id:
                return make_response(jsonify({'error': 'School ID not found in session'}), 401)
            assignment = TeacherSubjectGradeStream.query.get(id)
            if not assignment:
                return make_response(jsonify({"error": "Assignment not found"}), 404)
            data = patch_args1.parse_args()

            
            for key, value in data.items():
                if value is not None:
                     setattr(assignment, key, value)

            db.session.commit()
            result = teacher_subject_grade_schema.dump(assignment)
            return make_response(jsonify(result), 200)

           

api.add_resource(UpdateTeacherAssignment, '/update-teacher-subject/<string:id>')





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
