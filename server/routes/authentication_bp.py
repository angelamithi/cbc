from datetime import datetime
from flask import Blueprint, jsonify
from flask_restful import Api, Resource, abort, reqparse
from flask_bcrypt import Bcrypt
from flask_jwt_extended import jwt_required, get_jwt, JWTManager,get_jwt_identity
from flask_jwt_extended import create_access_token,create_refresh_token
from models import Staff, Designation, db, TokenBlocklist
from serializer import staffSchema

bcrypt = Bcrypt()

authentication_bp = Blueprint('authentication_bp', __name__)
api = Api(authentication_bp)

login_args = reqparse.RequestParser()
login_args.add_argument('email_address', type=str, required=True,
                        help="email_address is required")
login_args.add_argument('password', type=str, required=True,
                        help="Password is required")

class Login(Resource):
    def post(self):
        data = login_args.parse_args()
        email_address  = data['email_address']
        password = data['password']

        staff = Staff.query.filter_by(email_address=email_address).first()
        if not staff:
            abort(404, detail="The email provided was not found. Please provide a valid email or sign in")

        if bcrypt.check_password_hash(staff.password, password.encode('utf-8')):
            designation = Designation.query.get(staff.designation_id)
            if not designation:
                abort(404, detail="Designation not found for this staff member")

            access_token = create_access_token(identity=staff.id, additional_claims={
                "designation": designation.designation_code,
                "school_id": staff.school_id,
                "staff_id":staff.id,
                "first_name":staff.first_name,
                "last_name":staff.last_name,
                "photo_url":staff.photo_url

                # "permissions": designation.permissions
            })
            refresh_token = create_refresh_token(identity=staff.id, additional_claims={
                "designation": designation.designation_code,
                "school_id": staff.school_id,
                "staff_id":staff.id,
                "first_name":staff.first_name,
                "last_name":staff.last_name,
                "photo_url":staff.photo_url

                # "permissions": designation.permissions
            })
            # result = staffSchema.dump(staff)
            return jsonify(access_token=access_token,refresh_token=refresh_token)
        else:
            abort(400, detail="Your password is incorrect")

api.add_resource(Login, '/login')

class Refresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        identity = get_jwt_identity()
        # Fetch user details from the database
        staff = Staff.query.get(identity)
        if not staff:
            abort(404, detail="User not found")

        designation = Designation.query.get(staff.designation_id)
        if not designation:
            abort(404, detail="Designation not found for this staff member")

        # Create new access token with additional claims
        access_token = create_access_token(identity=staff.id, additional_claims={
            "designation": designation.designation_code,
            "school_id": staff.school_id,
            "staff_id": staff.id,
            "first_name": staff.first_name,
            "last_name": staff.last_name,
            "photo_url":staff.photo_url
        })

        return jsonify(access_token=access_token)

api.add_resource(Refresh, '/refresh')

# Logout function
class Logout(Resource):
    @jwt_required()
    def get(self):
        token = get_jwt()
        blocked_token = TokenBlocklist(
            jti=token['jti'], created_at=datetime.utcnow())
        db.session.add(blocked_token)
        db.session.commit()
        return {'detail': "Token logged out"}

api.add_resource(Logout, '/logout')
