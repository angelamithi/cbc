from flask import Blueprint, make_response, jsonify
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required
from models import SubStrand, Strand, LearningOutcome, AssessmentRubic, db
from serializer import subStrandSchema, strandSchema, learningOutcomeSchema, assessmentRubicSchema
from auth import admin_required, superAdmin_required

subject_bp = Blueprint('subject_bp', __name__)
api = Api(subject_bp)

post_args = reqparse.RequestParser()
patch_args = reqparse.RequestParser()

# Define arguments for each resource
post_args.add_argument('substrand_name', type=str, required=True, help='SubStrand Name is required')
post_args.add_argument('strand_name', type=str, required=True, help='Strand Name is required')
post_args.add_argument('learning_outcomes', type=str, required=True, help='Learning Outcomes is required')
post_args.add_argument('assessment_rubrics', type=str, required=True, help='Assessment Rubrics is required')
post_args.add_argument('grade_id', type=str, required=True, help='Grade Id is required')
post_args.add_argument('subject_id', type=str, required=True, help='Subject Id is required')

patch_args.add_argument('substrand_name', type=str)
patch_args.add_argument('strand_name', type=str)
patch_args.add_argument('learning_outcomes', type=str)
patch_args.add_argument('assessment_rubrics', type=str)
patch_args.add_argument('grade_id', type=str)
patch_args.add_argument('subject_id', type=str)

class SubjectDetails(Resource):
    @jwt_required()
    def get(self, subject_id,grade_id):
        # Fetch data for SubStrands, Strands, LearningOutcomes, and AssessmentRubrics related to the subject_id
        sub_strands = SubStrand.query.filter_by(subject_id=subject_id,grade_id=grade_id).all()
        strands = Strand.query.filter_by(subject_id=subject_id,grade_id=grade_id).all()
        learning_outcomes = LearningOutcome.query.filter_by(subject_id=subject_id,grade_id=grade_id).all()
        assessment_rubrics = AssessmentRubic.query.filter_by(subject_id=subject_id,grade_id=grade_id).all()

        # Serialize the data
        result_sub_strands = subStrandSchema.dump(sub_strands, many=True)
        result_strands = strandSchema.dump(strands, many=True)
        result_learning_outcomes = learningOutcomeSchema.dump(learning_outcomes, many=True)
        result_assessment_rubrics = assessmentRubicSchema.dump(assessment_rubrics, many=True)

        # Return the serialized data
        return make_response(jsonify({
            "sub_strands": result_sub_strands,
            "strands": result_strands,
            "learning_outcomes": result_learning_outcomes,
            "assessment_rubrics": result_assessment_rubrics
        }), 200)

   
    @superAdmin_required()
    def post(self):
        data = post_args.parse_args()

        # Create new entries in each respective table
        new_sub_strand = SubStrand(substrand_name=data['substrand_name'], subject_id=data['subject_id'], grade_id=data['grade_id'])
        new_strand = Strand(strand_name=data['strand_name'], subject_id=data['subject_id'], grade_id=data['grade_id'])
        new_learning_outcome = LearningOutcome(learning_outcomes=data['learning_outcomes'], subject_id=data['subject_id'], grade_id=data['grade_id'])

        # Add entries to the database session and commit changes
        db.session.add(new_sub_strand)
        db.session.add(new_strand)
        db.session.add(new_learning_outcome)
        db.session.commit()

        # Create and save the four assessment rubrics
        new_assessment_rubrics = []
        for assessment_rubric_data in data['assessment_rubrics']:
            assessment_rubric = AssessmentRubic(assessment_rubics=assessment_rubric_data, subject_id=data['subject_id'], grade_id=data['grade_id'], learning_outcome_id=new_learning_outcome.id)
            db.session.add(assessment_rubric)
            new_assessment_rubrics.append(assessment_rubric)

        db.session.commit()

        # Serialize and return the newly created entries
        result_sub_strand = subStrandSchema.dump(new_sub_strand)
        result_strand = strandSchema.dump(new_strand)
        result_learning_outcome = learningOutcomeSchema.dump(new_learning_outcome)
        result_assessment_rubrics = [assessmentRubicSchema.dump(ar) for ar in new_assessment_rubrics]

        return make_response(jsonify({
            "sub_strand": result_sub_strand,
            "strand": result_strand,
            "learning_outcome": result_learning_outcome,
            "assessment_rubrics": result_assessment_rubrics
        }), 201)

api.add_resource(SubjectDetails, '/subject_details')

@superAdmin_required()
def patch(self, subject_id):
    data = patch_args.parse_args()

    # Update existing entries in each respective table
    sub_strand = SubStrand.query.filter_by(subject_id=subject_id, grade_id=data['grade_id']).first()
    if sub_strand:
        sub_strand.substrand_name = data['substrand_name']
        # Update other attributes of sub_strand as needed

    strand = Strand.query.filter_by(subject_id=subject_id, grade_id=data['grade_id']).first()
    if strand:
        strand.strand_name = data['strand_name']
        # Update other attributes of strand as needed

    learning_outcome = LearningOutcome.query.filter_by(subject_id=subject_id, grade_id=data['grade_id']).first()
    if learning_outcome:
        learning_outcome.learning_outcomes = data['learning_outcomes']
        # Update other attributes of learning_outcome as needed

    assessment_rubic = AssessmentRubic.query.filter_by(subject_id=subject_id, grade_id=data['grade_id']).first()
    if assessment_rubic:
        assessment_rubic.assessment_rubics = data['assessment_rubrics']
        # Update other attributes of assessment_rubic as needed

    # Commit changes to the database session
    db.session.commit()

    # Serialize and return the updated entries
    result_sub_strand = subStrandSchema.dump(sub_strand) if sub_strand else None
    result_strand = strandSchema.dump(strand) if strand else None
    result_learning_outcome = learningOutcomeSchema.dump(learning_outcome) if learning_outcome else None
    result_assessment_rubic = assessmentRubicSchema.dump(assessment_rubic) if assessment_rubic else None

    return make_response(jsonify({
        "sub_strand": result_sub_strand,
        "strand": result_strand,
        "learning_outcome": result_learning_outcome,
        "assessment_rubic": result_assessment_rubic,
    }), 200)

@superAdmin_required()
def delete(self, subject_id,grade_id):
    # Delete entries in each respective table based on the subject_id and grade_id
    SubStrand.query.filter_by(subject_id=subject_id, grade_id=grade_id).delete()
    Strand.query.filter_by(subject_id=subject_id, grade_id=grade_id).delete()
    LearningOutcome.query.filter_by(subject_id=subject_id, grade_id=grade_id).delete()
    AssessmentRubic.query.filter_by(subject_id=subject_id, grade_id=grade_id).delete()

    # Commit changes to the database session
    db.session.commit()

    return make_response(jsonify({"message": "Entries deleted successfully"}), 200)

api.add_resource(SubjectDetails, '/subjects/<string:subject_id>/grades/<string:grade_id>')
