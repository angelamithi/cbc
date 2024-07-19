from flask import Blueprint, make_response, jsonify
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt
from models import SummativeReport, db,Year,Term,Student
from serializer import summative_report_schema
from auth import admin_required, teacher_required
from datetime import datetime

summative_report_bp = Blueprint('summative_report_bp', __name__)
api = Api(summative_report_bp)



patch_args = reqparse.RequestParser()
patch_args.add_argument('exam_marks', type=int)
patch_args.add_argument('general_remarks', type=str)
patch_args.add_argument('class_teachers_comments', type=str)

def get_school_id_from_session():
    claims = get_jwt()
    return claims.get("school_id")




class AnnualAverageCalculator(Resource):
    @staticmethod
    def calculate_annual_averages(student_id, grade_id):
        school_id = get_school_id_from_session()
        current_year = datetime.now().year
        year_object = Year.query.filter_by(year_name=current_year).first()

        if not year_object:
            return make_response(jsonify({"error": f"No year found for {current_year}"}), 404)

        year_id = year_object.id
        summative_reports = SummativeReport.query.filter_by(
            student_id=student_id,
            year_id=year_id,
            grade_id=grade_id,
            school_id=school_id
        ).all()

        subject_ids = {report.subject_id for report in summative_reports}

        for subject_id in subject_ids:
            subject_reports = [report for report in summative_reports if report.subject_id == subject_id]

            total_marks = sum(report.exam_marks for report in subject_reports)
            average_grade = total_marks / len(subject_reports) if subject_reports else 0

            for report in subject_reports:
                report.average_grade = average_grade

        db.session.commit()

    @jwt_required()
    def get(self, grade_id, student_id):
        school_id = get_school_id_from_session()
        if not school_id:
            return make_response(jsonify({'error': 'School ID not found in session'}), 401)

        AnnualAverageCalculator.calculate_annual_averages(student_id, grade_id)

        return make_response(jsonify({"message": "Annual averages calculated successfully"}), 200)

api.add_resource(AnnualAverageCalculator, '/calculate_annual_average/<string:grade_id>/<string:student_id>')

class EditSummativeReport(Resource):
    @admin_required()
    def patch(self, grade_id, student_id):
        school_id = get_school_id_from_session()
        if not school_id:
            return make_response(jsonify({"error": "School ID not found in session"}), 401)

        current_year = datetime.now().year
        year = Year.query.filter_by(year_name=current_year).first()
        if not year:
            return make_response(jsonify({"error": f"No year found for {current_year}"}), 404)

        year_id = year.id

        # Retrieve the SummativeReport with additional filters
        summative_report = SummativeReport.query.filter_by(
            school_id=school_id,
            year_id=year_id,
            grade_id=grade_id,
            student_id=student_id
        ).first()

        if not summative_report:
            return make_response(jsonify({"error": "Summative Report not found for the provided criteria"}), 404)

        data = patch_args.parse_args()
        for key, value in data.items():
            if value is not None:
                setattr(summative_report, key, value)

        # Recalculate the annual averages if any of the exam marks are updated
        AnnualAverageCalculator.calculate_annual_averages(student_id, grade_id)

        db.session.commit()

        result = summative_report_schema.dump(summative_report)
        return make_response(jsonify(result), 200)

api.add_resource(EditSummativeReport, '/edit_summative_report/<string:grade_id>/<string:student_id>')


class SummativeReportDetails(Resource):
    @jwt_required()
    def get(self,grade_id, student_id ):
        school_id = get_school_id_from_session()
     
        current_year = datetime.now().year
        year_object = Year.query.filter_by(year_name=current_year).first()

        if not year_object:
            return make_response(jsonify({"error": f"No year found for {current_year}"}), 404)

        year_id = year_object.id
        
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
    
   
api.add_resource(SummativeReportDetails, '/summative_reports_per_year/<string:grade_id>/<string:student_id>/')
    
class SummativeReportDetailsPerTerm(Resource):
    @jwt_required()
    def get(self, grade_id, student_id, term_id):
        school_id = get_school_id_from_session()

        current_year = datetime.now().year
        year_object = Year.query.filter_by(year_name=current_year).first()

        if not year_object:
            return make_response(jsonify({"error": f"No year found for {current_year}"}), 404)

        year_id = year_object.id
        
        summative_reports = SummativeReport.query.filter_by(
            student_id=student_id,
            grade_id=grade_id,
            year_id=year_id,
            term_id=term_id,  # Add term_id filter
            school_id=school_id
        ).all()

        if not summative_reports:
            return make_response(jsonify({"error": "Summative Reports not found for this student, grade, term, and year combination"}), 404)

        result = summative_report_schema.dump(summative_reports, many=True)
        return make_response(jsonify(result), 200)
    
api.add_resource(SummativeReportDetailsPerTerm, '/summative_reports_per_term/<string:grade_id>/<string:student_id>/<string:term_id>')

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
    
api.add_resource(SummativeReportById, '/single_summative_report/<string:id>')

