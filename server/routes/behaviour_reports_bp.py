from flask import Blueprint, make_response, jsonify
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt
from models import BehaviourReport, db,Year # Assuming BehaviourReport model is defined in 'models'
from auth import admin_required, teacher_required  # Assuming authentication decorators are defined
from serializer import behaviour_report_schema

from datetime import datetime

behaviour_report_bp = Blueprint('behaviour_report_bp', __name__)
api = Api(behaviour_report_bp)



patch_args = reqparse.RequestParser()
patch_args.add_argument('behaviour_goal', type=str)
patch_args.add_argument('behaviour_goal_assessment', type=str)
patch_args.add_argument('class_teachers_comments', type=str)

def get_school_id_from_session():
    claims = get_jwt()
    return claims.get("school_id")

class BehaviourReportDetails(Resource):
    @jwt_required()
    def get(self, grade_id,student_id):
        school_id = get_school_id_from_session()
        # Fetch the current year object
        current_year = datetime.now().year
        year_object = Year.query.filter_by(year_name=current_year).first()

        if not year_object:
            return make_response(jsonify({"error": f"No year found for {current_year}"}), 404)

        year_id = year_object.id

        behaviour_reports = BehaviourReport.query.filter_by(
            student_id=student_id,
            grade_id=grade_id,
            year_id=year_id,
            school_id=school_id
        ).all()

        if not behaviour_reports:
            return make_response(jsonify({"error": "Behaviour Reports not found for this student, grade, and year combination"}), 404)

        # Assuming behaviour_report_schema is defined for serialization
        result = behaviour_report_schema.dump(behaviour_reports, many=True)
        return make_response(jsonify(result), 200)
api.add_resource(BehaviourReportDetails, '/behaviour_reports/<string:student_id>/<string:grade_id>/<string:year_id>')

class BehaviourPostReportDetails(Resource):
    @teacher_required()
    def patch(self, grade_id,student_id):
        school_id = get_school_id_from_session()
        data = patch_args.parse_args()
        # Fetch the current year object
        current_year = datetime.now().year
        year_object = Year.query.filter_by(year_name=current_year).first()

        if not year_object:
            return make_response(jsonify({"error": f"No year found for {current_year}"}), 404)

        year_id = year_object.id

        existing_report = BehaviourReport.query.filter_by(
            student_id=student_id,
            grade_id=grade_id,
            year_id=year_id,
            school_id=school_id
        ).first()

        if not existing_report:
            return make_response(jsonify({
                "error": "No existing report found to update for this student, grade, and year."
            }), 404)

        for key, value in data.items():
            if value is not None:
                setattr(existing_report, key, value)

        db.session.commit()

        # Assuming behaviour_report_schema is defined for serialization
        result = behaviour_report_schema.dump(existing_report)
        return make_response(jsonify(result), 200)

api.add_resource(BehaviourReportDetails, '/update_behaviour_reports/<string:grade_id><string:student_id>')

class BehaviourReportById(Resource):
    @jwt_required()
    def get(self, id):
        behaviour_report = BehaviourReport.query.get(id)
        if not behaviour_report:
            return make_response(jsonify({"error": "Behaviour Report not found"}), 404)

        # Assuming behaviour_report_schema is defined for serialization
        result = behaviour_report_schema.dump(behaviour_report)
        return make_response(jsonify(result), 200)

    @admin_required()
    def delete(self, id):
        behaviour_report = BehaviourReport.query.get(id)
        if not behaviour_report:
            return make_response(jsonify({"error": "Behaviour Report not found"}), 404)

        db.session.delete(behaviour_report)
        db.session.commit()
        return make_response(jsonify({"message": "Behaviour Report deleted successfully"}), 200)



api.add_resource(BehaviourReportById, '/behaviour_reports/<string:id>')
