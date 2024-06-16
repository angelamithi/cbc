from flask import Blueprint, make_response, jsonify
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required
from models import Designation, db
from serializer import designationSchema
from auth import admin_required, superAdmin_required

designation_bp = Blueprint('designation_bp', __name__)
api = Api(designation_bp)

post_args = reqparse.RequestParser()
post_args.add_argument('designation_name', type=str, required=True, help='Designation Name is required')
post_args.add_argument('designation_code', type=int, required=True, help='Designation Code is required')
post_args.add_argument('school_id', type=str, required=True, help='School Id is required')

patch_args = reqparse.RequestParser()
patch_args.add_argument('designation_name', type=str)
patch_args.add_argument('designation_code', type=int)
patch_args.add_argument('school_id', type=str)

class DesignationDetails(Resource):
    @admin_required()
    def get(self):
        designations = Designation.query.all()
        result = designationSchema.dump(designations, many=True)
        return make_response(jsonify(result), 200)

    @admin_required()
    def post(self):
        data = post_args.parse_args()

        # Check if the designation already exists
        existing_designation = Designation.query.filter_by(school_id=data['school_id'], designation_name=data['designation_name']).first()
        if existing_designation:
            return make_response(jsonify({"error": "Designation already exists for this school"}), 409)

        new_designation = Designation(designation_name=data['designation_name'], designation_code=data['designation_code'],
                                      school_id=data['school_id'])
        db.session.add(new_designation)
        db.session.commit()

        result = designationSchema.dump(new_designation)
        return make_response(jsonify(result), 201)

api.add_resource(DesignationDetails, '/designations')

class DesignationById(Resource):
    @jwt_required()
    def get(self, id):
        designation = Designation.query.get(id)
        if not designation:
            return make_response(jsonify({"error": "Designation not found"}), 404)

        result = designationSchema.dump(designation)
        return make_response(jsonify(result), 200)

    @admin_required()
    def delete(self, id):
        designation = Designation.query.get(id)
        if not designation:
            return make_response(jsonify({"error": "Designation not found"}), 404)

        db.session.delete(designation)
        db.session.commit()
        return make_response(jsonify({"message": "Designation deleted successfully"}), 200)

    @admin_required()
    def patch(self, id):
        designation = Designation.query.get(id)
        if not designation:
            return make_response(jsonify({"error": "Designation not found"}), 404)

        data = patch_args.parse_args()
        for key, value in data.items():
            if value is not None:
                setattr(designation, key, value)

        db.session.commit()
        result = designationSchema.dump(designation)
        return make_response(jsonify(result), 200)

api.add_resource(DesignationById, '/designations/<string:id>')
