from flask import Blueprint, make_response, jsonify
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required
from models import AssessmentRubic, db
from serializer import assessmentRubicSchema
from auth import admin_required, superAdmin_required

assessment_rubic_bp = Blueprint('assessment_rubic_bp', __name__)
api = Api(assessment_rubic_bp)

post_args = reqparse.RequestParser()
post_args.add_argument('school_id', type=str, required=True, help='School Id is required')
post_args.add_argument('assessment_rubics', type=str, required=True, help='Assessment Rubrics is required')
post_args.add_argument('assessment_rubic_mark', type=int, required=True, help='Assessment Rubric Mark is required')
post_args.add_argument('grade_id', type=str, required=True, help='Grade Id is required')
post_args.add_argument('subject_id', type=str, required=True, help='Subject Id is required')
post_args.add_argument('strand_id', type=str, required=True, help='Strand Id is required')
post_args.add_argument('sub_strand_id', type=str, required=True, help='SubStrand Id is required')
post_args.add_argument('learning_outcome_id', type=str, required=True, help='Learning Outcome Id is required')

patch_args = reqparse.RequestParser()
patch_args.add_argument('school_id', type=str)
patch_args.add_argument('assessment_rubics', type=str)
patch_args.add_argument('assessment_rubic_mark', type=int)
patch_args.add_argument('grade_id', type=str)
patch_args.add_argument('subject_id', type=str)
patch_args.add_argument('strand_id', type=str)
patch_args.add_argument('sub_strand_id', type=str)
patch_args.add_argument('learning_outcome_id', type=str)

class AssessmentRubicDetails(Resource):
    @jwt_required()
    def get(self):
        assessment_rubics = AssessmentRubic.query.all()
        result = assessmentRubicSchema.dump(assessment_rubics, many=True)
        return make_response(jsonify(result), 200)

    @superAdmin_required()
    def post(self):
        data = post_args.parse_args()

        # Check if the assessment rubric already exists
        existing_assessment_rubic = AssessmentRubic.query.filter_by(school_id=data['school_id'],
                                                                    assessment_rubics=data['assessment_rubics'],
                                                                    grade_id=data['grade_id'], subject_id=data['subject_id'],
                                                                    strand_id=data['strand_id'], sub_strand_id=data['sub_strand_id'],
                                                                    learning_outcome_id=data['learning_outcome_id']).first()
        if existing_assessment_rubic:
            return make_response(jsonify({"error": "Assessment Rubric already exists for this school, grade, subject, strand, sub-strand, and learning outcome"}), 409)

        new_assessment_rubic = AssessmentRubic(school_id=data['school_id'], assessment_rubics=data['assessment_rubics'],
                                               assessment_rubic_mark=data['assessment_rubic_mark'], grade_id=data['grade_id'],
                                               subject_id=data['subject_id'], strand_id=data['strand_id'], sub_strand_id=data['sub_strand_id'],
                                               learning_outcome_id=data['learning_outcome_id'])
        db.session.add(new_assessment_rubic)
        db.session.commit()

        result = assessmentRubicSchema.dump(new_assessment_rubic)
        return make_response(jsonify(result), 201)

api.add_resource(AssessmentRubicDetails, '/assessment_rubrics')

class AssessmentRubicById(Resource):
    @jwt_required()
    def get(self, id):
        assessment_rubic = AssessmentRubic.query.get(id)
        if not assessment_rubic:
            return make_response(jsonify({"error": "Assessment Rubric not found"}), 404)

        result = assessmentRubicSchema.dump(assessment_rubic)
        return make_response(jsonify(result), 200)

    @superAdmin_required()
    def delete(self, id):
        assessment_rubic = AssessmentRubic.query.get(id)
        if not assessment_rubic:
            return make_response(jsonify({"error": "Assessment Rubric not found"}), 404)

        db.session.delete(assessment_rubic)
        db.session.commit()
        return make_response(jsonify({"message": "Assessment Rubric deleted successfully"}), 200)

    @superAdmin_required()
    def patch(self, id):
        assessment_rubic = AssessmentRubic.query.get(id)
        if not assessment_rubic:
            return make_response(jsonify({"error": "Assessment Rubric not found"}), 404)

        data = patch_args.parse_args()
        for key, value in data.items():
            if value is not None:
                setattr(assessment_rubic, key, value)

        db.session.commit()
        result = assessmentRubicSchema.dump(assessment_rubic)
        return make_response(jsonify(result), 200)

api.add_resource(AssessmentRubicById, '/assessment_rubrics/<string:id>')
