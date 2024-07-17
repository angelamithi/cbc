from flask import Blueprint, make_response, jsonify
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required,get_jwt
from models import SummativeReport, db
from serializer import summative_report_schema
from auth import admin_required,teacher_required

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
post_args.add_argument('exam_1_marks', type=int, required=True, help='Exam 1 Marks are required')
post_args.add_argument('exam_2_marks', type=int, required=True, help='Exam 2 Marks are required')
post_args.add_argument('exam_3_marks', type=int, required=True, help='Exam 3 Marks are required')
post_args.add_argument('average_grade', type=float, required=True, help='Average Grade is required')
post_args.add_argument('general_remarks', type=str, required=True, help='General Remarks are required')
post_args.add_argument('class_teachers_comments', type=str, required=True, help='Class Teacher\'s Comments are required')

patch_args = reqparse.RequestParser()
patch_args.add_argument('exam_1_marks', type=int)
patch_args.add_argument('exam_2_marks', type=int)
patch_args.add_argument('exam_3_marks', type=int)
patch_args.add_argument('average_grade', type=float)
patch_args.add_argument('general_remarks', type=str)
patch_args.add_argument('class_teachers_comments', type=str)




def get_school_id_from_session():
    claims = get_jwt()
    return claims.get("school_id")

class SummativeReportDetails(Resource):
    @jwt_required()
    def get(self, student_id, grade_id, year_id):
        school_id=get_school_id_from_session()
        summative_reports = SummativeReport.query.filter_by(
            student_id=student_id,
            grade_id=grade_id,
            year_id=year_id,
            school_id=school_id

        ).all()

        if not summative_reports:
            return make_response(jsonify({"error": "Summative Reports not found for this student, grade, and year combination"}), 404)

        result = summative_report_schema.dump(summative_reports)
        return make_response(jsonify(result), 200)

    @teacher_required()
    def post(self):
        school_id=get_school_id_from_session()
        data = post_args.parse_args()

        new_summative_report = SummativeReport(
            student_id=data['student_id'],
            grade_id=data['grade_id'],
            year_id=data['year_id'],
            school_id=school_id,
            stream_id=data['stream_id'],
            subject_id=data['subject_id'],
            class_teacher_id=data['class_teacher_id'],
            exam_1_marks=data['exam_1_marks'],
            exam_2_marks=data['exam_2_marks'],
            exam_3_marks=data['exam_3_marks'],
            average_grade=data['average_grade'],
            general_remarks=data['general_remarks'],
            class_teachers_comments=data['class_teachers_comments'],
         
           
            

        )
        db.session.add(new_summative_report)
        db.session.commit()

        result = summative_report_schema.dump(new_summative_report)
        return make_response(jsonify(result), 201)

api.add_resource(SummativeReportDetails, '/summative_reports/<string:student_id>/<string:grade_id>/<string:year_id>')

class SummativeReportById(Resource):
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

        db.session.commit()

        result = summative_report_schema.dump(summative_report)
        return make_response(jsonify(result), 200)

api.add_resource(SummativeReportById, '/summative_reports/<int:id>')
