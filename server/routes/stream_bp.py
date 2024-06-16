from flask import Blueprint, make_response, jsonify
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required
from models import Stream, db
from serializer import streamSchema
from auth import admin_required, superAdmin_required

stream_bp = Blueprint('stream_bp', __name__)
api = Api(stream_bp)

post_args = reqparse.RequestParser()
post_args.add_argument('school_id', type=str, required=True, help='School Id is required')
post_args.add_argument('stream_name', type=str, required=True, help='Stream Name is required')

patch_args = reqparse.RequestParser()
patch_args.add_argument('school_id', type=str)
patch_args.add_argument('stream_name', type=str)

class StreamDetails(Resource):
    @jwt_required()
    def get(self):
        streams = Stream.query.all()
        result = streamSchema.dump(streams, many=True)
        return make_response(jsonify(result), 200)

    @admin_required()
    def post(self):
        data = post_args.parse_args()

        # Check if the stream already exists
        existing_stream = Stream.query.filter_by(school_id=data['school_id'], stream_name=data['stream_name']).first()
        if existing_stream:
            return make_response(jsonify({"error": "Stream already exists for this school"}), 409)

        new_stream = Stream(school_id=data['school_id'], stream_name=data['stream_name'])
        db.session.add(new_stream)
        db.session.commit()

        result = streamSchema.dump(new_stream)
        return make_response(jsonify(result), 201)

api.add_resource(StreamDetails, '/streams')

class StreamById(Resource):
    @jwt_required()
    def get(self, id):
        stream = Stream.query.get(id)
        if not stream:
            return make_response(jsonify({"error": "Stream not found"}), 404)

        result = streamSchema.dump(stream)
        return make_response(jsonify(result), 200)

    @admin_required()
    def delete(self, id):
        stream = Stream.query.get(id)
        if not stream:
            return make_response(jsonify({"error": "Stream not found"}), 404)

        db.session.delete(stream)
        db.session.commit()
        return make_response(jsonify({"message": "Stream deleted successfully"}), 200)

    @admin_required()
    def patch(self, id):
        stream = Stream.query.get(id)
        if not stream:
            return make_response(jsonify({"error": "Stream not found"}), 404)

        data = patch_args.parse_args()
        for key, value in data.items():
            if value is not None:
                setattr(stream, key, value)

        db.session.commit()
        result = streamSchema.dump(stream)
        return make_response(jsonify(result), 200)

api.add_resource(StreamById, '/streams/<string:id>')
