import itertools,random
from datetime import datetime, date
from app import create_app
from models import (School,Student, Parent, Department, Staff, Grade, Subject, Strand,
                    SubStrand, LearningOutcome, AssessmentRubic, Designation, Year, Term, Report,
                    TokenBlocklist,Category,Stream,TeacherSubjectGradeStream,grade_stream,teacher_grade_stream,db)

app = create_app()


def seed_database():
    with app.app_context():
        School.query.delete()
        Student.query.delete()
        Parent.query.delete()
        Department.query.delete()
        Category.query.delete()
        Staff.query.delete()
        Grade.query.delete()
        Subject.query.delete()
        Strand.query.delete()
        SubStrand.query.delete()
        LearningOutcome.query.delete()
        AssessmentRubic.query.delete()
        Designation.query.delete()
        Year.query.delete()
        Term.query.delete()
        Report.query.delete()
        Stream.query.delete()
        TeacherSubjectGradeStream.query.delete()
        stmt = teacher_grade_stream.delete()
        db.session.execute(stmt)
        db.session.commit()
        stmt1 = grade_stream.delete()
        db.session.execute(stmt1)
        db.session.commit()
       
        db.create_all()

        # Seed data for Categories

        school_data=[
            {"id":"school_id_1","name":"pilot_school","code":"S001","address":"P.O BOX 345 Nairobi","contact":"0745665454","email":"info@pilotschool.com"}

        ]
        schools=[]
        for school_info in school_data:
            school=School(**school_info)
            schools.append(school)
            db.session.add(school)
        db.session.commit()
        
        category_data = [
            {"category_name": "ECD", "school_id": "school_id_1"},
            {"category_name": "Lower Primary", "school_id": "school_id_1"},
            {"category_name": "Upper Primary", "school_id": "school_id_1"},
            {"category_name": "Junior Secondary", "school_id": "school_id_1"},
        ]

        categories = []
        for category_info in category_data:
            category = Category(**category_info)
            categories.append(category)
            db.session.add(category)
        db.session.commit()


                # Seed data for Designations
        designation_data = [
            {"designation_name": "Super-Administrator", "designation_code": 100, "school_id": "school_id_1"},
            {"designation_name": "Administrator", "designation_code": 101, "school_id": "school_id_1"},
            {"designation_name": "Teacher", "designation_code": 102, "school_id": "school_id_1"},
            {"designation_name": "Principal", "designation_code": 103, "school_id": "school_id_1"},
            {"designation_name": "Department Head-Mathematics", "designation_code": 104, "school_id": "school_id_1"},
            {"designation_name": "Department Head-English", "designation_code": 105, "school_id": "school_id_1"},
            {"designation_name": "Department Head-Creatives", "designation_code": 106, "school_id": "school_id_1"},
        ]

        designations = []
        for designation_info in designation_data:
            designation = Designation(**designation_info)
            designations.append(designation)
            db.session.add(designation)
        db.session.commit()

                # Seed data for Staff
        staff_data = [
            {"payroll_number": "PR001", "first_name": "Alice", "last_name": "Wanjiku", "date_of_birth": date(1985, 4, 12),
            "phone_number": "1234567890", "alternative_contact": "0987654321", "email_address": "alice.wanjiku@example.com","status":"yes",
            "password": "hashed_password_1", "designation_id": designations[0].id, "school_id": "school_id_1"},
            {"payroll_number": "PR002", "first_name": "Mark", "last_name": "Mbithi", "date_of_birth": date(1979, 9, 25),
            "phone_number": "2345678901", "alternative_contact": "1987654321", "email_address": "mark.mbithi@yahoo.com",
            "password": "hashed_password_2", "designation_id": designations[1].id, "school_id": "school_id_1","status":"yes"},
            {"payroll_number": "PR003", "first_name": "Jane", "last_name": "Mbote", "date_of_birth": date(1987, 7, 20),
            "phone_number": "2547823940", "alternative_contact": "", "email_address": "jane.mbote@gmail.com",
            "password": "hashed_password_3", "designation_id": designations[2].id, "school_id": "school_id_1","status":"yes"},
            {"payroll_number": "PR004", "first_name": "Martin", "last_name": "Otieno", "date_of_birth": date(1989, 1, 27),
            "phone_number": "2543789001", "alternative_contact": "", "email_address": "martin.otieno@example.com",
            "password": "hashed_password_4", "designation_id": designations[0].id, "school_id": "school_id_1","status":"yes"},
            {"payroll_number": "PR005", "first_name": "Rose", "last_name": "Ndegwa", "date_of_birth": date(1967, 3, 1),
            "phone_number": "2545667891", "alternative_contact": "", "email_address": "rose.ndegwa@example.com",
            "password": "hashed_password_4", "designation_id": designations[3].id, "school_id": "school_id_1","status":"yes"},
        ]

        staffs = []
        for staff_info in staff_data:
            staff = Staff(**staff_info)
            staffs.append(staff)
            db.session.add(staff)
        db.session.commit()


                # Seed data for Grades
        grade_data = [
            {"grade": "Grade 1", "class_teacher_id": staffs[0].id, "category_id": categories[0].id, "school_id": "school_id_1"},
            {"grade": "Grade 2", "class_teacher_id": staffs[2].id, "category_id": categories[1].id, "school_id": "school_id_1"},
            {"grade": "Grade 3", "class_teacher_id": staffs[1].id, "category_id": categories[0].id, "school_id": "school_id_1"}
        ]

        grades = []
        for grade_info in grade_data:
            grade = Grade(**grade_info)
            grades.append(grade)
            db.session.add(grade)
        db.session.commit()


                # Seed data for Streams
        stream_data = [
            {"stream_name": "A", "school_id": "school_id_1"},  # Replace school_id_1 with the actual school ID
            {"stream_name": "B", "school_id": "school_id_1"}   # Replace school_id_2 with the actual school ID
        ]

        streams = []
        for stream_info in stream_data:
            stream = Stream(**stream_info)
            streams.append(stream)
            db.session.add(stream)
        db.session.commit()

        # Seed data for Students
        student_data = [
            {"admission_number": "ADM001", "joined_date": date(2020, 1, 15), "first_name": "Charles", "last_name": "Mbooni",
            "date_of_birth": date(2010, 5, 10), "birth_certificate_number": "BCN001", "photo_url": "photo1.jpg",
            "grade_id": grades[1].id, "stream_id": streams[0].id, "school_id": "school_id_1","status":"yes"},
            {"admission_number": "ADM002", "joined_date": date(2021, 2, 20), "first_name": "Diana", "last_name": "Mwite",
            "date_of_birth": date(2011, 7, 14), "birth_certificate_number": "BCN002", "photo_url": "photo2.jpg",
            "grade_id": grades[1].id, "stream_id": streams[1].id, "school_id": "school_id_1","status":"yes"}
        ]

        students = []
        for student_info in student_data:
            student = Student(**student_info)
            students.append(student)
            db.session.add(student)
        db.session.commit()


                # Seed data for Parents
        parent_data = [
            {"mothers_first_name": "Eve", "mothers_last_name": "Mbooni", "mothers_contact": "3456789012",
            "mothers_email": "eve.brown@example.com",
            "fathers_first_name": "Frank", "fathers_last_name": "Mbooni", "fathers_contact": "4456789012",
            "fathers_email": "frank.brown@example.com",
            "guardian_first_name": "", "guardian_last_name": "", "guardian_contact": "5456789012",
            "guardian_email": "grace.brown@example.com",
            "student_id": students[0].id, "school_id": "school_id_1","status":"yes"},
            {"mothers_first_name": "", "mothers_last_name": "", "mothers_contact": "6456789012",
            "mothers_email": "hannah.miller@example.com",
            "fathers_first_name": "", "fathers_last_name": "", "fathers_contact": "7456789012",
            "fathers_email": "ian.miller@example.com",
            "guardian_first_name": "Jenny", "guardian_last_name": "Mwite", "guardian_contact": "8456789012",
            "guardian_email": "jenny.miller@example.com",
            "student_id": students[1].id, "school_id": "school_id_1","status":"yes"},
        ]

        for parent_info in parent_data:
            parent = Parent(**parent_info)
            db.session.add(parent)
        db.session.commit()


        # Seed data for Subjects
        subject_data = [
            {"subject_name": "ENGLISH LANGUAGE ACTIVITIES", "school_id": "school_id_1"},
            {"subject_name": "INDIGENOUS LANGUAGES ACTIVITIES", "school_id": "school_id_1"},
            {"subject_name": "KISWAHILI LANGUAGE ACTIVITIES", "school_id": "school_id_1"},
            {"subject_name": "MATHEMATICS ACTIVITES", "school_id": "school_id_1"},
            {"subject_name": "ENVIRONMENTAL ACTIVITES", "school_id": "school_id_1"},
            {"subject_name": "CHRISTIAN RELIGIOUS EDUCATION ACTIVITIES", "school_id": "school_id_1"},
            {"subject_name": "CREATIVE ARTS ACTIVITIES", "school_id": "school_id_1"},
        ]

        subjects = []
        for subject_info in subject_data:
            subject = Subject(**subject_info)
            subjects.append(subject)
            db.session.add(subject)
        db.session.commit()

                # Seed data for Strands
        strand_data = [
        {"strand_name": "LISTENING AND SPEAKING", "subject_id": subjects[0].id, "grade_id": grades[1].id},
        {"strand_name": "READING", "subject_id": subjects[0].id, "grade_id": grades[1].id},
        {"strand_name": "THINGS FOUND AT SCHOOL", "subject_id": subjects[1].id, "grade_id": grades[1].id},
        {"strand_name": "ACTIVITIES AT SCHOOL", "subject_id": subjects[1].id, "grade_id": grades[1].id},
        {"strand_name": "KUSIKILIZA NA KUZUNGUMZA", "subject_id": subjects[2].id, "grade_id": grades[1].id},
        {"strand_name": "KUSOMA", "subject_id": subjects[2].id, "grade_id": grades[1].id},
        {"strand_name": "NUMBERS", "subject_id": subjects[3].id, "grade_id": grades[1].id},
        {"strand_name": "MEASUREMENT", "subject_id": subjects[3].id, "grade_id": grades[1].id},
        {"strand_name": "SOCIAL ENVIRONMENT", "subject_id": subjects[4].id, "grade_id": grades[1].id},
        {"strand_name": "NATURAL ENVIRONMENT", "subject_id": subjects[4].id, "grade_id": grades[1].id},
        {"strand_name": "CREATION", "subject_id": subjects[5].id, "grade_id": grades[1].id},
        {"strand_name": "THE HOLY BIBLE", "subject_id": subjects[5].id, "grade_id": grades[1].id},
        {"strand_name": "CREATING AND EXPLORATION", "subject_id": subjects[6].id, "grade_id": grades[1].id},
        {"strand_name": "PERFORMANCE AND DISPLAY", "subject_id": subjects[6].id, "grade_id": grades[1].id},                
    ]


        strands = []
        for strand_info in strand_data:
            strand = Strand(**strand_info)
            strands.append(strand)
            db.session.add(strand)
        db.session.commit()


                # Seed data for SubStrands
        substrand_data = [
        {"substrand_name": "Pronunciation and Vocabulary", "strand_id": strands[0].id, "subject_id": subjects[0].id, "grade_id": grades[1].id},
        {"substrand_name": "Fluency", "strand_id": strands[1].id, "subject_id": subjects[0].id, "grade_id": grades[1].id},
        {"substrand_name": "LISTENING Listening to Instructions", "strand_id": strands[2].id, "subject_id": subjects[1].id, "grade_id": grades[1].id},
        {"substrand_name": "LISTENING Simple instructions", "strand_id": strands[3].id, "subject_id": subjects[1].id, "grade_id": grades[1].id},
        {"substrand_name": "Kusikiliza na Kuzungumza", "strand_id": strands[4].id, "subject_id": subjects[2].id, "grade_id": grades[1].id},
        {"substrand_name": "Kusoma Ufahamu", "strand_id": strands[5].id, "subject_id": subjects[2].id, "grade_id": grades[1].id},
        {"substrand_name": "Number Concept", "strand_id": strands[6].id, "subject_id": subjects[3].id, "grade_id": grades[1].id},
        {"substrand_name": "Length", "strand_id": strands[7].id, "subject_id": subjects[3].id, "grade_id": grades[1].id},
        {"substrand_name": "OUR HOME", "strand_id": strands[8].id, "subject_id": subjects[4].id, "grade_id": grades[1].id},
        {"substrand_name": "WEATHER", "strand_id": strands[9].id, "subject_id": subjects[4].id, "grade_id": grades[1].id},
        {"substrand_name": "Self-Awareness", "strand_id": strands[10].id, "subject_id": subjects[5].id, "grade_id": grades[1].id},
        {"substrand_name": "The Holy Bible as a guide in daily lives", "strand_id": strands[11].id, "subject_id": subjects[5].id, "grade_id": grades[1].id},
        {"substrand_name": "Creating and Exploration", "strand_id": strands[12].id, "subject_id": subjects[6].id, "grade_id": grades[1].id},
        {"substrand_name": "Performance and Display", "strand_id": strands[13].id, "subject_id": subjects[6].id, "grade_id": grades[1].id}, 
    ]


        substrands = []
        for substrand_info in substrand_data:
            substrand = SubStrand(**substrand_info)
            substrands.append(substrand)
            db.session.add(substrand)
        db.session.commit()

                # Seed data for LearningOutcomes
        learning_outcome_data = [
    {"learning_outcomes": "Distinguish words with the target sound in conversations.", "grade_id": grades[1].id, "subject_id": subjects[0].id,
    "strand_id": strands[0].id, "sub_strand_id": substrands[0].id},
    {"learning_outcomes": "Recognize the target blend during reading.", "grade_id": grades[1].id, "subject_id": subjects[0].id,
    "strand_id": strands[1].id, "sub_strand_id": substrands[1].id},
    {"learning_outcomes": "Respond to simple sequenced instructions related to items found in school.", "grade_id": grades[1].id, "subject_id": subjects[1].id,
    "strand_id": strands[2].id, "sub_strand_id": substrands[2].id},
    {"learning_outcomes": "Respond to simple instructions related to school activities.", "grade_id": grades[1].id, "subject_id": subjects[1].id,
    "strand_id": strands[3].id, "sub_strand_id": substrands[3].id},

    {"learning_outcomes": "Kutambua maamkuzi na maagano ya nyakati za siku.", "grade_id": grades[1].id, "subject_id": subjects[2].id,
    "strand_id": strands[4].id, "sub_strand_id": substrands[4].id},
    {"learning_outcomes": "Kutambua msamiati kuhusu suala lengwa katika kifungu chepesi cha ufahamu.", "grade_id": grades[1].id, "subject_id": subjects[2].id,
    "strand_id": strands[5].id, "sub_strand_id": substrands[5].id},
    {"learning_outcomes": "Read numbers 1-100 in symbols, Represent numbers 1-100 using concrete objects in the environment.", "grade_id": grades[1].id, "subject_id": subjects[3].id,
    "strand_id": strands[6].id, "sub_strand_id": substrands[6].id},
    {"learning_outcomes": "Measure length using fixed units, Identify the metre as a unit of measuring length, Measure length in metres.", "grade_id": grades[1].id, "subject_id": subjects[3].id,
    "strand_id": strands[7].id, "sub_strand_id": substrands[7].id},
    {"learning_outcomes": "Differentiate between personal and common items used at home.", "grade_id": grades[1].id, "subject_id": subjects[4].id,
    "strand_id": strands[8].id, "sub_strand_id": substrands[8].id},
    {"learning_outcomes": "Identify weather conditions at different times of the day.", "grade_id": grades[1].id, "subject_id": subjects[4].id,
    "strand_id": strands[9].id, "sub_strand_id": substrands[9].id},
    {"learning_outcomes": "State what they like about themselves as God’s creation, Appreciate their physical appearance as uniquely created by God, State different chores they do at home as service to God", "grade_id": grades[1].id, "subject_id": subjects[5].id,
    "strand_id": strands[10].id, "sub_strand_id": substrands[10].id},
    {"learning_outcomes": "Identify reasons for reading the Bible to strengthen their faith in God, State how often they read the Bible as a family to seek God’s guidance", "grade_id": grades[1].id, "subject_id": subjects[5].id,
    "strand_id": strands[11].id, "sub_strand_id": substrands[11].id},
    {"learning_outcomes": "Identify basic shapes, sing action songs, make body movement formations, model and draw basic shapes.", "grade_id": grades[1].id, "subject_id": subjects[6].id,
    "strand_id": strands[12].id, "sub_strand_id": substrands[12].id},
    {"learning_outcomes": "Identify different directions of turning, make simple costumes, perform turning in different directions, and sing songs while making patterns using turning.", "grade_id": grades[1].id, "subject_id": subjects[6].id,
    "strand_id": strands[13].id, "sub_strand_id": substrands[13].id},

]


        learning_outcomes = []
        for learning_outcome_info in learning_outcome_data:
            learning_outcome = LearningOutcome(**learning_outcome_info)
            learning_outcomes.append(learning_outcome)
            db.session.add(learning_outcome)
        db.session.commit()


        # Seed data for AssessmentRubics
        assessment_rubic_data = [
        {"assessment_rubics": "E.E: Distinguishes all words with the target sound in conversations effortlessly.", "assessment_rubic_mark": 4, "grade_id": grades[1].id, "subject_id": subjects[0].id,
        "strand_id": strands[0].id, "sub_strand_id": substrands[0].id, "learning_outcome_id": learning_outcomes[0].id},
        {"assessment_rubics": "M.E: Distinguishes words with the target sound in conversations effortlessly", "assessment_rubic_mark": 3, "grade_id": grades[1].id, "subject_id": subjects[0].id,
        "strand_id": strands[0].id, "sub_strand_id": substrands[0].id, "learning_outcome_id": learning_outcomes[0].id},
        {"assessment_rubics": "A.E: Distinguishes some words with the target sound in conversations effortlessly", "assessment_rubic_mark": 2, "grade_id": grades[1].id, "subject_id": subjects[0].id,
        "strand_id": strands[0].id, "sub_strand_id": substrands[0].id, "learning_outcome_id": learning_outcomes[0].id},
        {"assessment_rubics": "B.E: Distinguishes some words with the target sound in conversations with some help.", "assessment_rubic_mark": 1, "grade_id": grades[1].id, "subject_id": subjects[0].id,
        "strand_id": strands[0].id, "sub_strand_id": substrands[0].id, "learning_outcome_id": learning_outcomes[0].id},
        {"assessment_rubics": "E.E: Recognizes the target blend and its sound for ease of reading easily.", "assessment_rubic_mark": 4, "grade_id": grades[1].id, "subject_id": subjects[0].id,
        "strand_id": strands[1].id, "sub_strand_id": substrands[1].id, "learning_outcome_id": learning_outcomes[1].id},
        {"assessment_rubics": "M.E: Recognises the target blend and its sound for ease of reading.", "assessment_rubic_mark": 3, "grade_id": grades[1].id, "subject_id": subjects[0].id,
        "strand_id": strands[1].id, "sub_strand_id": substrands[1].id, "learning_outcome_id": learning_outcomes[1].id},
        {"assessment_rubics": "A.E: Recognises the target blend and its sound occasionally for ease of reading.", "assessment_rubic_mark": 2, "grade_id": grades[1].id, "subject_id": subjects[0].id,
        "strand_id": strands[1].id, "sub_strand_id": substrands[1].id, "learning_outcome_id": learning_outcomes[1].id},
        {"assessment_rubics": "B.E: Recognises the target blend and its sound for ease of reading with assistance.", "assessment_rubic_mark": 1, "grade_id": grades[1].id, "subject_id": subjects[0].id,
        "strand_id": strands[1].id, "sub_strand_id": substrands[1].id, "learning_outcome_id": learning_outcomes[1].id},


        {"assessment_rubics": "E.E: Perfectly responds to simple sequenced instructions related to items found in school.", "assessment_rubic_mark": 4, "grade_id": grades[1].id, "subject_id": subjects[1].id,
        "strand_id": strands[2].id, "sub_strand_id": substrands[2].id, "learning_outcome_id": learning_outcomes[2].id},
        {"assessment_rubics": "M.E: Responds to simple sequenced instructions related to items found in school.", "assessment_rubic_mark": 3, "grade_id": grades[1].id, "subject_id": subjects[1].id,
        "strand_id": strands[2].id, "sub_strand_id": substrands[2].id, "learning_outcome_id": learning_outcomes[2].id},
        {"assessment_rubics": "A.E: Responds to some simple sequenced instructions related to items found in school.", "assessment_rubic_mark": 2, "grade_id": grades[1].id, "subject_id": subjects[1].id,
        "strand_id": strands[2].id, "sub_strand_id": substrands[2].id, "learning_outcome_id": learning_outcomes[2].id},
        {"assessment_rubics": "B.E: Responds with difficulties to some simple sequenced instructions related to items found in school.", "assessment_rubic_mark": 1, "grade_id": grades[1].id, "subject_id": subjects[1].id,
        "strand_id": strands[2].id, "sub_strand_id": substrands[2].id, "learning_outcome_id": learning_outcomes[2].id},


        {"assessment_rubics": "E.E: Effectively responds to simple instructions related to school activities.", "assessment_rubic_mark": 4, "grade_id": grades[1].id, "subject_id": subjects[1].id,
        "strand_id": strands[3].id, "sub_strand_id": substrands[3].id, "learning_outcome_id": learning_outcomes[3].id},
        {"assessment_rubics": "M.E: Responds to simple instructions related to school activities.", "assessment_rubic_mark": 3, "grade_id": grades[1].id, "subject_id": subjects[1].id,
        "strand_id": strands[3].id, "sub_strand_id": substrands[3].id, "learning_outcome_id": learning_outcomes[3].id},
        {"assessment_rubics": "A.E: Responds to some simple instructions related to school activities.", "assessment_rubic_mark": 2, "grade_id": grades[1].id, "subject_id": subjects[1].id,
        "strand_id": strands[3].id, "sub_strand_id": substrands[3].id, "learning_outcome_id": learning_outcomes[3].id},
        {"assessment_rubics": "B.E: Responds with difficulties to simple instructions related to school activities.", "assessment_rubic_mark": 1, "grade_id": grades[1].id, "subject_id": subjects[1].id,
        "strand_id": strands[3].id, "sub_strand_id": substrands[3].id, "learning_outcome_id": learning_outcomes[3].id},

        {"assessment_rubics": "KZM: Anatambua maamkuzi na maagano ya nyakati za siku kwa wepesi", "assessment_rubic_mark": 4, "grade_id": grades[1].id, "subject_id": subjects[2].id, "strand_id": strands[4].id, "sub_strand_id": substrands[4].id, "learning_outcome_id": learning_outcomes[4].id},
        {"assessment_rubics": "KFM: Anatambua maamkuzi na maagano ya nyakati za siku", "assessment_rubic_mark": 3, "grade_id": grades[1].id, "subject_id": subjects[2].id, "strand_id": strands[4].id, "sub_strand_id": substrands[4].id, "learning_outcome_id": learning_outcomes[4].id},
        {"assessment_rubics": "KKM: Anatambua baadhi ya maamkuzi na maagano ya nyakati za siku.", "assessment_rubic_mark": 2, "grade_id": grades[1].id, "subject_id": subjects[2].id, "strand_id": strands[4].id, "sub_strand_id": substrands[4].id, "learning_outcome_id": learning_outcomes[4].id},
        {"assessment_rubics": "MM: Anatambua maamkuzi na maagano ya nyakati za siku kwa kusaidiwa", "assessment_rubic_mark": 1, "grade_id": grades[1].id, "subject_id": subjects[2].id, "strand_id": strands[5].id, "sub_strand_id": substrands[5].id, "learning_outcome_id": learning_outcomes[4].id},
        {"assessment_rubics": "KZM: Anatambua msamiati kuhusu suala lengwa katika kifungu chepesi cha ufahamu kwa urahisi", "assessment_rubic_mark": 4, "grade_id": grades[1].id, "subject_id": subjects[2].id, "strand_id": strands[5].id, "sub_strand_id": substrands[5].id, "learning_outcome_id": learning_outcomes[5].id},
        {"assessment_rubics": "KFM: Anatambua msamiati kuhusu suala lengwa katika kifungu chepesi cha ufahamu", "assessment_rubic_mark": 3, "grade_id": grades[1].id, "subject_id": subjects[2].id, "strand_id": strands[5].id, "sub_strand_id": substrands[5].id, "learning_outcome_id": learning_outcomes[5].id},
        {"assessment_rubics": "KKM: Anatambua baadhi ya msamiati kuhusu suala lengwa katika kifungu chepesi cha ufahamu", "assessment_rubic_mark": 2, "grade_id": grades[1].id, "subject_id": subjects[2].id, "strand_id": strands[5].id, "sub_strand_id": substrands[5].id, "learning_outcome_id": learning_outcomes[5].id},
        {"assessment_rubics": "MM: Anatambua msamiati kuhusu suala lengwa katika kifungu chepesi cha ufahamu kwa kusaidiwa.", "assessment_rubic_mark": 1, "grade_id": grades[1].id, "subject_id": subjects[2].id, "strand_id": strands[5].id, "sub_strand_id": substrands[5].id, "learning_outcome_id": learning_outcomes[5].id},
        {"assessment_rubics": "E E: Correctly: reads numbers more than 100 in symbols, represents numbers more than 100 using concrete objects.", "assessment_rubic_mark": 4, "grade_id": grades[1].id, "subject_id": subjects[3].id, "strand_id": strands[6].id, "sub_strand_id": substrands[6].id, "learning_outcome_id": learning_outcomes[6].id},
        {"assessment_rubics": "M E: Correctly: reads numbers 1-100 in symbols, represents numbers 1-100 using concrete objects. ", "assessment_rubic_mark": 3, "grade_id": grades[1].id, "subject_id": subjects[3].id, "strand_id": strands[6].id, "sub_strand_id": substrands[6].id, "learning_outcome_id": learning_outcomes[6].id},
        {"assessment_rubics": "A E: Inconsistently: reads numbers 1-100 in symbols, represents numbers 1-100 using concrete objects.", "assessment_rubic_mark": 2, "grade_id": grades[1].id, "subject_id": subjects[3].id, "strand_id": strands[6].id, "sub_strand_id": substrands[6].id, "learning_outcome_id": learning_outcomes[6].id},
        {"assessment_rubics": "B E: Major inaccuracies in: reading numbers 1-100 in symbols, representing numbers 1-100 using concrete objects.", "assessment_rubic_mark": 1, "grade_id": grades[1].id, "subject_id": subjects[3].id, "strand_id": strands[6].id, "sub_strand_id": substrands[6].id, "learning_outcome_id": learning_outcomes[6].id},
        {"assessment_rubics": "E E: Correctly: measures length using fixed units, identifies the metre as a unit of measuring length and measures length in metres with ease.", "assessment_rubic_mark": 4, "grade_id": grades[1].id, "subject_id": subjects[3].id, "strand_id": strands[7].id, "sub_strand_id": substrands[7].id, "learning_outcome_id": learning_outcomes[7].id},
        {"assessment_rubics": "M E: Correctly: measures length using fixed units, identifies the metre as a unit of measuring length and measures length in metres.", "assessment_rubic_mark": 3, "grade_id": grades[1].id, "subject_id": subjects[3].id, "strand_id": strands[7].id, "sub_strand_id": substrands[7].id, "learning_outcome_id": learning_outcomes[7].id},
        {"assessment_rubics": "A E: Inconsistently: measures length using fixed units, identifies the metre as a unit of measuring length and measures length in metres.", "assessment_rubic_mark": 2, "grade_id": grades[1].id, "subject_id": subjects[3].id, "strand_id": strands[7].id, "sub_strand_id": substrands[7].id, "learning_outcome_id": learning_outcomes[7].id},
        {"assessment_rubics": "B E: Major inaccuracies in: measuring length using fixed units, identifying the metre as a unit of measuring length and measuring length in metres.", "assessment_rubic_mark": 1, "grade_id": grades[1].id, "subject_id": subjects[3].id, "strand_id": strands[7].id, "sub_strand_id": substrands[7].id, "learning_outcome_id": learning_outcomes[7].id},
        {"assessment_rubics": "E E: Differentiates between personal and common items used at home with ease.", "assessment_rubic_mark": 4, "grade_id": grades[1].id, "subject_id": subjects[4].id, "strand_id": strands[8].id, "sub_strand_id": substrands[8].id, "learning_outcome_id": learning_outcomes[8].id},
        {"assessment_rubics": "M E: Differentiates between personal and common items used at home with ease.", "assessment_rubic_mark": 3, "grade_id": grades[1].id, "subject_id": subjects[4].id, "strand_id": strands[8].id, "sub_strand_id": substrands[8].id, "learning_outcome_id": learning_outcomes[8].id},
        {"assessment_rubics": "A E: Is able to differentiate between personal and common items used at home with assistance.", "assessment_rubic_mark": 2, "grade_id": grades[1].id, "subject_id": subjects[4].id, "strand_id": strands[8].id, "sub_strand_id": substrands[8].id, "learning_outcome_id": learning_outcomes[8].id},
        {"assessment_rubics": "B E: Has difficulties differentiating between personal and common items used at home.", "assessment_rubic_mark": 1, "grade_id": grades[1].id, "subject_id": subjects[4].id, "strand_id": strands[8].id, "sub_strand_id": substrands[8].id, "learning_outcome_id": learning_outcomes[8].id},
    
        {"assessment_rubics": "E E: Precisely identifies weather conditions at different times of the day.", "assessment_rubic_mark": 4, "grade_id": grades[1].id, "subject_id": subjects[4].id,"strand_id": strands[9].id, "sub_strand_id": substrands[9].id, "learning_outcome_id": learning_outcomes[9].id},
        {"assessment_rubics": "M E: Identifies weather conditions at different times of the day.", "assessment_rubic_mark": 3, "grade_id": grades[1].id, "subject_id": subjects[4].id,"strand_id": strands[9].id, "sub_strand_id": substrands[9].id, "learning_outcome_id": learning_outcomes[9].id},
        {"assessment_rubics": "A E: Identifies weather conditions at different times of the day with assistance.", "assessment_rubic_mark": 2, "grade_id": grades[1].id, "subject_id": subjects[4].id,"strand_id": strands[9].id, "sub_strand_id": substrands[9].id, "learning_outcome_id": learning_outcomes[9].id},
        {"assessment_rubics": "B E: inconsistently identifies weather conditions at different times of the day.", "assessment_rubic_mark": 1, "grade_id": grades[1].id, "subject_id": subjects[4].id,"strand_id": strands[9].id, "sub_strand_id": substrands[9].id, "learning_outcome_id": learning_outcomes[9].id},

        {"assessment_rubics": "E E: Correctly and consistently appreciates self and others and participates in different chores.", "assessment_rubic_mark": 4, "grade_id": grades[1].id, "subject_id": subjects[5].id,"strand_id": strands[10].id, "sub_strand_id": substrands[10].id, "learning_outcome_id": learning_outcomes[10].id},
        {"assessment_rubics": "M E: Correctly appreciates self and others and participates in different chores.", "assessment_rubic_mark": 3, "grade_id": grades[1].id, "subject_id": subjects[5].id,"strand_id": strands[10].id, "sub_strand_id": substrands[10].id, "learning_outcome_id": learning_outcomes[10].id},
        {"assessment_rubics": "A E: Occasionally respects self and others and sometimes participates in different chores.", "assessment_rubic_mark": 2, "grade_id": grades[1].id, "subject_id": subjects[5].id,"strand_id": strands[10].id, "sub_strand_id": substrands[10].id, "learning_outcome_id": learning_outcomes[10].id},
        {"assessment_rubics": "B E: Hardly respects self or others.", "assessment_rubic_mark": 1, "grade_id": grades[1].id, "subject_id": subjects[5].id,"strand_id": strands[10].id, "sub_strand_id": substrands[10].id, "learning_outcome_id": learning_outcomes[10].id}, 
        {"assessment_rubics": "E E: Effectively and regularly reads the Bible.", "assessment_rubic_mark": 4, "grade_id": grades[1].id, "subject_id": subjects[5].id,"strand_id": strands[11].id, "sub_strand_id": substrands[11].id, "learning_outcome_id": learning_outcomes[11].id},
        {"assessment_rubics": "M E: Regularly reads the Bible", "assessment_rubic_mark": 3, "grade_id": grades[1].id, "subject_id": subjects[5].id,"strand_id": strands[11].id, "sub_strand_id": substrands[11].id, "learning_outcome_id": learning_outcomes[11].id},
        {"assessment_rubics": "A E: Once in a while reads the Bible.", "assessment_rubic_mark": 2, "grade_id": grades[1].id, "subject_id": subjects[5].id,"strand_id": strands[11].id, "sub_strand_id": substrands[11].id, "learning_outcome_id": learning_outcomes[11].id},
        {"assessment_rubics": "B E: Hardly reads the Bible.", "assessment_rubic_mark": 1, "grade_id": grades[1].id, "subject_id": subjects[5].id,"strand_id": strands[11].id, "sub_strand_id": substrands[11].id, "learning_outcome_id": learning_outcomes[11].id},

        {"assessment_rubics": "E E: Identifies all basic shapes, expressively sings action songs, creatively makes body movement formations, models and draws basic shapes.", "assessment_rubic_mark": 4, "grade_id": grades[1].id, "subject_id": subjects[6].id,"strand_id": strands[12].id, "sub_strand_id": substrands[12].id, "learning_outcome_id": learning_outcomes[12].id},
        {"assessment_rubics": "M E: Identifies all basic shapes, sings action songs, makes body movement formations, models and draws basic shapes.", "assessment_rubic_mark": 3, "grade_id": grades[1].id, "subject_id": subjects[6].id,"strand_id": strands[12].id, "sub_strand_id": substrands[12].id, "learning_outcome_id": learning_outcomes[12].id},
        {"assessment_rubics": "A E: Identifies a few basic shapes, sings action songs, makes body movement formations, models and draws basic shapes.", "assessment_rubic_mark": 2, "grade_id": grades[1].id, "subject_id": subjects[6].id,"strand_id": strands[12].id, "sub_strand_id": substrands[12].id, "learning_outcome_id": learning_outcomes[12].id},
        {"assessment_rubics": "B E: Identifies basic shapes only with assistance, sings action songs only given cues, makes body movement formations, models and draws basic shapes.", "assessment_rubic_mark": 1, "grade_id": grades[1].id, "subject_id": subjects[6].id,"strand_id": strands[12].id, "sub_strand_id": substrands[12].id, "learning_outcome_id": learning_outcomes[12].id},

        {"assessment_rubics": "E E: Identifies a variety of directions of turning, make simple costumes with a good finish, perform turning in different directions, and expressively sing songs while making patterns using turning.", "assessment_rubic_mark": 1, "grade_id": grades[1].id, "subject_id": subjects[6].id,"strand_id": strands[13].id, "sub_strand_id": substrands[13].id, "learning_outcome_id": learning_outcomes[13].id},
        {"assessment_rubics": "M E: Identities different directions of turning, make simple costumes, perform turning in different directions, and sing songs while making patterns using turning.", "assessment_rubic_mark": 1, "grade_id": grades[1].id, "subject_id": subjects[6].id,"strand_id": strands[13].id, "sub_strand_id": substrands[13].id, "learning_outcome_id": learning_outcomes[13].id},
        {"assessment_rubics": "A E: Identifies some directions of turning, make simple costumes, perform turning in different directions, and sing songs while making patterns using turning with few challenges.", "assessment_rubic_mark": 1, "grade_id": grades[1].id, "subject_id": subjects[6].id,"strand_id": strands[13].id, "sub_strand_id": substrands[13].id, "learning_outcome_id": learning_outcomes[13].id},
        {"assessment_rubics": "B E: Identifies very few directions of turning, make simple costumes, perform turning in different directions, and sing songs while making patterns using turning with many challenges.", "assessment_rubic_mark": 1, "grade_id": grades[1].id, "subject_id": subjects[6].id, "strand_id": strands[13].id, "sub_strand_id": substrands[13].id, "learning_outcome_id": learning_outcomes[13].id}]
        
        assessment_rubics = []
        for assessment_rubic_info in assessment_rubic_data:
            assessment_rubic = AssessmentRubic(**assessment_rubic_info)
            assessment_rubics.append(assessment_rubic)
            db.session.add(assessment_rubic)
        db.session.commit()

        # Seed data for Departments
        department_data = [
            {"department_name": "Mathematics", "department_head": "Alice Wanjiku", "dept_staff": staffs[0].id,"school_id": "school_id_1"},
            {"department_name": "English", "department_head": "Mark Mbithi", "dept_staff": staffs[1].id,"school_id": "school_id_1"},
        ]
        departments = []
        for department_info in department_data:
            department = Department(**department_info)
            departments.append(department)
            db.session.add(department)
        db.session.commit()

        # Seed data for Years
        year_data = [
            {"year_name": 2023},
            {"year_name": 2024},
        ]
        years = []
        for year_info in year_data:
            year = Year(**year_info)
            years.append(year)
            db.session.add(year)
        db.session.commit()

        # Seed data for Terms
        term_data = [
            {"term_name": "Term 1"},
            {"term_name": "Term 2"},
            {"term_name": "Term 3"},
        ]
        terms = []
        for term_info in term_data:
            term = Term(**term_info)
            terms.append(term)
            db.session.add(term)
        db.session.commit()

        db.session.execute(grade_stream.insert().values([
        {'grade_id': grades[0].id, 'stream_id': streams[0].id},
        {'grade_id': grades[1].id, 'stream_id': streams[0].id},
        {'grade_id': grades[1].id, 'stream_id': streams[1].id},
        # Add more entries as needed
    ]))
        db.session.commit()
            #

        # Seed teacher_grade_stream table
        db.session.execute(teacher_grade_stream.insert().values([
            {'staff_id': staffs[0].id, 'grade_id': grades[0].id, 'stream_id': streams[0].id},
            {'staff_id': staffs[1].id, 'grade_id': grades[1].id, 'stream_id': streams[0].id},
            {'staff_id': staffs[2].id, 'grade_id': grades[1].id, 'stream_id': streams[1].id},
            # Add more entries as needed
        ]))
        db.session.commit()
            #

        # Seed TeacherSubjectGradeStream table (if applicable)
        db.session.add(TeacherSubjectGradeStream(
            staff_id=staffs[0].id,
            subject_id=subjects[0].id,
            grade_id=grades[0].id,
            stream_id=streams[0].id
        ))

        # Commit the changes
        db.session.commit()
            #

        # Assuming you have already created and populated other tables like Staff, Year, Term, Grade, Student, Subject, Strand, SubStrand, LearningOutcome, AssessmentRubric

        # Fetch existing entries for foreign key references
        staffs = db.session.query(Staff).all()
        years = db.session.query(Year).all()
        terms = db.session.query(Term).all()
        grades = db.session.query(Grade).all()
        students = db.session.query(Student).all()
        subjects = db.session.query(Subject).all()
        strands = db.session.query(Strand).all()
        substrands = db.session.query(SubStrand).all()
        learning_outcomes = db.session.query(LearningOutcome).all()
        assessment_rubics = db.session.query(AssessmentRubic).all()

        # Generate all possible combinations
        combinations = list(itertools.product(
            range(6),  # subjects index from 0 to 5
            range(14)  # learning outcomes index from 0 to 13
        ))

        # Define possible grades
        grades_info = [
            {"grade_ee": True, "grade_me": False, "grade_ae": False, "grade_be": False, "single_mark": 4},
            {"grade_ee": False, "grade_me": True, "grade_ae": False, "grade_be": False, "single_mark": 3},
            {"grade_ee": False, "grade_me": False, "grade_ae": True, "grade_be": False, "single_mark": 2},
            {"grade_ee": False, "grade_me": False, "grade_ae": False, "grade_be": True, "single_mark": 1}
        ]

        # Seed data for reports
        reports_data = []
        for combo in combinations:
            subject_idx,assessment_rubic_idx = combo
            grade_info = random.choice(grades_info)  # Randomly select a grade
            report_info = {
                "staff_id": staffs[0].id,
                "year_id": years[0].id,
                "grade_id": grades[1].id,
                "stream_id":streams[0].id,
                "student_id": students[0].id,                
                "subject_id": subjects[subject_idx].id,
                "assessment_rubic_id":assessment_rubics[assessment_rubic_idx].id,
                "single_mark": grade_info["single_mark"],
                "grade_ee": grade_info["grade_ee"],
                "grade_me": grade_info["grade_me"],
                "grade_ae": grade_info["grade_ae"],
                "grade_be": grade_info["grade_be"],
                "school_id": "school_id_1"
            }
            reports_data.append(report_info)

        # Add and commit the data
        for report_info in reports_data:
            report = Report(**report_info)
            db.session.add(report)

        db.session.commit()



       


if __name__ == "__main__":
    seed_database()