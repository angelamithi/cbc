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
        report = FormativeReport.query.filter_by(student_id=student_id, grade_id=grade_id, subject_id=subject_id, year_id=current_year).first()

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

        # Construct the nested response structure
        response_data = {
            "grade": {
                "grade_id": grade.id,
                "grade_name": grade.grade,
                "subjects": [
                    {
                        "subject_id": subject.id,
                        "subject_name": subject.subject_name,
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
                ]
            },
            # "report": result_report
        }

        # Return the serialized data
        return make_response(jsonify(response_data), 200)
api.add_resource(RetrieveStudentReport, '/get_student_report/<string:grade_id>/<string:student_id>/<string:subject_id>')





class UpdateStudentReport(Resource):
    @jwt_required()
    def patch(self, grade_id, student_id, subject_id):
        school_id = get_school_id_from_session()
        parser = reqparse.RequestParser()
        parser.add_argument('rubrics', type=list, location='json', required=True, help='List of rubrics is required')

        # Parse the arguments from the request
        args = parser.parse_args()
        rubrics = args['rubrics']

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

            # Loop through each rubric and update accordingly
            for rubric in rubrics:
                rubric_id = rubric['assessment_rubic_id']
                rubric_mark = rubric['assessment_rubic_mark']
                is_selected = 1 if rubric['is_selected'] else 0  # Convert boolean to 1 or 0

                # Update the report fields based on the rubric data
                report.assessment_rubic_id = rubric_id
                report.assessment_rubic_mark = rubric_mark

                # Update is_selected for the assessment rubric that was deselected
                if is_selected == 1:
                    AssessmentRubic.query.filter_by(id=rubric_id).update({"is_selected": 1})
                else:
                    AssessmentRubic.query.filter_by(id=rubric_id).update({"is_selected": 0})

            # Commit changes to the database
            db.session.commit()

            # Optionally, you can return the updated report or a success message
            return make_response(jsonify({"message": "Report updated successfully"}), 200)

        except Exception as e:
            # Handle exceptions, e.g., if report or rubrics are not found
            return make_response(jsonify({"error": str(e)}), 404)

api.add_resource(UpdateStudentReport, '/update_student_report/<string:grade_id>/<string:student_id>/<string:subject_id>')



class CreateStudentReport(Resource):
    @jwt_required()
    def post(self):
        school_id=get_school_id_from_session()
        parser = reqparse.RequestParser()
        parser.add_argument('grade_id', type=str, required=True, help='Grade ID is required')
        parser.add_argument('student_id', type=str, required=True, help='Student ID is required')
        parser.add_argument('subject_id', type=str, required=True, help='Subject ID is required')
        parser.add_argument('year_id', type=str, required=True, help='Year ID is required')
        parser.add_argument('staff_id', type=str, required=True, help='Staff is required')
        parser.add_argument('stream_id', type=str, required=True, help='Stream is required')

        parser.add_argument('rubrics', type=list, location='json', required=True, help='List of rubrics is required')

        # Fetch the current year object
        current_year = datetime.now().year
        year_object = Year.query.filter_by(year_name=current_year).first()

        if not year_object:
                return make_response(jsonify({"error": f"No year found for {current_year}"}), 404)

        year_id = year_object.id
        
        args = parser.parse_args()
        grade_id = args['grade_id']
        student_id = args['student_id']
        subject_id = args['subject_id']
        year_id = year_id
        stream_id = args['stream_id']
        staff_id = args['staff_id']
        rubrics = args['rubrics']

        try:
            # Loop through each rubric and create a new report entry
            for rubric in rubrics:
                rubric_id = rubric['assessment_rubic_id']
                rubric_mark = rubric['assessment_rubic_mark']
                is_selected = 1 if rubric['is_selected'] else 0  # Convert boolean to 1 or 0

                # Create a new FormativeReport instance for each rubric
                new_report = FormativeReport(
                    school_id=school_id,
                    student_id=student_id,
                    grade_id=grade_id,
                    subject_id=subject_id,
                    year_id=year_id,
                    staff_id=staff_id,
                    stream_id=stream_id,
                    assessment_rubic_id=rubric_id,
                    assessment_rubic_mark=rubric_mark,
                    is_selected=is_selected
                )

                # Add new_report to session
                db.session.add(new_report)

            # Commit changes to the database
            db.session.commit()

            # Optionally, you can return the newly created report or a success message
            return make_response(jsonify({"message": "Report created successfully"}), 201)

        except Exception as e:
            # Handle exceptions, e.g., if there's an error in creating the report or rubrics are not found
            db.session.rollback()  # Rollback changes in case of an error
            return make_response(jsonify({"error": str(e)}), 400)

# Add the route for creating a new student report
api.add_resource(CreateStudentReport, '/create_student_report')
