from flask import Blueprint, make_response, jsonify
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required
from models import Staff, db
from serializer import staffSchema
from auth import admin_required, superAdmin_required
from datetime import datetime
from flask_bcrypt import Bcrypt

staff_bp = Blueprint('staff_bp', __name__)

bcrypt = Bcrypt()
api = Api(staff_bp)

post_args = reqparse.RequestParser()
post_args.add_argument('school_id', type=str, required=True, help='School Id is required')
post_args.add_argument('payroll_number', type=str, required=True, help='Payroll Number is required')
post_args.add_argument('first_name', type=str, required=True, help='First Name is required')
post_args.add_argument('last_name', type=str, required=True, help='Last Name is required')
post_args.add_argument('date_of_birth', type=str, required=True, help='Date of Birth is required')
post_args.add_argument('phone_number', type=str)
post_args.add_argument('alternative_contact', type=str)
post_args.add_argument('email_address', type=str)
post_args.add_argument('password', type=str, required=True, help='Password is required')
post_args.add_argument('designation_id', type=str, required=True, help='Designation ID is required')

patch_args = reqparse.RequestParser()
patch_args.add_argument('school_id', type=str)
patch_args.add_argument('payroll_number', type=str)
patch_args.add_argument('first_name', type=str)
patch_args.add_argument('last_name', type=str)
patch_args.add_argument('date_of_birth', type=str)
patch_args.add_argument('phone_number', type=str)
patch_args.add_argument('alternative_contact', type=str)
patch_args.add_argument('email_address', type=str)
patch_args.add_argument('password', type=str)
patch_args.add_argument('designation_id', type=str)

class StaffDetails(Resource):
    # @admin_required()
    def get(self):
        staff = Staff.query.all()
        result = staffSchema.dump(staff, many=True)
        return make_response(jsonify(result), 200)

    # @admin_required()
    def post(self):
        data = post_args.parse_args()

        # Check if the staff already exists
        existing_staff = Staff.query.filter_by(school_id=data['school_id'], payroll_number=data['payroll_number']).first()
        if existing_staff:
            return make_response(jsonify({"error": "Staff with the same payroll number already exists"}), 409)
        
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')

             

        date_of_birth = datetime.strptime(data["date_of_birth"], "%Y-%m-%d")
        new_staff = Staff(school_id=data['school_id'], payroll_number=data['payroll_number'],
                          first_name=data['first_name'], last_name=data['last_name'],
                          date_of_birth=date_of_birth, phone_number=data['phone_number'],
                          alternative_contact=data['alternative_contact'], email_address=data['email_address'],
                          password=hashed_password, designation_id=data['designation_id'])
        db.session.add(new_staff)
        db.session.commit()

        result = staffSchema.dump(new_staff)
        return make_response(jsonify(result), 201)

api.add_resource(StaffDetails, '/staffs')

class StaffById(Resource):
    # @admin_required()
    def get(self, id):
        staff = Staff.query.get(id)
        if not staff:
            return make_response(jsonify({"error": "Staff not found"}), 404)

        result = staffSchema.dump(staff)
        return make_response(jsonify(result), 200)

    @admin_required()
    def delete(self, id):
        staff = Staff.query.get(id)
        if not staff:
            return make_response(jsonify({"error": "Staff not found"}), 404)

        db.session.delete(staff)
        db.session.commit()
        return make_response(jsonify({"message": "Staff deleted successfully"}), 200)

    @admin_required()
    def patch(self, id):
        staff = Staff.query.get(id)
        if not staff:
            return make_response(jsonify({"error": "Staff not found"}), 404)

        data = patch_args.parse_args()
        for key, value in data.items():
            if value is not None:
                setattr(staff, key, value)

        db.session.commit()
        result = staffSchema.dump(staff)
        return make_response(jsonify(result), 200)

api.add_resource(StaffById, '/staffs/<string:id>')
