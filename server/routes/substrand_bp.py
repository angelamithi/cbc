from flask import Blueprint, make_response, jsonify
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required
from models import SubStrand, db
from serializer import subStrandSchema
from auth import admin_required, superAdmin_required

substrand_bp = Blueprint('substrand_bp', __name__)
api = Api(substrand_bp)

post_args = reqparse.RequestParser()
post_args.add_argument('school_id', type=str, required=True, help='School Id is required')
post_args.add_argument('substrand_name', type=str, required=True, help='SubStrand Name is required')
post_args.add_argument('strand_id', type=str, required=True, help='Strand Id is required')
post_args.add_argument('subject_id', type=str, required=True, help='Subject Id is required')
post_args.add_argument('grade_id', type=str, required=True, help='Grade Id is required')

patch_args = reqparse.RequestParser()
patch_args.add_argument('school_id', type=str)
patch_args.add_argument('substrand_name', type=str)
patch_args.add_argument('strand_id', type=str)
patch_args.add_argument('subject_id', type=str)
patch_args.add_argument('grade_id', type=str)

class SubStrandDetails(Resource):
    @jwt_required()
    def get(self):
        sub_strands = SubStrand.query.all()
        result = subStrandSchema.dump(sub_strands, many=True)
        return make_response(jsonify(result), 200)

    @superAdmin_required()
    def post(self):
        data = post_args.parse_args()

        # Check if the sub-strand already exists
        existing_sub_strand = SubStrand.query.filter_by(school_id=data['school_id'], substrand_name=data['substrand_name'],
                                                        strand_id=data['strand_id'], subject_id=data['subject_id'],
                                                        grade_id=data['grade_id']).first()
        if existing_sub_strand:
            return make_response(jsonify({"error": "SubStrand already exists for this school, strand, subject, and grade"}), 409)

        new_sub_strand = SubStrand(school_id=data['school_id'], substrand_name=data['substrand_name'],
                                   strand_id=data['strand_id'], subject_id=data['subject_id'], grade_id=data['grade_id'])
        db.session.add(new_sub_strand)
        db.session.commit()

        result = subStrandSchema.dump(new_sub_strand)
        return make_response(jsonify(result), 201)

api.add_resource(SubStrandDetails, '/substrands')

class SubStrandById(Resource):
    @jwt_required()
    def get(self, id):
        sub_strand = SubStrand.query.get(id)
        if not sub_strand:
            return make_response(jsonify({"error": "SubStrand not found"}), 404)

        result = subStrandSchema.dump(sub_strand)
        return make_response(jsonify(result), 200)

    @superAdmin_required()
    def delete(self, id):
        sub_strand = SubStrand.query.get(id)
        if not sub_strand:
            return make_response(jsonify({"error": "SubStrand not found"}), 404)

        db.session.delete(sub_strand)
        db.session.commit()
        return make_response(jsonify({"message": "SubStrand deleted successfully"}), 200)

    @superAdmin_required()
    def patch(self, id):
        sub_strand = SubStrand.query.get(id)
        if not sub_strand:
            return make_response(jsonify({"error": "SubStrand not found"}), 404)

        data = patch_args.parse_args()
        for key, value in data.items():
            if value is not None:
                setattr(sub_strand, key, value)

        db.session.commit()
        result = subStrandSchema.dump(sub_strand)
        return make_response(jsonify(result), 200)

api.add_resource(SubStrandById, '/substrands/<string:id>')

