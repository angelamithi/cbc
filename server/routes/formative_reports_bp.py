from flask import Blueprint, make_response, jsonify,session,request
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required,get_jwt
from serializer import formative_report_schema,subStrandSchema,strandSchema,learningOutcomeSchema,assessmentRubicSchema
from auth import admin_required, superAdmin_required,teacher_required
from models import Strand,SubStrand,LearningOutcome,AssessmentRubic,Grade,Subject,Staff,Stream,Year,FormativeReport,Student,db
from sqlalchemy.orm import joinedload

from datetime import datetime

formative_reports_bp = Blueprint('formative_reports_bp', __name__)
api = Api(formative_reports_bp)




def get_school_id_from_session():
    claims = get_jwt()
    return claims.get("school_id")




class RetrieveStudentReport(Resource):
    @jwt_required()
    def get(self, grade_id, student_id, subject_id):
        school_id = get_school_id_from_session()
        
        # Fetch the current year object
        current_year = datetime.now().year
        year_object = Year.query.filter_by(year_name=current_year).first()

        if not year_object:
            return make_response(jsonify({"error": f"No year found for {current_year}"}), 404)

        year_id = year_object.id
        
        # Fetch student, grade, subject details
        grade = Grade.query.get(grade_id)
        student = Student.query.get(student_id)
        subject = Subject.query.get(subject_id)

        if not grade:
            return make_response(jsonify({"message": "Invalid grade"}), 404)
        if not subject:
            return make_response(jsonify({"message": "Invalid subject"}), 404)
        if not student:
            return make_response(jsonify({"message": "Invalid student"}), 404)

        # Fetch related data
        strands = Strand.query.filter_by(subject_id=subject_id, grade_id=grade_id).all()
        sub_strands = SubStrand.query.filter_by(subject_id=subject_id, grade_id=grade_id).all()
        learning_outcomes = LearningOutcome.query.filter_by(subject_id=subject_id, grade_id=grade_id).all()

        # Fetch assessment rubrics and filter for those related to the current subject and grade
        assessment_rubrics = AssessmentRubic.query.filter_by(subject_id=subject_id, grade_id=grade_id).all()

        # Fetch the report details for the student for the current year
        report = FormativeReport.query.filter_by(student_id=student_id, grade_id=grade_id, subject_id=subject_id, year_id=year_id).first()

        if not report:
            return make_response(jsonify({"message": "Report not found"}), 404)

        # Create a map for learning outcome to grade type (assessment_rubic_id) for each assessment rubric
        learning_outcome_grade_types = {}
        for rubric in assessment_rubrics:
            report_for_rubic = FormativeReport.query.filter_by(
                student_id=student_id,
                grade_id=grade_id,
                subject_id=subject_id,
                year_id=year_id,
                assessment_rubic_id=rubric.id,
                school_id=school_id
            ).first()

            if report_for_rubic and report_for_rubic.is_selected == 1:
                learning_outcome_grade_types[rubric.learning_outcome_id] = rubric.id

        # Serialize the data (assuming strandSchema, subStrandSchema, and learningOutcomeSchema are defined)
        result_strands = strandSchema.dump(strands, many=True)
        result_sub_strands = subStrandSchema.dump(sub_strands, many=True)
        result_learning_outcomes = learningOutcomeSchema.dump(learning_outcomes, many=True)

        # Construct the nested response structure without grade and subject
        response_data = {
            "strands": [
                {
                    "strand_id": strand.id,
                    "strand_name": strand.strand_name,
                    "sub_strands": [
                        {
                            "sub_strand_id": sub_strand.id,
                            "sub_strand_name": sub_strand.substrand_name,
                            "learning_outcomes": [
                                {
                                    "learning_outcome_id": outcome['id'],
                                    "learning_outcome_name": outcome['learning_outcomes'],
                                    "grade_type": learning_outcome_grade_types.get(outcome['id'], None),
                                    "assessment_rubrics": [
                                        {
                                            "assessment_rubic_id": rubric.id,
                                            "assessment_rubic_name": rubric.assessment_rubics,
                                            "assessment_rubic_mark": rubric.assessment_rubic_mark
                                            # Add other attributes you need from AssessmentRubic
                                        }
                                        for rubric in assessment_rubrics
                                        if rubric.learning_outcome_id == outcome['id']
                                    ]
                                }
                                for outcome in result_learning_outcomes
                                if outcome['sub_strand_id'] == sub_strand.id
                            ]
                        }
                        for sub_strand in sub_strands
                        if sub_strand.strand_id == strand.id
                    ]
                }
                for strand in strands
            ]
        }

        # Return the serialized data
        return make_response(jsonify(response_data), 200)

api.add_resource(RetrieveStudentReport, '/get_student_report/<string:grade_id>/<string:subject_id>/<string:student_id>')






class UpdateStudentReport(Resource):
    @jwt_required()
    def patch(self, grade_id, student_id, subject_id):
        school_id = get_school_id_from_session()
        parser = reqparse.RequestParser()
        parser.add_argument('rubrics', type=dict, location='json', help='Rubric data')

        # Parse the arguments from the request
        args = parser.parse_args()
        rubrics = args['rubrics']

        if rubrics is None:
            return make_response(jsonify({"error": "Rubric data is required"}), 400)

        # Check if rubrics is a list or a single dictionary
        if isinstance(rubrics, list):
            rubric_list = rubrics
        elif isinstance(rubrics, dict):
            rubric_list = [rubrics]
        else:
            return make_response(jsonify({"error": "Invalid rubric data format"}), 400)

        try:
            # Fetch the current year object
            current_year = datetime.now().year
            year_object = Year.query.filter_by(year_name=current_year).first()

            if not year_object:
                return make_response(jsonify({"error": f"No year found for {current_year}"}), 404)

            year_id = year_object.id

            # Fetch the report to update
            report = FormativeReport.query.filter_by(student_id=student_id, grade_id=grade_id,
                                                     subject_id=subject_id, year_id=year_id,
                                                     school_id=school_id).first()

            if not report:
                return make_response(jsonify({"error": "Report not found"}), 404)

            # Initialize a list to hold the updated rubrics
            updated_rubrics = []

            # Loop through each rubric and update accordingly
            for rubric in rubric_list:
                rubric_id = rubric.get('assessment_rubic_id')

                if rubric_id:
                    assessment_rubic = AssessmentRubic.query.get(rubric_id)
                    if assessment_rubic:
                        rubric_mark = assessment_rubic.assessment_rubic_mark
                        is_selected = 1
                    else:
                        rubric_mark = 0
                        is_selected = 0
                else:
                    rubric_mark = 0
                    is_selected = 0

                # Update the report for each rubric
                if rubric_id:
                    updated_rubric = FormativeReport.query.filter_by(student_id=student_id, grade_id=grade_id,
                                                                     subject_id=subject_id, year_id=year_id,
                                                                     school_id=school_id, assessment_rubic_id=rubric_id).first()
                    if updated_rubric:
                        updated_rubric.single_mark = rubric_mark
                        updated_rubric.is_selected = is_selected
                        db.session.add(updated_rubric)
                    else:
                        # Handle cases where the rubric is not found in the existing report
                        new_rubric = FormativeReport(
                            student_id=student_id,
                            grade_id=grade_id,
                            subject_id=subject_id,
                            year_id=year_id,
                            school_id=school_id,
                            assessment_rubic_id=rubric_id,
                            single_mark=rubric_mark,
                            is_selected=is_selected
                        )
                        db.session.add(new_rubric)

            # Commit changes to the database
            db.session.commit()

            # Optionally, you can return the updated report or a success message
            return make_response(jsonify({"message": "Report updated successfully"}), 200)

        except Exception as e:
            # Handle exceptions, e.g., if report or rubrics are not found
            return make_response(jsonify({"error": str(e)}), 404)

api.add_resource(UpdateStudentReport, '/update_student_report/<string:grade_id>/<string:subject_id>/<string:student_id>')





