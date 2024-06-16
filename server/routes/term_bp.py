from flask import Blueprint, make_response, jsonify
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required
from models import Term, db
from serializer import termSchema
from auth import admin_required, superAdmin_required

term_bp = Blueprint('term_bp', __name__)
api = Api(term_bp)

post_args = reqparse.RequestParser()
post_args.add_argument('school_id', type=str, required=True, help='School Id is required')
post_args.add_argument('term_name', type=str, required=True, help='Term Name is required')

patch_args = reqparse.RequestParser()
patch_args.add_argument('school_id', type=str)
patch_args.add_argument('term_name', type=str)

class TermDetails(Resource):
    @jwt_required()
    def get(self):
        terms = Term.query.all()
        result = termSchema.dump(terms, many=True)
        return make_response(jsonify(result), 200)

    @superAdmin_required()
    def post(self):
        data = post_args.parse_args()

        # Check if the term already exists
        existing_term = Term.query.filter_by(school_id=data['school_id'], term_name=data['term_name']).first()
        if existing_term:
            return make_response(jsonify({"error": "Term already exists for this school"}), 409)

        new_term = Term(school_id=data['school_id'], term_name=data['term_name'])
        db.session.add(new_term)
        db.session.commit()

        result = termSchema.dump(new_term)
        return make_response(jsonify(result), 201)

api.add_resource(TermDetails, '/terms')

class TermById(Resource):
    @jwt_required()
    def get(self, id):
        term = Term.query.get(id)
        if not term:
            return make_response(jsonify({"error": "Term not found"}), 404)

        result = termSchema.dump(term)
        return make_response(jsonify(result), 200)

    @superAdmin_required()
    def delete(self, id):
        term = Term.query.get(id)
        if not term:
            return make_response(jsonify({"error": "Term not found"}), 404)

        db.session.delete(term)
        db.session.commit()
        return make_response(jsonify({"message": "Term deleted successfully"}), 200)

    @superAdmin_required()
    def patch(self, id):
        term = Term.query.get(id)
        if not term:
            return make_response(jsonify({"error": "Term not found"}), 404)

        data = patch_args.parse_args()
        for key, value in data.items():
            if value is not None:
                setattr(term, key, value)

        db.session.commit()
        result = termSchema.dump(term)
        return make_response(jsonify(result), 200)

api.add_resource(TermById, '/terms/<string:id>')
