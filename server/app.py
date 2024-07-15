#!/usr/bin/env python3
# server/app.py
import os
from flask import Flask,jsonify,make_response,request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api, Resource,reqparse
from sqlalchemy.exc import SQLAlchemyError
from flask_cors import CORS,cross_origin
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from datetime import datetime,timedelta
from flask_jwt_extended import JWTManager
from models import (School,Student, Parent, Department, Staff, Grade, Subject, Strand,
                    SubStrand, LearningOutcome, AssessmentRubic, Designation, Year, Term, FormativeReport,
                    TokenBlocklist,Category,Stream,Parent,db)
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from routes.schools_bp import schools_bp
from routes.parent_bp import parent_bp
from routes.student_bp import student_bp
from routes.grade_bp import grade_bp
from routes.stream_bp import stream_bp
from routes.category_bp import category_bp
from routes.staff_bp import staff_bp
from routes.designation_bp import designation_bp
from routes.subjects_bp import subjects_bp
from routes.subject_details_bp import subject_details_bp
from routes.strand_bp import strand_bp
from routes.substrand_bp import substrand_bp
from routes.learning_outcome_bp import learning_outcome_bp
from routes.assessment_rubic_bp import assessment_rubic_bp
from routes.department_bp import department_bp
from routes.year_bp import year_bp
from routes.term_bp import term_bp
from routes.authentication_bp import authentication_bp
from routes.formative_reports_bp import formative_reports_bp
from routes.change_password_bp import change_password_bp
from routes.analytics_bp import  analytics_bp



#!/usr/bin/env python3
# server/app.py

bcrypt = Bcrypt()


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    migrate = Migrate(app, db)

    db.init_app(app)


    bcrypt.init_app(app)
    load_dotenv()
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)


    cloudinary_url = os.getenv('CLOUDINARY_URL')
    cloudinary_cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
    cloudinary_api_key = os.getenv('CLOUDINARY_API_KEY')
    cloudinary_api_secret = os.getenv('CLOUDINARY_API_SECRET')

    app.config['CLOUDINARY_URL'] = cloudinary_url
    app.config['CLOUDINARY_CLOUD_NAME'] = cloudinary_cloud_name
    app.config['CLOUDINARY_API_KEY'] = cloudinary_api_key
    app.config['CLOUDINARY_API_SECRET'] = cloudinary_api_secret

 
    jwt = JWTManager(app)
    CORS(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
        jti = jwt_payload["jti"]
        token = db.session.query(TokenBlocklist).filter_by(jti=jti).first()
        return token is not None
    
 

    app.register_blueprint(schools_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(stream_bp)
    app.register_blueprint(grade_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(designation_bp)
    app.register_blueprint(subjects_bp)
    app.register_blueprint(parent_bp)
    app.register_blueprint(strand_bp)
    app.register_blueprint(substrand_bp)
    app.register_blueprint(learning_outcome_bp)
    app.register_blueprint(assessment_rubic_bp)
    app.register_blueprint(authentication_bp)
    app.register_blueprint(year_bp)
    app.register_blueprint(term_bp)
    app.register_blueprint(department_bp)
    app.register_blueprint(formative_reports_bp)
    app.register_blueprint(subject_details_bp)
    app.register_blueprint(change_password_bp)
    app.register_blueprint(analytics_bp)




   
   




    return app



app = create_app()


