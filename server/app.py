#!/usr/bin/env python3
# server/app.py

from flask import Flask,jsonify,make_response,request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api, Resource,reqparse
from sqlalchemy.exc import SQLAlchemyError
from flask_cors import CORS,cross_origin
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from datetime import datetime
from models import db

#!/usr/bin/env python3
# server/app.py



def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    migrate = Migrate(app, db)

    db.init_app(app)
    return app



app = create_app()


