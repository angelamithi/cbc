from flask import Blueprint, make_response, jsonify
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required
from models import Report, db
from serializer import reportSchema
from auth import admin_required, superAdmin_required,teacher_required

reports_bp = Blueprint('reports_bp', __name__)
api = Api(reports_bp)

post_args = reqparse.RequestParser()
post_args.add_argument('school_id', type=str, required=True, help='School Id is required')
post_args.add_argument('staff_id', type=str, required=True, help='Staff Id is required')
post_args.add_argument('year_id', type=str, required=True, help='Year Id is required')
post_args.add_argument('term_id', type=str, required=True, help='Term Id is required')
post_args.add_argument('grade_id', type=str, required=True, help='Grade Id is required')
post_args.add_argument('stream_id', type=str, required=True, help='Stream Id is required')
post_args.add_argument('student_id', type=str, required=True, help='Student Id is required')
post_args.add_argument('subject_id', type=str, required=True, help='Subject Id is required')
post_args.add_argument('strand_id', type=str, required=True, help='Strand Id is required')
post_args.add_argument('substrand_id', type=str, required=True, help='Substrand Id is required')
post_args.add_argument('learning_outcomes_id', type=str, required=True, help='Learning Outcomes Id is required')
post_args.add_argument('assessment_rubics_id', type=str, required=True, help='Assessment Rubrics Id is required')
post_args.add_argument('single_mark', type=int, required=True, help='Single Mark is required')
post_args.add_argument('grade_ee', type=bool, default=False)
post_args.add_argument('grade_me', type=bool, default=False)
post_args.add_argument('grade_ae', type=bool, default=False)
post_args.add_argument('grade_be', type=bool, default=False)

patch_args = reqparse.RequestParser()
patch_args.add_argument('school_id', type=str)
patch_args.add_argument('staff_id', type=str)
patch_args.add_argument('year_id', type=str)
patch_args.add_argument('term_id', type=str)
patch_args.add_argument('grade_id', type=str)
patch_args.add_argument('stream_id', type=str)
patch_args.add_argument('student_id', type=str)
patch_args.add_argument('subject_id', type=str)
patch_args.add_argument('strand_id', type=str)
patch_args.add_argument('substrand_id', type=str)
patch_args.add_argument('learning_outcomes_id', type=str)
patch_args.add_argument('assessment_rubics_id', type=str)
patch_args.add_argument('single_mark', type=int)
patch_args.add_argument('grade_ee', type=bool)
patch_args.add_argument('grade_me', type=bool)
patch_args.add_argument('grade_ae', type=bool)
patch_args.add_argument('grade_be', type=bool)

class ReportDetails(Resource):
    @jwt_required()
    def get(self):
        reports = Report.query.all()
        result = reportSchema.dump(reports, many=True)
        return make_response(jsonify(result), 200)

    @teacher_required()
    def post(self):
        data = post_args.parse_args()

        new_report = Report(
            school_id=data['school_id'],
            staff_id=data['staff_id'],
            year_id=data['year_id'],
            term_id=data['term_id'],
            grade_id=data['grade_id'],
            stream_id=data['stream_id'],
            student_id=data['student_id'],
            subject_id=data['subject_id'],
            strand_id=data['strand_id'],
            substrand_id=data['substrand_id'],
            learning_outcomes_id=data['learning_outcomes_id'],
            assessment_rubics_id=data['assessment_rubics_id'],
            single_mark=data['single_mark'],
            grade_ee=data['grade_ee'],
            grade_me=data['grade_me'],
            grade_ae=data['grade_ae'],
            grade_be=data['grade_be']
        )
        db.session.add(new_report)
        db.session.commit()

        result = reportSchema.dump(new_report)
        return make_response(jsonify(result), 201)

api.add_resource(ReportDetails, '/reports')

class ReportById(Resource):
    @jwt_required()
    def get(self, id):
        report = Report.query.get(id)
        if not report:
            return make_response(jsonify({"error": "Report not found"}), 404)

        result = reportSchema.dump(report)
        return make_response(jsonify(result), 200)

    @admin_required()
    def delete(self, id):
        report = Report.query.get(id)
        if not report:
            return make_response(jsonify({"error": "Report not found"}), 404)

        db.session.delete(report)
        db.session.commit()
        return make_response(jsonify({"message": "Report deleted successfully"}), 200)

    @teacher_required()
    def patch(self, id):
        report = Report.query.get(id)
        if not report:
            return make_response(jsonify({"error": "Report not found"}), 404)

        data = patch_args.parse_args()
        for key, value in data.items():
            if value is not None:
                setattr(report, key, value)

        db.session.commit()
        result = reportSchema.dump(report)
        return make_response(jsonify(result), 200)

api.add_resource(ReportById, '/reports/<string:id>')
