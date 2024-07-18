from flask import Blueprint, make_response, jsonify
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt
from models import SummativeReport, db
from serializer import summative_report_schema
from auth import admin_required, teacher_required

summative_report_bp = Blueprint('summative_report_bp', __name__)
api = Api(summative_report_bp)

post_args = reqparse.RequestParser()
post_args.add_argument('student_id', type=str, required=True, help='Student ID is required')
post_args.add_argument('subject_id', type=str, required=True, help='Subject ID is required')
post_args.add_argument('grade_id', type=str, required=True, help='Grade ID is required')
post_args.add_argument('year_id', type=str, required=True, help='Year ID is required')
post_args.add_argument('term_id', type=str, required=True, help='Term ID is required')
post_args.add_argument('stream_id', type=str, required=True, help='Stream ID is required')
post_args.add_argument('class_teacher_id', type=str, required=True, help='Class Teacher ID is required')
post_args.add_argument('subject_teacher_id', type=str, required=True, help='Subject Teacher ID is required')
post_args.add_argument('exam_1_marks', type=int, help='Exam 1 Marks are optional')
post_args.add_argument('exam_2_marks', type=int, help='Exam 2 Marks are optional ')
post_args.add_argument('exam_3_marks', type=int, help='Exam 3 Marks are optional')
post_args.add_argument('general_remarks', type=str, required=True, help='General Remarks are optional')
post_args.add_argument('class_teachers_comments', type=str, required=True, help='Class Teacher\'s Comments are optional')

patch_args = reqparse.RequestParser()
patch_args.add_argument('exam_1_marks', type=int)
patch_args.add_argument('exam_2_marks', type=int)
patch_args.add_argument('exam_3_marks', type=int)
patch_args.add_argument('general_remarks', type=str)
patch_args.add_argument('class_teachers_comments', type=str)

def get_school_id_from_session():
    claims = get_jwt()
    return claims.get("school_id")

class SummativeReportDetails(Resource):
    @jwt_required()
    def get(self, student_id, grade_id, year_id):
        school_id = get_school_id_from_session()
        print(f"Fetching reports for student_id={student_id}, grade_id={grade_id}, year_id={year_id}, school_id={school_id}")
        
        summative_reports = SummativeReport.query.filter_by(
            student_id=student_id,
            grade_id=grade_id,
            year_id=year_id,
            school_id=school_id
        ).all()

        if not summative_reports:
            print("No summative reports found.")
            return make_response(jsonify({"error": "Summative Reports not found for this student, grade, and year combination"}), 404)

        result = summative_report_schema.dump(summative_reports,many=True)
        print(f"Found reports: {result}")
        return make_response(jsonify(result), 200)
    
    @staticmethod
    def calculate_average_grade(exam_1_marks, exam_2_marks, exam_3_marks):
        exams = [exam_1_marks, exam_2_marks, exam_3_marks]
        valid_exams = [exam for exam in exams if exam is not None]
        if valid_exams:
            return sum(valid_exams) / len(valid_exams)
        return None
api.add_resource(SummativeReportDetails, '/summative_reports/<string:student_id>/<string:grade_id>/<string:year_id>')
    
    # @teacher_required()
class SummativePostReportDetails(Resource):
        @jwt_required()
        def post(self):
            school_id = get_school_id_from_session()
            data = post_args.parse_args()

            # Check if a report already exists for the same student, grade, and year
            existing_report = SummativeReport.query.filter_by(
                student_id=data['student_id'],
                grade_id=data['grade_id'],
                year_id=data['year_id'],
                school_id=school_id
            ).first()

            if existing_report:
                existing_report_details = {
                    "exam_1_marks": existing_report.exam_1_marks,
                    "exam_2_marks": existing_report.exam_2_marks,
                    "exam_3_marks": existing_report.exam_3_marks,
                    "general_remarks": existing_report.general_remarks,
                    "class_teachers_comments": existing_report.class_teachers_comments
                }
                return make_response(jsonify({
                    "message": "A report for this student, grade, and year already exists. Do you want to edit it instead?",
                    "existing_report_details": existing_report_details
                }), 409)

            average_grade = SummativeReportDetails.calculate_average_grade(
                data.get('exam_1_marks'),
                data.get('exam_2_marks'),
                data.get('exam_3_marks')
            )

            new_summative_report = SummativeReport(
                student_id=data['student_id'],
                grade_id=data['grade_id'],
                year_id=data['year_id'],
                term_id=data['term_id'],
                school_id=school_id,
                stream_id=data['stream_id'],
                subject_id=data['subject_id'],
                subject_teacher_id=data['subject_teacher_id'],
                class_teacher_id=data['class_teacher_id'],
                exam_1_marks=data.get('exam_1_marks'),
                exam_2_marks=data.get('exam_2_marks'),
                exam_3_marks=data.get('exam_3_marks'),
                average_grade=average_grade,
                general_remarks=data['general_remarks'],
                class_teachers_comments=data['class_teachers_comments'],
            )
            db.session.add(new_summative_report)
            db.session.commit()

            result = summative_report_schema.dump(new_summative_report)
            return make_response(jsonify(result), 201)

api.add_resource(SummativePostReportDetails, '/summative_reports')

class SummativeReportById(Resource):
    @staticmethod
    def calculate_average_grade(exam_1_marks, exam_2_marks, exam_3_marks):
        exams = [exam_1_marks, exam_2_marks, exam_3_marks]
        valid_exams = [exam for exam in exams if exam is not None]
        if valid_exams:
            return sum(valid_exams) / len(valid_exams)
        return None
    @jwt_required()
    def get(self, id):
        summative_report = SummativeReport.query.get(id)
        if not summative_report:
            return make_response(jsonify({"error": "Summative Report not found"}), 404)

        result = summative_report_schema.dump(summative_report)
        return make_response(jsonify(result), 200)

    @admin_required()
    def delete(self, id):
        summative_report = SummativeReport.query.get(id)
        if not summative_report:
            return make_response(jsonify({"error": "Summative Report not found"}), 404)

        db.session.delete(summative_report)
        db.session.commit()
        return make_response(jsonify({"message": "Summative Report deleted successfully"}), 200)

    @admin_required()
    def patch(self, id):
        summative_report = SummativeReport.query.get(id)
        if not summative_report:
            return make_response(jsonify({"error": "Summative Report not found"}), 404)

        data = patch_args.parse_args()
        for key, value in data.items():
            if value is not None:
                setattr(summative_report, key, value)

        # Recalculate the average grade if any of the exam marks are updated
        summative_report.average_grade = SummativeReportById.calculate_average_grade(
            summative_report.exam_1_marks,
            summative_report.exam_2_marks,
            summative_report.exam_3_marks
        )

        db.session.commit()

        result = summative_report_schema.dump(summative_report)
        return make_response(jsonify(result), 200)

api.add_resource(SummativeReportById, '/summative_reports/<string:id>')
