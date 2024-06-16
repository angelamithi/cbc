from flask import Blueprint, make_response, jsonify
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required
from models import Strand, db
from serializer import strandSchema
from auth import admin_required, superAdmin_required

strand_bp = Blueprint('strand_bp', __name__)
api = Api(strand_bp)

post_args = reqparse.RequestParser()
post_args.add_argument('school_id', type=str, required=True, help='School Id is required')
post_args.add_argument('strand_name', type=str, required=True, help='Strand Name is required')
post_args.add_argument('subject_id', type=str, required=True, help='Subject Id is required')
post_args.add_argument('grade_id', type=str, required=True, help='Grade Id is required')

patch_args = reqparse.RequestParser()
patch_args.add_argument('school_id', type=str)
patch_args.add_argument('strand_name', type=str)
patch_args.add_argument('subject_id', type=str)
patch_args.add_argument('grade_id', type=str)

class StrandDetails(Resource):
    @jwt_required()
    def get(self):
        strands = Strand.query.all()
        result = strandSchema.dump(strands, many=True)
        return make_response(jsonify(result), 200)

    @superAdmin_required()
    def post(self):
        data = post_args.parse_args()

        # Check if the strand already exists
        existing_strand = Strand.query.filter_by(school_id=data['school_id'], strand_name=data['strand_name'],
                                                 subject_id=data['subject_id'], grade_id=data['grade_id']).first()
        if existing_strand:
            return make_response(jsonify({"error": "Strand already exists for this school, subject, and grade"}), 409)

        new_strand = Strand(school_id=data['school_id'], strand_name=data['strand_name'],
                            subject_id=data['subject_id'], grade_id=data['grade_id'])
        db.session.add(new_strand)
        db.session.commit()

        result = strandSchema.dump(new_strand)
        return make_response(jsonify(result), 201)

api.add_resource(StrandDetails, '/strands')

class StrandById(Resource):
    @jwt_required()
    def get(self, id):
        strand = Strand.query.get(id)
        if not strand:
            return make_response(jsonify({"error": "Strand not found"}), 404)

        result = strandSchema.dump(strand)
        return make_response(jsonify(result), 200)

    @superAdmin_required()
    def delete(self, id):
        strand = Strand.query.get(id)
        if not strand:
            return make_response(jsonify({"error": "Strand not found"}), 404)

        db.session.delete(strand)
        db.session.commit()
        return make_response(jsonify({"message": "Strand deleted successfully"}), 200)

    @superAdmin_required()
    def patch(self, id):
        strand = Strand.query.get(id)
        if not strand:
            return make_response(jsonify({"error": "Strand not found"}), 404)

        data = patch_args.parse_args()
        for key, value in data.items():
            if value is not None:
                setattr(strand, key, value)

        db.session.commit()
        result = strandSchema.dump(strand)
        return make_response(jsonify(result), 200)

api.add_resource(StrandById, '/strands/<string:id>')
