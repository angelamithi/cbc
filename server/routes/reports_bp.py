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
post_args.add_argument("assessment_rubic_id", type=str, required=True, help="Assessment Rubric ID is required")

patch_args = reqparse.RequestParser()
patch_args.add_argument("assessment_rubic_id", type=str, help="Assessment Rubric ID")
patch_args.add_argument("updates", type=list, location='json', help="List of updates")

def get_school_id_from_session():
    claims = get_jwt()
    return claims.get("school_id")



class CreateStudentReport(Resource):
    @jwt_required()
    def post(self):
        school_id = get_school_id_from_session()
        if not school_id:
            return make_response(jsonify({'error': 'School ID not found in session'}), 401)
        
        args = post_args.parse_args()

        # Fetch the assessment rubric mark
        assessment_rubic = AssessmentRubic.query.filter_by(id=args['assessment_rubic_id']).first()
        if not assessment_rubic:
            return make_response(jsonify({'error': 'Assessment Rubric not found'}), 404)

        single_mark = assessment_rubic.assessment_rubic_mark

        # Determine the grade flags based on the single mark
        grade_ee = single_mark == 4
        grade_me = single_mark == 3
        grade_ae = single_mark == 2
        grade_be = single_mark == 1

        # Create a new report
        new_report = Report(
            school_id=school_id,
            student_id=args['student_id'],
            subject_id=args['subject_id'],
            grade_id=args['grade_id'],
            year_id=args['year_id'],
            staff_id=args['staff_id'],
            stream_id=args['stream_id'],
            assessment_rubic_id=args['assessment_rubic_id'],
            grade_ee=grade_ee,
            grade_me=grade_me,
            grade_ae=grade_ae,
            grade_be=grade_be,
            single_mark=single_mark  # Ensure this is an integer
        )

        db.session.add(new_report)
        db.session.commit()

        # Serialize the data
      
        result = reportSchema.dump(new_report)

        return make_response(jsonify(result), 201)

# Add the route for the API resource
api.add_resource(CreateStudentReport, '/create_student_report')


class RetrieveStudentReport(Resource):

    @jwt_required()
    def get(self, grade_id, student_id, subject_id, year_id):
        # Fetch student, grade, subject, and year details
        year = Year.query.get(year_id)
        grade = Grade.query.get(grade_id)
        # stream = Stream.query.get(stream_id)
        # staff_id = Staff.query.get(staff_id)
        student = Student.query.get(student_id)        
        subject = Subject.query.get(subject_id)
     

        
        if not grade:
             return make_response(jsonify({"message": "Invalid grade"}), 404)
        if not subject:
             return make_response(jsonify({"message": "Invalid subject"}), 404)
        if not year:
             return make_response(jsonify({"message": "Invalid year"}), 404)
        if not student :
            return make_response(jsonify({"message": "Invalid student"}), 404)


        # Fetch related data
        sub_strands = SubStrand.query.filter_by(subject_id=subject_id, grade_id=grade_id).all()
        strands = Strand.query.filter_by(subject_id=subject_id, grade_id=grade_id).all()
        learning_outcomes = LearningOutcome.query.filter_by(subject_id=subject_id, grade_id=grade_id).all()
        assessment_rubrics = AssessmentRubic.query.filter_by(subject_id=subject_id, grade_id=grade_id).all()

        # Fetch the report details for the student
        reports = Report.query.filter_by(student_id=student_id, grade_id=grade_id, subject_id=subject_id, year_id=year_id).first()

        if not reports:
            return make_response(jsonify({"message": "Report not found"}), 404)
        
        # Serialize the data
        result_report=reportSchema.dump(reports)
        result_strands = strandSchema.dump(strands, many=True)
        result_sub_strands = subStrandSchema.dump(sub_strands, many=True)        
        result_learning_outcomes = learningOutcomeSchema.dump(learning_outcomes, many=True)
        result_assessment_rubrics = assessmentRubicSchema.dump(assessment_rubrics, many=True)

        # Return the serialized data
        return make_response(jsonify({
            "reports":result_report,
            "strands": result_strands,
            "sub_strands": result_sub_strands,          
            "learning_outcomes": result_learning_outcomes,
            "assessment_rubrics": result_assessment_rubrics
        }), 200)

      
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