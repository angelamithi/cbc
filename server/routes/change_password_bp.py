from datetime import datetime
from flask import Blueprint,request,make_response,jsonify
from flask_marshmallow import Marshmallow
from flask_restful import Api, Resource, reqparse,abort
from flask_jwt_extended import jwt_required,get_jwt_identity,current_user, get_jwt
from flask_bcrypt import Bcrypt
from models import db,Staff


change_password_bp=Blueprint('change_password_bp',__name__)
ma=Marshmallow(change_password_bp)
api=Api(change_password_bp)
bcrypt = Bcrypt()
 

change_password_args=reqparse.RequestParser()
change_password_args.add_argument('currentPassword',type=str, required=True)
change_password_args.add_argument('newPassword',type=str, required=True)
change_password_args.add_argument('confirmPassword',type=str, required=True)

forgot_password_args = reqparse.RequestParser()
forgot_password_args.add_argument('email', type=str, required=True, help="Email is required")
forgot_password_args.add_argument('school_id', type=str, required=True, help="School ID is required")
forgot_password_args.add_argument('newPassword', type=str, required=True, help="New password is required")
forgot_password_args.add_argument('confirmPassword', type=str, required=True, help="Confirm password is required")



class ChangePassword(Resource):
    @jwt_required()
    def post(self):
        data = change_password_args.parse_args()
        claims = get_jwt()
        print(claims)
        
        current_user = get_jwt_identity()
      
        staff = Staff.query.filter_by(id=current_user).first()

        if not staff:
            abort(404, detail="staff not found")

        if not bcrypt.check_password_hash(Staff.password, data["currentPassword"]):
            return abort(401, detail="Incorrect current password")
        
        if data["newPassword"] != data["confirmPassword"]:
            return abort(422, detail="New password and confirm password do not match")
        hashed_password = bcrypt.generate_password_hash(data["newPassword"]).decode('utf-8')
        
        Staff.password = hashed_password

        db.session.commit()

        return {'detail': 'Password has been changed successfully'}

        
api.add_resource(ChangePassword, '/change_password')

class ForgotPassword(Resource):
    def post(self):
        data = forgot_password_args.parse_args()

        # Filter by email_address and school_id
        staff = Staff.query.filter_by(email_address=data['email'], school_id=data['school_id']).first()

        if not staff:
            abort(404, detail="Employee not found")

        if data["newPassword"] != data["confirmPassword"]:
            return abort(422, detail="New password and confirm password do not match")

        # Update the password
        hashed_password = bcrypt.generate_password_hash(data["newPassword"]).decode('utf-8')
        staff.password = hashed_password

        db.session.commit()

        return {'detail': 'Password has been changed successfully'}

api.add_resource(ForgotPassword, '/forgot_password')


        


