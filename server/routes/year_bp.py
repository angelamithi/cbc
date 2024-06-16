from flask import Blueprint, make_response, jsonify
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required
from models import Year, db
from serializer import yearSchema
from auth import admin_required, superAdmin_required

year_bp = Blueprint('year_bp', __name__)
api = Api(year_bp)

post_args = reqparse.RequestParser()
post_args.add_argument('school_id', type=str, required=True, help='School Id is required')
post_args.add_argument('year_name', type=int, required=True, help='Year Name is required')

patch_args = reqparse.RequestParser()
patch_args.add_argument('school_id', type=str)
patch_args.add_argument('year_name', type=int)

class YearDetails(Resource):
    @jwt_required()
    def get(self):
        years = Year.query.all()
        result = yearSchema.dump(years, many=True)
        return make_response(jsonify(result), 200)

    @superAdmin_required()
    def post(self):
        data = post_args.parse_args()

        # Check if the year already exists
        existing_year = Year.query.filter_by(school_id=data['school_id'], year_name=data['year_name']).first()
        if existing_year:
            return make_response(jsonify({"error": "Year already exists for this school"}), 409)

        new_year = Year(school_id=data['school_id'], year_name=data['year_name'])
        db.session.add(new_year)
        db.session.commit()

        result = yearSchema.dump(new_year)
        return make_response(jsonify(result), 201)

api.add_resource(YearDetails, '/years')

class YearById(Resource):
    @jwt_required()
    def get(self, id):
        year = Year.query.get(id)
        if not year:
            return make_response(jsonify({"error": "Year not found"}), 404)

        result = yearSchema.dump(year)
        return make_response(jsonify(result), 200)

    @superAdmin_required()
    def delete(self, id):
        year = Year.query.get(id)
        if not year:
            return make_response(jsonify({"error": "Year not found"}), 404)

        db.session.delete(year)
        db.session.commit()
        return make_response(jsonify({"message": "Year deleted successfully"}), 200)

    @superAdmin_required()
    def patch(self, id):
        year = Year.query.get(id)
        if not year:
            return make_response(jsonify({"error": "Year not found"}), 404)

        data = patch_args.parse_args()
        for key, value in data.items():
            if value is not None:
                setattr(year, key, value)

        db.session.commit()
        result = yearSchema.dump(year)
        return make_response(jsonify(result), 200)

api.add_resource(YearById, '/years/<string:id>')
