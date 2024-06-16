from flask import Blueprint, make_response, jsonify
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_restful import Api, Resource, abort, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import School, db
from serializer import schoolSchema
from auth import admin_required,superAdmin_required

schools_bp = Blueprint('schools_bp', __name__)
api = Api(schools_bp)


post_args = reqparse.RequestParser()
post_args.add_argument('name', type=str, required=True,
                       help='School name is required')
post_args.add_argument('code', type=str,
                       required=True, help='School Code is required')
post_args.add_argument('address', type=str,
                       required=True, help='School address is required')
post_args.add_argument('contact', type=str, required=True, help='Phone Contact is required')
post_args.add_argument('email', type=str, help='email is required')

patch_args = reqparse.RequestParser()

patch_args.add_argument('name', type=str)
patch_args.add_argument('code', type=str)
patch_args.add_argument('address', type=str)
patch_args.add_argument('contact', type=str)
patch_args.add_argument('email', type=str)


class SchoolDetails(Resource):
    @superAdmin_required()
    def get(self):
        school_details = School.query.all()
        result = schoolSchema.dump(school_details, many=True)
        response = make_response(jsonify(result), 200)
        return response

  
    @superAdmin_required()
    def post(self):
        data = post_args.parse_args()

        # error handling
        school = School.query.filter_by(code=data.code).first()
        if school:
            return make_response(jsonify({"error": "School with the same code already exists"}), 409)



        new_school = School(name=data['name'], code=data['code'], address=data['address'],
                                contact=data['contact'], email=data['email'])
        db.session.add(new_school)
        db.session.commit()

        result = schoolSchema.dump(new_school)
        return make_response(jsonify(result), 201)


api.add_resource(SchoolDetails, '/schools')



class SchoolById(Resource):
    def get(self, id):
        single_school = School.query.filter_by(id=id).first()

        if not single_school:
            return make_response(jsonify({"error": f"School with id {id} does not exist"}), 404)

        else:
            result = schoolSchema.dump(single_school)
            return make_response(jsonify(result), 200)

    @superAdmin_required()
    def delete(self, id):
        single_school = School.query.filter_by(id=id).first()

        if not single_school:
            return make_response(jsonify({"error": f"School with id {id} does not exist"}), 404)

        db.session.delete(single_school)
        db.session.commit()

        return make_response(jsonify({"message": f"School with id {id} has been deleted"}), 200)

    @superAdmin_required()
    def patch(self, id):
        single_school = School.query.filter_by(id=id).first()

        if not single_school:
            return make_response(jsonify({"error": f"School with id {id} does not exist"}), 404)

        data = patch_args.parse_args()
       
        for key, value in data.items():
            if value is None:
                continue
            setattr(single_school, key, value)
        db.session.commit()

        

        result = schoolSchema.dump(single_school)
        return make_response(jsonify(result), 200)


api.add_resource(SchoolById, '/schools/<string:id>')