from flask import Blueprint, make_response, jsonify,request
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required
from models import SubStrand, Strand, LearningOutcome, AssessmentRubic, db,generate_uuid
from serializer import subStrandSchema, strandSchema, learningOutcomeSchema, assessmentRubicSchema
from auth import admin_required, superAdmin_required
from werkzeug.exceptions import HTTPException

subject_details_bp = Blueprint('subject_details_bp', __name__)
api = Api(subject_details_bp)

post_args = reqparse.RequestParser()
patch_args = reqparse.RequestParser()

# Define the parser for other fields
post_args = reqparse.RequestParser()
post_args.add_argument('substrand_name', type=str, required=True, help="Sub-strand name is required")
post_args.add_argument('strand_name', type=str, required=True, help="Strand name is required")
post_args.add_argument('learning_outcomes', type=str, required=True, help="Learning outcomes are required")
post_args.add_argument('assessment_rubrics', type=list, required=True, help="Assessment rubrics are required")

patch_args.add_argument('substrand_name', type=str)
patch_args.add_argument('strand_name', type=str)
patch_args.add_argument('learning_outcomes', type=str)
patch_args.add_argument('assessment_rubrics', type=str)
patch_args.add_argument('grade_id', type=str)
patch_args.add_argument('subject_id', type=str)



class SubjectPostGradeDetails(Resource):
    # @superAdmin_required()
    @jwt_required()
    def post(self, grade_id, subject_id):
        try:
            data = request.get_json()
          

            # Save Strand
            strand_id = generate_uuid()
            strand = Strand(
                id=strand_id,
                strand_name=data['strand_name'],
                subject_id=subject_id,
                grade_id=grade_id
            )
            db.session.add(strand)
          

            # Collect response data
            response_data = {
                'strand_id': strand_id,
                'strand_name': data['strand_name'],
                'substrands': []
            }
           

            # Save SubStrands
            for substrand_data in data['substrands']:
                substrand_id = generate_uuid()
                substrand = SubStrand(
                    id=substrand_id,
                    substrand_name=substrand_data['substrand_name'],
                    strand_id=strand_id,
                    subject_id=subject_id,
                    grade_id=grade_id
                )
                db.session.add(substrand)
               

                # Collect SubStrand data
                substrand_info = {
                    'substrand_id': substrand_id,
                    'substrand_name': substrand_data['substrand_name'],
                    'learning_outcomes': []
                }

                # Save Learning Outcomes
                for lo_data in substrand_data['learning_outcomes']:
                    lo_id = generate_uuid()
                    learning_outcome = LearningOutcome(
                        id=lo_id,
                        learning_outcomes=lo_data['learning_outcome'],
                        grade_id=grade_id,
                        subject_id=subject_id,
                        strand_id=strand_id,
                        sub_strand_id=substrand_id
                    )
                    db.session.add(learning_outcome)
                  

                    # Collect Learning Outcome data
                    learning_outcome_info = {
                        'learning_outcome_id': lo_id,
                        'learning_outcome': lo_data['learning_outcome'],
                        'assessment_rubrics': []
                    }

                    # Save Assessment Rubrics
                    for rubric_data in lo_data['assessment_rubrics']:
                        rubric_id = generate_uuid()
                        assessment_rubic = AssessmentRubic(
                            id=rubric_id,
                            assessment_rubics=rubric_data['assessment_rubics'],
                            assessment_rubic_mark=rubric_data['assessment_rubic_mark'],
                            grade_id=grade_id,
                            subject_id=subject_id,
                            strand_id=strand_id,
                            sub_strand_id=substrand_id,
                            learning_outcome_id=lo_id
                        )
                        db.session.add(assessment_rubic)
                       
                        # Collect Assessment Rubric data
                        assessment_rubric_info = {
                            'assessment_rubic_id': rubric_id,
                            'assessment_rubics': rubric_data['assessment_rubics'],
                            'assessment_rubic_mark': rubric_data['assessment_rubic_mark']
                        }
                        learning_outcome_info['assessment_rubrics'].append(assessment_rubric_info)

                    # Add Learning Outcome to SubStrand
                    substrand_info['learning_outcomes'].append(learning_outcome_info)

                # Add SubStrand to Strand
                response_data['substrands'].append(substrand_info)

            
            db.session.commit()

           
            final_response = {
                "message": "Data saved successfully",
                "data": response_data
            }
            
           
            response = jsonify(final_response)
            response.status_code = 201  
            

            return response  

        except Exception as e:
            db.session.rollback()
            print("Exception occurred:", str(e))  # Debug: Print the exception message
            return jsonify({"message": str(e)}), 500

# Route definition
api.add_resource(SubjectPostGradeDetails, '/grades/<string:grade_id>/subjects/<string:subject_id>')



# Route definition
















class SubjectDetailsById(Resource):

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
  
api.add_resource(SubjectDetailsById, '/subjects_details/<string:subject_id>/<string:grade_id>')


    
class SubjectGradePatchDetails(Resource):
    @jwt_required()
    def patch(self, strand_id):
        try:
            data = request.get_json()

            # Update Strand
            strand = Strand.query.filter_by(id=strand_id).first()
            if not strand:
                return make_response(jsonify({"message": "Strand not found"}), 404)

            strand.strand_name = data.get('strand_name', strand.strand_name)
            db.session.add(strand)

            # Update SubStrands
            for substrand_data in data.get('substrands', []):
                substrand = SubStrand.query.filter_by(
                    id=substrand_data['id'],
                    strand_id=strand_id
                ).first()

                if not substrand:
                    # If SubStrand does not exist, create a new one
                    substrand_id = generate_uuid()
                    substrand = SubStrand(
                        id=substrand_id,
                        substrand_name=substrand_data['substrand_name'],
                        strand_id=strand_id,
                        subject_id=data.get('subject_id'),
                        grade_id=data.get('grade_id')
                    )
                else:
                    substrand.substrand_name = substrand_data['substrand_name']

                db.session.add(substrand)

                # Update Learning Outcomes
                for lo_data in substrand_data.get('learning_outcomes', []):
                    learning_outcome = LearningOutcome.query.filter_by(
                        id=lo_data['id'],
                        sub_strand_id=substrand.id
                    ).first()

                    if not learning_outcome:
                        # If LearningOutcome does not exist, create a new one
                        lo_id = generate_uuid()
                        learning_outcome = LearningOutcome(
                            id=lo_id,
                            learning_outcomes=lo_data['learning_outcome'],
                            grade_id=data.get('grade_id'),
                            subject_id=data.get('subject_id'),
                            strand_id=strand_id,
                            sub_strand_id=substrand.id
                        )
                    else:
                        learning_outcome.learning_outcomes = lo_data['learning_outcome']

                    db.session.add(learning_outcome)

                    # Update Assessment Rubrics
                    for rubric_data in lo_data.get('assessment_rubrics', []):
                        assessment_rubic = AssessmentRubic.query.filter_by(
                            id=rubric_data['id'],
                            learning_outcome_id=learning_outcome.id
                        ).first()

                        if not assessment_rubic:
                            # If AssessmentRubic does not exist, create a new one
                            rubric_id = generate_uuid()
                            assessment_rubic = AssessmentRubic(
                                id=rubric_id,
                                assessment_rubics=rubric_data['assessment_rubrics'],
                                assessment_rubic_mark=rubric_data['assessment_rubic_mark'],
                                grade_id=data.get('grade_id'),
                                subject_id=data.get('subject_id'),
                                strand_id=strand_id,
                                sub_strand_id=substrand.id,
                                learning_outcome_id=learning_outcome.id
                            )
                        else:
                            assessment_rubic.assessment_rubics = rubric_data['assessment_rubrics']
                            assessment_rubic.assessment_rubic_mark = rubric_data['assessment_rubic_mark']

                        db.session.add(assessment_rubic)

            db.session.commit()
            return make_response(jsonify({
                "message": "Data updated successfully",
                "data": data
            }), 200)

        except Exception as e:
            db.session.rollback()
            error_message = str(e)  # Ensure the exception message is a string
            print(f"Error: {error_message}")  # Print error for debugging
            return make_response(jsonify({"message": error_message}), 500)

api.add_resource(SubjectGradePatchDetails, '/strand_update/<string:strand_id>')






class SubjectGradeDeleteDetails(Resource):
    # @superAdmin_required()
    @jwt_required()
    def delete(self, strand_id):
        try:
            # Retrieve the Strand
            strand = Strand.query.filter_by(id=strand_id).first()
            if not strand:
                return make_response(jsonify({"message": "Strand not found"}), 404)

            # Retrieve associated SubStrands
            substrands = SubStrand.query.filter_by(strand_id=strand_id).all()

            # Delete associated Learning Outcomes and Assessment Rubrics
            for substrand in substrands:
                learning_outcomes = LearningOutcome.query.filter_by(sub_strand_id=substrand.id).all()
                for learning_outcome in learning_outcomes:
                    assessment_rubrics = AssessmentRubic.query.filter_by(learning_outcome_id=learning_outcome.id).all()
                    for assessment_rubic in assessment_rubrics:
                        db.session.delete(assessment_rubic)
                    db.session.delete(learning_outcome)

                db.session.delete(substrand)

            # Delete the Strand
            db.session.delete(strand)

            # Commit the transaction
            db.session.commit()
            return make_response(jsonify({"message": "Data deleted successfully"}), 200)

        except Exception as e:
            db.session.rollback()
            error_message = str(e)  # Ensure the exception message is a string
            print(f"Error: {error_message}")  # Print error for debugging
            return make_response(jsonify({"message": error_message}), 500)

api.add_resource(SubjectGradeDeleteDetails, '/strand_delete/<string:strand_id>')

