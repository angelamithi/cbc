from flask import Blueprint, make_response, jsonify
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required
from models import Department, db
from serializer import departmentSchema
from auth import admin_required, superAdmin_required

department_bp = Blueprint('department_bp', __name__)
api = Api(department_bp)

post_args = reqparse.RequestParser()
post_args.add_argument('school_id', type=str, required=True, help='School Id is required')
post_args.add_argument('department_name', type=str, required=True, help='Department Name is required')
post_args.add_argument('department_head', type=str, required=True, help='Department Head is required')
post_args.add_argument('dept_staff', type=str, required=True, help='Department Staff is required')

patch_args = reqparse.RequestParser()
patch_args.add_argument('school_id', type=str)
patch_args.add_argument('department_name', type=str)
patch_args.add_argument('department_head', type=str)
patch_args.add_argument('dept_staff', type=str)

class DepartmentDetails(Resource):
    @jwt_required()
    def get(self):
        departments = Department.query.all()
        result = departmentSchema.dump(departments, many=True)
        return make_response(jsonify(result), 200)

    @admin_required()
    def post(self):
        data = post_args.parse_args()

        # Check if the department already exists
        existing_department = Department.query.filter_by(school_id=data['school_id'], department_name=data['department_name']).first()
        if existing_department:
            return make_response(jsonify({"error": "Department already exists for this school"}), 409)

        new_department = Department(school_id=data['school_id'], department_name=data['department_name'],
                                    department_head=data['department_head'], dept_staff=data['dept_staff'])
        db.session.add(new_department)
        db.session.commit()

        result = departmentSchema.dump(new_department)
        return make_response(jsonify(result), 201)

api.add_resource(DepartmentDetails, '/departments')

class DepartmentById(Resource):
    @jwt_required()
    def get(self, id):
        department = Department.query.get(id)
        if not department:
            return make_response(jsonify({"error": "Department not found"}), 404)

        result = departmentSchema.dump(department)
        return make_response(jsonify(result), 200)

    @admin_required()
    def delete(self, id):
        department = Department.query.get(id)
        if not department:
            return make_response(jsonify({"error": "Department not found"}), 404)

        db.session.delete(department)
        db.session.commit()
        return make_response(jsonify({"message": "Department deleted successfully"}), 200)

    @admin_required()
    def patch(self, id):
        department = Department.query.get(id)
        if not department:
            return make_response(jsonify({"error": "Department not found"}), 404)

        data = patch_args.parse_args()
        for key, value in data.items():
            if value is not None:
                setattr(department, key, value)

        db.session.commit()
        result = departmentSchema.dump(department)
        return make_response(jsonify(result), 200)

api.add_resource(DepartmentById, '/departments/<string:id>')
