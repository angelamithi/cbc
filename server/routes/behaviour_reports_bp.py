from flask import Blueprint, make_response, jsonify
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt
from models import BehaviourReport, db  # Assuming BehaviourReport model is defined in 'models'
from auth import admin_required, teacher_required  # Assuming authentication decorators are defined
from serializer import behaviour_report_schema

behaviour_report_bp = Blueprint('behaviour_report_bp', __name__)
api = Api(behaviour_report_bp)

post_args = reqparse.RequestParser()
post_args.add_argument('student_id', type=str, required=True, help='Student ID is required')
post_args.add_argument('grade_id', type=str, required=True, help='Grade ID is required')
post_args.add_argument('year_id', type=str, required=True, help='Year ID is required')
post_args.add_argument('stream_id', type=str, required=True, help='Stream ID is required')
post_args.add_argument('class_teacher_id', type=str, required=True, help='Class Teacher ID is required')
post_args.add_argument('behaviour_goal', type=str, required=True, help='Behaviour Goal is required')
post_args.add_argument('behaviour_goal_assessment', type=str, required=True, help='Behaviour Goal Assessment is required')
post_args.add_argument('class_teachers_comments', type=str, required=True, help='Class Teacher\'s Comments are required')

patch_args = reqparse.RequestParser()
patch_args.add_argument('behaviour_goal', type=str)
patch_args.add_argument('behaviour_goal_assessment', type=str)
patch_args.add_argument('class_teachers_comments', type=str)

def get_school_id_from_session():
    claims = get_jwt()
    return claims.get("school_id")

class BehaviourReportDetails(Resource):
    @jwt_required()
    def get(self, id):
        school_id = get_school_id_from_session()
        behaviour_reports = BehaviourReport.query.filter_by(id=id, school_id=school_id).first()

        if not behaviour_reports:
            return make_response(jsonify({"error": "Behaviour Report not found"}), 404)

        # Assuming behaviour_report_schema is defined for serialization
        result = behaviour_report_schema.dump(behaviour_reports)
        return make_response(jsonify(result), 200)

    @teacher_required()
    def post(self):
        school_id = get_school_id_from_session()
        data = post_args.parse_args()

        new_behaviour_report = BehaviourReport(
            student_id=data['student_id'],
            grade_id=data['grade_id'],
            year_id=data['year_id'],
            school_id=school_id,
            stream_id=data['stream_id'],
            class_teacher_id=data['class_teacher_id'],
            behaviour_goal=data['behaviour_goal'],
            behaviour_goal_assessment=data['behaviour_goal_assessment'],
            class_teachers_comments=data['class_teachers_comments']
        )

        db.session.add(new_behaviour_report)
        db.session.commit()

        # Assuming behaviour_report_schema is defined for serialization
        result = behaviour_report_schema.dump(new_behaviour_report)
        return make_response(jsonify(result), 201)

api.add_resource(BehaviourReportDetails, '/behaviour_reports/<string:id>')

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

    @admin_required()
    def patch(self, id):
        behaviour_report = BehaviourReport.query.get(id)
        if not behaviour_report:
            return make_response(jsonify({"error": "Behaviour Report not found"}), 404)

        data = patch_args.parse_args()
        for key, value in data.items():
            if value is not None:
                setattr(behaviour_report, key, value)

        db.session.commit()

        # Assuming behaviour_report_schema is defined for serialization
        result = behaviour_report_schema.dump(behaviour_report)
        return make_response(jsonify(result), 200)

api.add_resource(BehaviourReportById, '/behaviour_reports/<string:id>')
