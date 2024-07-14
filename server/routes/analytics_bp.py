from flask import Blueprint,jsonify, make_response,session
from flask_jwt_extended import jwt_required,get_jwt
from flask_restful import Resource, Api,reqparse
from sqlalchemy.sql import func,case
from models import Subject,Report,db,Student,Grade,Year,SubStrand,AssessmentRubic,Strand,Staff,TeacherSubjectGradeStream,LearningOutcome

analytics_bp = Blueprint('analytics_bp', __name__)
api = Api(analytics_bp)
# Overall Performance Analysis

def get_school_id_from_session():
    claims = get_jwt()
    return claims.get("school_id")


class AverageScoresPerSubject(Resource):
    @jwt_required()
    def get(self, grade_id):
        # Query to get the average scores per subject for a specific grade
        school_id = get_school_id_from_session()
        average_scores = (
            db.session.query(
                Subject.subject_name,
                func.avg(Report.single_mark).label('average_score')
            )
            .join(Report, Report.subject_id == Subject.id)
            .filter(Report.grade_id == grade_id,Report.school_id==school_id)
            .group_by(Subject.subject_name)
            .all()
        )

        # Serialize the results
        result = [{'subject_name': subject_name, 'average_score': average_score} for subject_name, average_score in average_scores]
        
        return make_response(jsonify(result), 200)

# Add the new resource to the API
api.add_resource(AverageScoresPerSubject, '/average-scores/grade/<string:grade_id>')

class PerformanceDistribution(Resource):
    @jwt_required()
    def get(self, subject_id,grade_id):
        school_id = get_school_id_from_session()
        
        # Query to fetch all scores for the given subject

        scores = db.session.query(Report.single_mark).filter_by(subject_id=subject_id,grade_id=grade_id,school_id=school_id).all()
        
        if not scores:
            return make_response(jsonify({"message": "No scores found for the given subject"}), 404)
        
        # Convert the scores from a list of tuples to a flat list
        scores = [score[0] for score in scores]
        
        # Calculate the histogram data
        # You can customize the bins as needed
        histogram_data = {}
        bin_size = 10
        for score in scores:
            bin_key = (score // bin_size) * bin_size
            if bin_key not in histogram_data:
                histogram_data[bin_key] = 0
            histogram_data[bin_key] += 1

        # Convert the histogram data to a sorted list of dictionaries for easy frontend use
        histogram_list = [{"range": f"{bin}-{bin + bin_size - 1}", "count": count} for bin, count in sorted(histogram_data.items())]

        return make_response(jsonify(histogram_list), 200)


api.add_resource(PerformanceDistribution, '/performance_distribution/subject/<string:subject_id>/<string:grade_id>')


#Student Performance Trends:
class StudentPerformanceOverTime(Resource):

    @staticmethod
    def count_learning_outcomes(subject_id, grade_id):
        learning_outcomes_count = LearningOutcome.query.filter_by(subject_id=subject_id, grade_id=grade_id).count()
        return learning_outcomes_count

    @staticmethod
    def total_possible_marks(subject_id, grade_id):
        learning_outcome_count = StudentPerformanceOverTime.count_learning_outcomes(subject_id, grade_id)
        total_marks = learning_outcome_count * 4
        return total_marks

    @staticmethod
    def student_total_marks(student_id, subject_id, grade_id, year_id):
        school_id = get_school_id_from_session()
        total_marks_obtained = db.session.query(db.func.sum(Report.single_mark)).filter_by(
            student_id=student_id,
            subject_id=subject_id,
            grade_id=grade_id,
            year_id=year_id,
            school_id=school_id
        ).scalar()
        return total_marks_obtained

    @staticmethod
    def get_student_performance(student_id, subject_id, grade_id, year_id):
        total_possible = StudentPerformanceOverTime.total_possible_marks(subject_id, grade_id)
        total_obtained = StudentPerformanceOverTime.student_total_marks(student_id, subject_id, grade_id, year_id)

        if total_obtained is None:
            total_obtained = 0

        return {
            "total_possible_marks": total_possible,
            "total_obtained_marks": total_obtained,
            "percentage": (total_obtained / total_possible) * 100 if total_possible > 0 else 0
        }
    @jwt_required()
    def get(self, student_id, subject_id, grade_id):
        try:
            # Fetch the student from the database
            student = Student.query.get(student_id)
            if not student:
                return jsonify({'message': 'Student not found'}), 404

            # Fetch subject and grade details
            subject = Subject.query.get(subject_id)
            grade = Grade.query.get(grade_id)
            if not subject or not grade:
                return jsonify({'message': 'Subject or Grade not found'}), 404

            # Fetch all years for which reports are available
            years = Year.query.order_by(Year.year_name).all()

            # Prepare data for the line chart
            performance_data = {
                'student_name': f'{student.first_name} {student.last_name}',
                'subject_name': subject.subject_name,
                'grade_name': grade.grade,
                'years': [],
                'percentages': []
            }

            # Iterate through the years to fetch performance data
            for year in years:
                year_id = year.id
                performance = self.get_student_performance(student_id, subject_id, grade_id, year_id)

                performance_data['years'].append(year.year_name)
                performance_data['percentages'].append(performance['percentage'])

            return make_response(jsonify(performance_data), 200)

        except Exception as e:
            return make_response(jsonify({'message': str(e)}), 500)


# Create routes for the API resources
api.add_resource(StudentPerformanceOverTime, '/students/<string:student_id>/performance/<string:subject_id>/<string:grade_id>')


class ClassPerformanceOverTime(Resource):

    @staticmethod
    def count_learning_outcomes(subject_id, grade_id):
        learning_outcomes_count = LearningOutcome.query.filter_by(subject_id=subject_id, grade_id=grade_id).count()
        return learning_outcomes_count

    @staticmethod
    def total_possible_marks(subject_id, grade_id):
        learning_outcome_count = ClassPerformanceOverTime.count_learning_outcomes(subject_id, grade_id)
        total_marks = learning_outcome_count * 4
        return total_marks
    
    @staticmethod    
    def class_total_marks(subject_id, grade_id, year_id):
        school_id = get_school_id_from_session()
        total_marks_obtained = db.session.query(func.sum(Report.single_mark)).filter_by(
            subject_id=subject_id,
            grade_id=grade_id,
            year_id=year_id,
            school_id=school_id
        ).scalar() or 0  # Use 0 if no marks obtained
       
        
        return total_marks_obtained
    
    @staticmethod    
    def get_class_performance(subject_id, grade_id, year_id):
        
        total_possible = ClassPerformanceOverTime.total_possible_marks(subject_id, grade_id)
        total_obtained = ClassPerformanceOverTime.class_total_marks(subject_id, grade_id, year_id)
        
        percentage = (total_obtained / total_possible) * 100 if total_possible > 0 else 0
        
        return {
            "total_possible_marks": total_possible,
            "total_obtained_marks": total_obtained,
            "percentage": percentage
        }
    
    @jwt_required()    
    def get(self, subject_id, grade_id):
        try:
            # Fetch subject and grade details
            subject = Subject.query.get(subject_id)
            grade = Grade.query.get(grade_id)
            
            if not subject or not grade:
                return make_response(jsonify({'message': 'Subject or Grade not found'}), 404)
            
            # Fetch all years for which reports are available
            years = Year.query.order_by(Year.year_name).all()
            
            # Prepare data for the line chart
            performance_data = {
                'subject_name': subject.subject_name,
                'grade_name': grade.grade,
                'years': [],
                'percentages': []
            }
            
            # Iterate through the years to fetch performance data
            for year in years:
                year_id = year.id
                print(f"Fetching performance for year {year.year_name} with ID {year_id}")
                performance = self.get_class_performance(subject_id, grade_id, year_id)
                
                performance_data['years'].append(year.year_name)
                performance_data['percentages'].append(performance['percentage'])
            
            return make_response(jsonify(performance_data), 200)
        
        except Exception as e:
            return make_response(jsonify({'message': str(e)}), 500)

# Create routes for the API resources
api.add_resource(ClassPerformanceOverTime, '/class/performance/<string:subject_id>/<string:grade_id>')




# distribution_args = reqparse.RequestParser()
# distribution_args.add_argument('subject_id', type=str, required=True, help='Subject ID is required')
# distribution_args.add_argument('grade_id', type=str, required=True, help='Grade ID is required')
# distribution_args.add_argument('year_id', type=str, required=True, help='Year ID is required')


class DistributionAssessmentGrades(Resource):
    def get(self, subject_id, grade_id, year_id):
        school_id = get_school_id_from_session()
        # Query to get average single_mark per student
        average_marks = db.session.query(
            Report.student_id,
            db.func.avg(Report.single_mark).label('avg_mark')
        ).filter(
            Report.subject_id == subject_id,
            Report.grade_id == grade_id,
            Report.year_id == year_id,
            Report.school_id==school_id
        ).group_by(Report.student_id).all()

        if not average_marks:
            return make_response(jsonify({'error': 'No data found for the given criteria'}), 404)

        # Dictionary to count grades
        grade_counts = {
            'EE': 0,
            'ME': 0,
            'AE': 0,
            'BE': 0
        }

        # Aggregate grades
        for mark in average_marks:
            avg_mark = mark.avg_mark

            # Determine grade based on avg_mark
            if avg_mark >= 3.5:
                grade = 'EE'  # Excellent
            elif avg_mark >= 2.5:
                grade = 'ME'  # Good
            elif avg_mark >= 1.5:
                grade = 'AE'  # Average
            else:
                grade = 'BE'  # Below Average

            # Increment grade count
            grade_counts[grade] += 1

        # Construct response data
        response_data = {
            'grade_distribution': grade_counts,
            'student_results': []
        }

        # Prepare student results
        for mark in average_marks:
            student_id = mark.student_id
            avg_mark = mark.avg_mark

            # Determine grade based on avg_mark
            if avg_mark >= 3.5:
                grade = 'EE'  # Excellent
            elif avg_mark >= 2.5:
                grade = 'ME'  # Good
            elif avg_mark >= 1.5:
                grade = 'AE'  # Average
            else:
                grade = 'BE'  # Below Average

            # Add student result to response
            response_data['student_results'].append({
                'student_id': student_id,
                'average_mark': avg_mark,
                'grade': grade
            })

        return jsonify(response_data)

# Add the route for the API resource
api.add_resource(DistributionAssessmentGrades, '/distribution_assessment_grades/<string:subject_id>/<string:grade_id>/<string:year_id>')

# Add the route for the API resource


#Custom Analytics for Teachers and Administrators:


class TeacherPerformanceInsights(Resource):
    @jwt_required()
    def get(self, subject_id, grade_id):
        school_id = get_school_id_from_session()
        try:
            # Fetch all teachers who taught the subject and grade in any stream
            teachers = db.session.query(Staff).join(TeacherSubjectGradeStream, TeacherSubjectGradeStream.staff_id == Staff.id) \
                                                .filter(TeacherSubjectGradeStream.subject_id == subject_id) \
                                                .filter(TeacherSubjectGradeStream.grade_id == grade_id) \
                                                .filter(Staff.school_id == school_id) \
                                                .all()

            # Prepare teacher performance insights
            insights = []
            for teacher in teachers:
                teacher_performance = self.calculate_teacher_performance(teacher.id, subject_id, grade_id)
                insights.append({
                    'teacher_name': f'{teacher.first_name} {teacher.last_name}',
                    'performance_percentage': teacher_performance
                })

            return make_response(jsonify(insights), 200)

        except Exception as e:
            return make_response(jsonify({'message': str(e)}), 500)

    def calculate_teacher_performance(self, teacher_id, subject_id, grade_id):
        try:
            # Fetch all reports for the subject, grade, and teacher
            reports = Report.query.filter_by(subject_id=subject_id, grade_id=grade_id, staff_id=teacher_id).all()

            total_possible_marks = 0
            total_obtained_marks = 0

            for report in reports:
                total_possible_marks += report.assessment_rubic_id.assessment_rubic_mark
                total_obtained_marks += report.single_mark
           
            if total_possible_marks > 0:
                performance_percentage = (total_obtained_marks / total_possible_marks) * 100
            else:
                performance_percentage = 0

            return performance_percentage

        except Exception as e:
            print(f"Error calculating teacher performance: {str(e)}")
            return 0

# Create routes for the API resources
api.add_resource(TeacherPerformanceInsights, '/teacher_performance_insights/<string:subject_id>/<string:grade_id>')

