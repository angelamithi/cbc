from flask import Blueprint, make_response, jsonify
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required
from models import Parent, db
from serializer import parentSchema
from auth import admin_required, superAdmin_required

parent_bp = Blueprint('parent_bp', __name__)
api = Api(parent_bp)

post_args = reqparse.RequestParser()
post_args.add_argument('school_id', type=str, required=True, help='School Id is required')
post_args.add_argument('mothers_first_name', type=str)
post_args.add_argument('mothers_last_name', type=str)
post_args.add_argument('mothers_contact', type=str)
post_args.add_argument('mothers_email', type=str)
post_args.add_argument('fathers_first_name', type=str)
post_args.add_argument('fathers_last_name', type=str)
post_args.add_argument('fathers_contact', type=str)
post_args.add_argument('fathers_email', type=str)
post_args.add_argument('guardian_first_name', type=str)
post_args.add_argument('guardian_last_name', type=str)
post_args.add_argument('guardian_contact', type=str)
post_args.add_argument('guardian_email', type=str)
post_args.add_argument('student_id', type=str, required=True, help='Student Id is required')

patch_args = reqparse.RequestParser()
patch_args.add_argument('school_id', type=str)
patch_args.add_argument('mothers_first_name', type=str)
patch_args.add_argument('mothers_last_name', type=str)
patch_args.add_argument('mothers_contact', type=str)
patch_args.add_argument('mothers_email', type=str)
patch_args.add_argument('fathers_first_name', type=str)
patch_args.add_argument('fathers_last_name', type=str)
patch_args.add_argument('fathers_contact', type=str)
patch_args.add_argument('fathers_email', type=str)
patch_args.add_argument('guardian_first_name', type=str)
patch_args.add_argument('guardian_last_name', type=str)
patch_args.add_argument('guardian_contact', type=str)
patch_args.add_argument('guardian_email', type=str)
patch_args.add_argument('student_id', type=str)

class ParentDetails(Resource):
    @jwt_required()
    def get(self):
        parents = Parent.query.all()
        result = parentSchema.dump(parents, many=True)
        return make_response(jsonify(result), 200)

    @admin_required()
    def post(self):
        data = post_args.parse_args()

        # Check if the parent already exists for the student
        existing_parent = Parent.query.filter_by(student_id=data['student_id']).first()
        if existing_parent:
            return make_response(jsonify({"error": "Parent details already exist for this student"}), 409)

        new_parent = Parent(school_id=data['school_id'], mothers_first_name=data['mothers_first_name'],
                            mothers_last_name=data['mothers_last_name'], mothers_contact=data['mothers_contact'],
                            mothers_email=data['mothers_email'], fathers_first_name=data['fathers_first_name'],
                            fathers_last_name=data['fathers_last_name'], fathers_contact=data['fathers_contact'],
                            fathers_email=data['fathers_email'], guardian_first_name=data['guardian_first_name'],
                            guardian_last_name=data['guardian_last_name'], guardian_contact=data['guardian_contact'],
                            guardian_email=data['guardian_email'], student_id=data['student_id'])
        db.session.add(new_parent)
        db.session.commit()

        result = parentSchema.dump(new_parent)
        return make_response(jsonify(result), 201)

api.add_resource(ParentDetails, '/parents')

class ParentById(Resource):
    @jwt_required()
    def get(self, id):
        parent = Parent.query.get(id)
        if not parent:
            return make_response(jsonify({"error": "Parent details not found"}), 404)

        result = parentSchema.dump(parent)
        return make_response(jsonify(result), 200)

    @admin_required()
    def delete(self, id):
        parent = Parent.query.get(id)
        if not parent:
            return make_response(jsonify({"error": "Parent details not found"}), 404)

        db.session.delete(parent)
        db.session.commit()
        return make_response(jsonify({"message": "Parent details deleted successfully"}), 200)

    @admin_required()
    def patch(self, id):
        parent = Parent.query.get(id)
        if not parent:
            return make_response(jsonify({"error": "Parent details not found"}), 404)

        data = patch_args.parse_args()
        for key, value in data.items():
            if value is not None:
                setattr(parent, key, value)

        db.session.commit()
        result = parentSchema.dump(parent)
        return make_response(jsonify(result), 200)

api.add_resource(ParentById, '/parents/<string:id>')
