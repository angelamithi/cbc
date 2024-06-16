from flask import Blueprint, make_response, jsonify
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required
from models import LearningOutcome, db
from serializer import learningOutcomeSchema
from auth import admin_required, superAdmin_required

learning_outcome_bp = Blueprint('learning_outcome_bp', __name__)
api = Api(learning_outcome_bp)

post_args = reqparse.RequestParser()
post_args.add_argument('school_id', type=str, required=True, help='School Id is required')
post_args.add_argument('learning_outcomes', type=str, required=True, help='Learning Outcomes is required')
post_args.add_argument('grade_id', type=str, required=True, help='Grade Id is required')
post_args.add_argument('subject_id', type=str, required=True, help='Subject Id is required')
post_args.add_argument('strand_id', type=str, required=True, help='Strand Id is required')
post_args.add_argument('sub_strand_id', type=str, required=True, help='SubStrand Id is required')

patch_args = reqparse.RequestParser()
patch_args.add_argument('school_id', type=str)
patch_args.add_argument('learning_outcomes', type=str)
patch_args.add_argument('grade_id', type=str)
patch_args.add_argument('subject_id', type=str)
patch_args.add_argument('strand_id', type=str)
patch_args.add_argument('sub_strand_id', type=str)

class LearningOutcomeDetails(Resource):
    @jwt_required()
    def get(self):
        learning_outcomes = LearningOutcome.query.all()
        result = learningOutcomeSchema.dump(learning_outcomes, many=True)
        return make_response(jsonify(result), 200)

    @superAdmin_required()
    def post(self):
        data = post_args.parse_args()

        # Check if the learning outcome already exists
        existing_learning_outcome = LearningOutcome.query.filter_by(school_id=data['school_id'],
                                                                    learning_outcomes=data['learning_outcomes'],
                                                                    grade_id=data['grade_id'], subject_id=data['subject_id'],
                                                                    strand_id=data['strand_id'], sub_strand_id=data['sub_strand_id']).first()
        if existing_learning_outcome:
            return make_response(jsonify({"error": "Learning Outcome already exists for this school, grade, subject, strand, and sub-strand"}), 409)

        new_learning_outcome = LearningOutcome(school_id=data['school_id'], learning_outcomes=data['learning_outcomes'],
                                               grade_id=data['grade_id'], subject_id=data['subject_id'], strand_id=data['strand_id'],
                                               sub_strand_id=data['sub_strand_id'])
        db.session.add(new_learning_outcome)
        db.session.commit()

        result = learningOutcomeSchema.dump(new_learning_outcome)
        return make_response(jsonify(result), 201)

api.add_resource(LearningOutcomeDetails, '/learning_outcomes')

class LearningOutcomeById(Resource):
    @jwt_required()
    def get(self, id):
        learning_outcome = LearningOutcome.query.get(id)
        if not learning_outcome:
            return make_response(jsonify({"error": "Learning Outcome not found"}), 404)

        result = learningOutcomeSchema.dump(learning_outcome)
        return make_response(jsonify(result), 200)

    @superAdmin_required()
    def delete(self, id):
        learning_outcome = LearningOutcome.query.get(id)
        if not learning_outcome:
            return make_response(jsonify({"error": "Learning Outcome not found"}), 404)

        db.session.delete(learning_outcome)
        db.session.commit()
        return make_response(jsonify({"message": "Learning Outcome deleted successfully"}), 200)

    @superAdmin_required()
    def patch(self, id):
        learning_outcome = LearningOutcome.query.get(id)
        if not learning_outcome:
            return make_response(jsonify({"error": "Learning Outcome not found"}), 404)

        data = patch_args.parse_args()
        for key, value in data.items():
            if value is not None:
                setattr(learning_outcome, key, value)

        db.session.commit()
        result = learningOutcomeSchema.dump(learning_outcome)
        return make_response(jsonify(result), 200)

api.add_resource(LearningOutcomeById, '/learning_outcomes/<string:id>')
