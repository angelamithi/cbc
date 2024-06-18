from flask import Blueprint, make_response, jsonify,session,request
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required
from models import Report,Student,db
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
post_args.add_argument('single_mark', type=int, required=True, help='Single Mark is required')
post_args.add_argument('grade_ee', type=bool, default=False)
post_args.add_argument('grade_me', type=bool, default=False)
post_args.add_argument('grade_ae', type=bool, default=False)
post_args.add_argument('grade_be', type=bool, default=False)

patch_args = reqparse.RequestParser()
patch_args.add_argument('single_mark', type=int)
patch_args.add_argument('grade_ee', type=bool)
patch_args.add_argument('grade_me', type=bool)
patch_args.add_argument('grade_ae', type=bool)
patch_args.add_argument('grade_be', type=bool)

class ReportDetails(Resource):
    @jwt_required()
    def get_student_reports(grade_id, student_id):
        school_id = session.get('school_id')
        if not school_id:
            return jsonify({'message': 'School ID not found in session'}), 400

        student = Student.query.filter_by(id=student_id, school_id=school_id, grade_id=grade_id).first()
        if not student:
            return jsonify({'message': 'Student not found for the given school and grade'}), 404

        reports = Report.query.filter_by(student_id=student_id).all()
        result = reportSchema.dump(reports, many=True)
        return make_response(jsonify(result), 200)

    class ReportDetails(Resource):
        @teacher_required()
        def create_student_report(self):
            data = post_args.parse_args()
            school_id = data.get('school_id')
            student_id = data.get('student_id')
            
            student = Student.query.filter_by(id=student_id, school_id=school_id, grade_id=data['grade_id']).first()
            if not student:
                return jsonify({'message': 'Student not found for the given school and grade'}), 404

            # Automatically generate single_mark based on grade_ee, grade_me, grade_ae, grade_be
            grade_ee = data.get('grade_ee')
            grade_me = data.get('grade_me')
            grade_ae = data.get('grade_ae')
            grade_be = data.get('grade_be')

            if grade_ee:
                single_mark = 4
            elif grade_me:
                single_mark = 3
            elif grade_ae:
                single_mark = 2
            elif grade_be:
                single_mark = 1
            else:
                single_mark = None  # Handle other cases as needed

            # Create new_report with the automatically generated single_mark
            new_report = Report(
                school_id=school_id,
                staff_id=data['staff_id'],
                year_id=data['year_id'],
                term_id=data['term_id'],
                grade_id=data['grade_id'],
                stream_id=data['stream_id'],
                student_id=student_id,
                subject_id=data['subject_id'],
                single_mark=single_mark,
                grade_ee=data['grade_ee'],
                grade_me=data['grade_me'],
                grade_ae=data['grade_ae'],
                grade_be=data['grade_be']
            )

            db.session.add(new_report)
            db.session.commit()

            return make_response({'message': 'Report created successfully'}, 201)

        
api.add_resource(ReportDetails, '/reports')

class ReportById(Resource):
        
   
    @admin_required()
    def delete(self, school_id, grade_id, student_id, report_id):
        report = Report.query.filter_by(id=report_id, school_id=school_id, grade_id=grade_id, student_id=student_id).first()
        if not report:
            return make_response(jsonify({"error": "Report not found"}), 404)

        db.session.delete(report)
        db.session.commit()
        return make_response(jsonify({"message": "Report deleted successfully"}), 200)


    @teacher_required()
    def edit_student_report(grade_id, student_id, report_id):
        school_id = session.get('school_id')
        if not school_id:
            return jsonify({'message': 'School ID not found in session'}), 400

        report = Report.query.filter_by(id=report_id, school_id=school_id, grade_id=grade_id, student_id=student_id).first()
        if not report:
            return jsonify({'message': 'Report not found for the given school, grade, and student'}), 404

        args = patch_args.parse_args()
        grade_ee = args['grade_ee']
        grade_me = args['grade_me']
        grade_ae = args['grade_ae']
        grade_be = args['grade_be']

        # Update single_mark based on grade_ee, grade_me, grade_ae, grade_be values
        if grade_ee:
            report.single_mark = 4
        elif grade_me:
            report.single_mark = 3
        elif grade_ae:
            report.single_mark = 2
        elif grade_be:
            report.single_mark = 1

        db.session.commit()
        return jsonify({'message': 'Report updated successfully'}), 200

api.add_resource(ReportById, '/reports/<string:id>')