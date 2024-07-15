from flask import Blueprint, make_response, jsonify,session,request
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required,get_jwt
from models import Report,Student,db
from serializer import reportSchema,subStrandSchema,strandSchema,learningOutcomeSchema,assessmentRubicSchema
from auth import admin_required, superAdmin_required,teacher_required
from models import Strand,SubStrand,LearningOutcome,AssessmentRubic,Grade,Subject,Staff,Stream,Year
from sqlalchemy.orm import joinedload

reports_bp = Blueprint('reports_bp', __name__)
api = Api(reports_bp)


post_args = reqparse.RequestParser()


post_args.add_argument("student_id", type=str, required=True, help="Student ID is required")
post_args.add_argument("subject_id", type=str, required=True, help="Subject ID is required")
post_args.add_argument("grade_id", type=str, required=True, help="Grade ID is required")
post_args.add_argument("year_id", type=str, required=True, help="Year ID is required")
post_args.add_argument("staff_id", type=str, required=True, help="Staff ID is required")
post_args.add_argument("stream_id", type=str, required=True, help="Stream ID is required")
post_args.add_argument("assessment_rubic_id", type=str, help="Assessment Rubric ID")
post_args.add_argument("assessment_rubic_ids", type=list, location='json', help="List of Assessment Rubric IDs")

patch_args = reqparse.RequestParser()
patch_args.add_argument("assessment_rubic_id", type=str, help="Assessment Rubric ID")
patch_args.add_argument("updates", type=list, location='json', help="List of updates")

def get_school_id_from_session():
    claims = get_jwt()
    return claims.get("school_id")



class RetrieveStudentReport(Resource):

    @jwt_required()
    def get(self, grade_id, student_id, subject_id, year_id):
        # Fetch student, grade, subject, and year details
        year = Year.query.get(year_id)
        grade = Grade.query.get(grade_id)
        student = Student.query.get(student_id)
        subject = Subject.query.get(subject_id)

        if not grade:
            return make_response(jsonify({"message": "Invalid grade"}), 404)
        if not subject:
            return make_response(jsonify({"message": "Invalid subject"}), 404)
        if not year:
            return make_response(jsonify({"message": "Invalid year"}), 404)
        if not student:
            return make_response(jsonify({"message": "Invalid student"}), 404)

        # Fetch related data
        strands = Strand.query.filter_by(subject_id=subject_id, grade_id=grade_id).all()
        sub_strands = SubStrand.query.filter_by(subject_id=subject_id, grade_id=grade_id).all()
        learning_outcomes = LearningOutcome.query.filter_by(subject_id=subject_id, grade_id=grade_id).all()
        assessment_rubrics = AssessmentRubic.query.filter_by(subject_id=subject_id, grade_id=grade_id).all()

        # Fetch the report details for the student
        report = Report.query.filter_by(student_id=student_id, grade_id=grade_id, subject_id=subject_id, year_id=year_id).first()

        if not report:
            return make_response(jsonify({"message": "Report not found"}), 404)

        # Serialize the data
        result_report = reportSchema.dump(report)
        result_strands = strandSchema.dump(strands, many=True)
        result_sub_strands = subStrandSchema.dump(sub_strands, many=True)
        result_learning_outcomes = learningOutcomeSchema.dump(learning_outcomes, many=True)
        result_assessment_rubrics = assessmentRubicSchema.dump(assessment_rubrics, many=True)

        # Construct a map for learning outcome to grade type for each assessment rubric
        learning_outcome_grade_types = {}
        for assessment_rubic in assessment_rubrics:
            lo_id = assessment_rubic.learning_outcome_id
            grade_type = None
            report_for_rubic = Report.query.filter_by(
                student_id=student_id,
                grade_id=grade_id,
                subject_id=subject_id,
                year_id=year_id,
                assessment_rubic_id=assessment_rubic.id  # Assuming there's a foreign key like this in Report
            ).first()
            
            if report_for_rubic:
                if report_for_rubic.grade_ee == 1:
                    grade_type = "EE"
                elif report_for_rubic.grade_me == 1:
                    grade_type = "ME"
                elif report_for_rubic.grade_ae == 1:
                    grade_type = "AE"
                elif report_for_rubic.grade_be == 1:
                    grade_type = "BE"

            learning_outcome_grade_types[lo_id] = grade_type

        # Add grade type to each learning outcome
        for outcome in result_learning_outcomes:
            outcome['grade_type'] = learning_outcome_grade_types.get(outcome['id'], None)

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
                                                "grade_type": outcome['grade_type'],
                                                "assessment_rubrics": [
                                                    {
                                                        "assessment_rubic_id": rubric.id,
                                                        "assessment_rubic_name": rubric.assessment_rubics,
                                                        # Add other attributes you need from AssessmentRubic
                                                        # Fetch from report_for_rubic.grade_ee, etc.
                                                        "grade_ee": report_for_rubic.grade_ee if report_for_rubic else None,
                                                        "grade_me": report_for_rubic.grade_me if report_for_rubic else None,
                                                        "grade_ae": report_for_rubic.grade_ae if report_for_rubic else None,
                                                        "grade_be": report_for_rubic.grade_be if report_for_rubic else None
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

# Add the route for the API resource
api.add_resource(RetrieveStudentReport, '/get_student_report/<string:grade_id>/<string:student_id>/<string:subject_id>/<string:year_id>')



class UpdateStudentReport(Resource):
    @jwt_required()
    def patch(self, grade_id, student_id, subject_id, year_id):
        args = patch_args.parse_args()

        assessment_rubic_id = args.get('assessment_rubic_id')
        updates = args.get('updates')

        report = Report.query.filter_by(student_id=student_id, grade_id=grade_id, subject_id=subject_id, year_id=year_id).first()

        if not report:
            return make_response(jsonify({"message": "Report not found"}), 404)

        if assessment_rubic_id:
            assessment_rubic = AssessmentRubic.query.filter_by(id=assessment_rubic_id).first()
            if not assessment_rubic:
                return make_response(jsonify({'error': f'Assessment Rubric {assessment_rubic_id} not found'}), 404)

            single_mark = assessment_rubic.assessment_rubic_mark

            # Update the report with new assessment rubric and marks
            report.assessment_rubic_id = assessment_rubic_id
            report.single_mark = single_mark
            report.grade_ee = single_mark == 4
            report.grade_me = single_mark == 3
            report.grade_ae = single_mark == 2
            report.grade_be = single_mark == 1

        if updates:
            # Process each update separately
            for update in updates:
                assessment_rubic_id = update.get("assessment_rubic_id")
                assessment_rubic = AssessmentRubic.query.filter_by(id=assessment_rubic_id).first()

                if not assessment_rubic:
                    return make_response(jsonify({'error': f'Assessment Rubric {assessment_rubic_id} not found'}), 404)

                single_mark = assessment_rubic.assessment_rubic_mark

                # Check if a report with the same keys already exists
                existing_report = Report.query.filter_by(
                    student_id=student_id,
                    grade_id=grade_id,
                    subject_id=subject_id,
                    year_id=year_id,
                    assessment_rubic_id=assessment_rubic_id
                ).first()

                if existing_report:
                    # Update the existing report with new assessment rubric and marks
                    existing_report.single_mark = single_mark
                    existing_report.grade_ee = single_mark == 4
                    existing_report.grade_me = single_mark == 3
                    existing_report.grade_ae = single_mark == 2
                    existing_report.grade_be = single_mark == 1
                else:
                    # Create a new report for the current assessment rubric
                    new_report = Report(
                        school_id=report.school_id,
                        student_id=student_id,
                        subject_id=subject_id,
                        grade_id=grade_id,
                        year_id=year_id,
                        staff_id=report.staff_id,
                        stream_id=report.stream_id,
                        assessment_rubic_id=assessment_rubic_id,
                        grade_ee=single_mark == 4,
                        grade_me=single_mark == 3,
                        grade_ae=single_mark == 2,
                        grade_be=single_mark == 1,
                        single_mark=single_mark  # Ensure this is an integer
                    )
                    db.session.add(new_report)

        db.session.commit()

        # Serialize the data
        result = reportSchema.dump(report)

        return make_response(jsonify(result), 200)


api.add_resource(UpdateStudentReport, '/update_student_report/<string:grade_id>/<string:student_id>/<string:subject_id>/<string:year_id>')