from flask import Blueprint, make_response, jsonify,session,request
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_restful import Api, Resource, abort, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity,get_jwt
from models import Student, db,Grade,Staff,BehaviourReport,SummativeReport,FormativeReport,Year,TeacherSubjectGradeStream,GradeStreamClassTeacher,Term,AssessmentRubic
from serializer import studentSchema,grade_stream_class_teacher_schema
from auth import admin_required,superAdmin_required
from datetime import datetime
from sqlalchemy.exc import IntegrityError

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
post_args.add_argument('status', type=str, required=True, help='Status is required')


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
patch_args.add_argument('status', type=str)



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

        try:
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
                stream_id=data['stream_id'],
                status=data['status']
            )
            db.session.add(new_student)
            db.session.flush()  # Ensure the new_student ID is available

            # Fetch the current year_id
            current_year = datetime.now().year
            year = Year.query.filter_by(year_name=current_year).first()
            if not year:
                return make_response(jsonify({"error": "Year not found"}), 404)

            year_id = year.id

            # Fetch subject_ids and corresponding subject_teacher_ids for the grade and stream
            teacher_subjects = TeacherSubjectGradeStream.query.filter_by(
                grade_id=data['grade_id'], 
                stream_id=data['stream_id']
            ).all()

            # Fetch class teacher ID for the specific grade and stream
            class_teacher = GradeStreamClassTeacher.query.filter_by(
                grade_id=data['grade_id'], 
                stream_id=data['stream_id']
            ).first()
            if not class_teacher:
                return make_response(jsonify({"error": "Class teacher not found"}), 404)

            class_teacher_id = class_teacher.staff_id

            # Fetch all term IDs
            terms = Term.query.all()
            term_ids = [term.id for term in terms]

            # Create Formative Reports for each subject 
            for ts in teacher_subjects:
                # Fetch the corresponding assessment rubric IDs for each subject
                assessment_rubrics = AssessmentRubic.query.filter_by(subject_id=ts.subject_id).all()
                assessment_rubric_ids = [rubric.id for rubric in assessment_rubrics]

                for rubric_id in assessment_rubric_ids:
                    formative_report = FormativeReport(
                        school_id=data['school_id'],
                        student_id=new_student.id,
                        subject_id=ts.subject_id,
                        grade_id=data['grade_id'],
                        stream_id=data['stream_id'],
                        year_id=year_id,
                        subject_teacher_id=ts.staff_id,
                        assessment_rubic_id=rubric_id  # Save the individual assessment rubric ID
                    )
                    db.session.add(formative_report)

            # Create Summative Reports for each subject and term
            for ts in teacher_subjects:
                for term_id in term_ids:
                    summative_report = SummativeReport(
                        school_id=data['school_id'],
                        student_id=new_student.id,
                        subject_id=ts.subject_id,
                        grade_id=data['grade_id'],
                        stream_id=data['stream_id'],
                        class_teacher_id=class_teacher_id,
                        year_id=year_id,
                        term_id=term_id,
                        subject_teacher_id=ts.staff_id,
                        exam_marks=0,
                        average_grade=0,
                        general_remarks="",
                        class_teachers_comments=""
                    )
                    db.session.add(summative_report)

            # Create Behavior Report
            behaviour_report = BehaviourReport(
                school_id=data['school_id'],
                student_id=new_student.id,
                grade_id=data['grade_id'],
                year_id=year_id,  # Using the derived year_id
                stream_id=data['stream_id'],
                class_teacher_id=class_teacher_id,
                behaviour_goal="",
                behaviour_goal_assessment="",
                class_teachers_comments=""
            )
            db.session.add(behaviour_report)

            db.session.commit()

            result = studentSchema.dump(new_student)
            return make_response(jsonify(result), 201)

        except IntegrityError:
            db.session.rollback()
            return make_response(jsonify({"error": "Database integrity error occurred"}), 500)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"error": str(e)}), 500)

api.add_resource(StudentDetails, '/students')


class StudentsByGrade(Resource):
    @jwt_required()
    def get(self, grade_id):
        school_id = get_school_id_from_session()
        if not school_id:
            return make_response(jsonify({'error': 'School ID not found in session'}), 401)

        students_details = Student.query.filter_by(school_id=school_id, grade_id=grade_id).all()
        result = studentSchema.dump(students_details, many=True)
        return make_response(jsonify(result), 200)
api.add_resource(StudentsByGrade, '/students/grade/<string:grade_id>')

class StudentsByGradeAndStream(Resource):
    @jwt_required()
    def get(self, grade_id, stream_id):
        school_id = get_school_id_from_session()

        if not school_id:
            return make_response(jsonify({'error': 'School ID not found in session'}), 401)

        # Query to fetch students of the specific grade and stream
        students_details = Student.query.filter_by(school_id=school_id, grade_id=grade_id, stream_id=stream_id).all()

        # Serialize the query result
        result = studentSchema.dump(students_details, many=True)

        return make_response(jsonify(result), 200)
api.add_resource(StudentsByGradeAndStream, '/students/grades/<string:grade_id>/streams/<string:stream_id>')

    
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


class PromoteStudent(Resource):
    @admin_required()
    def post(self, student_id):
        school_id = get_school_id_from_session()
        if not school_id:
            return make_response(jsonify({'error': 'School ID not found in session'}), 401)

        student = Student.query.filter_by(school_id=school_id, id=student_id).first()
        if not student:
            return make_response(jsonify({"error": f"Student with id {student_id} does not exist in the specified school"}), 404)

        current_grade = Grade.query.get(student.grade_id)
        if current_grade:
            next_grade = Grade.query.filter(
                Grade.school_id == student.school_id,
                Grade.grade.ilike(f"Grade {int(current_grade.grade.split(' ')[-1]) + 1}")
            ).first()
            if next_grade:
                student.grade_id = next_grade.id
                db.session.commit()
                result = studentSchema.dump(student)
                return make_response(jsonify(result), 200)
        
        return make_response(jsonify({"error": "Promotion failed. Next grade not found or other error occurred"}), 400)

api.add_resource(PromoteStudent, '/promote/students/<string:student_id>')
