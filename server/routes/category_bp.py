from flask import Blueprint, make_response, jsonify
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required
from models import Category, db
from serializer import categorySchema
from auth import admin_required, superAdmin_required

category_bp = Blueprint('category_bp', __name__)
api = Api(category_bp)

post_args = reqparse.RequestParser()
post_args.add_argument('school_id', type=str, required=True, help='School Id is required')
post_args.add_argument('category_name', type=str, required=True, help='Category Name is required')

patch_args = reqparse.RequestParser()
patch_args.add_argument('school_id', type=str)
patch_args.add_argument('category_name', type=str)

class CategoryDetails(Resource):
    @jwt_required()
    def get(self):
        categories = Category.query.all()
        result = categorySchema.dump(categories, many=True)
        return make_response(jsonify(result), 200)

    @superAdmin_required()
    def post(self):
        data = post_args.parse_args()

        # Check if the category already exists
        existing_category = Category.query.filter_by(school_id=data['school_id'], category_name=data['category_name']).first()
        if existing_category:
            return make_response(jsonify({"error": "Category already exists for this school"}), 409)

        new_category = Category(school_id=data['school_id'], category_name=data['category_name'])
        db.session.add(new_category)
        db.session.commit()

        result = categorySchema.dump(new_category)
        return make_response(jsonify(result), 201)

api.add_resource(CategoryDetails, '/categories')

class CategoryById(Resource):
    @jwt_required()
    def get(self, id):
        category = Category.query.get(id)
        if not category:
            return make_response(jsonify({"error": "Category not found"}), 404)

        result = categorySchema.dump(category)
        return make_response(jsonify(result), 200)

    @superAdmin_required()
    def delete(self, id):
        category = Category.query.get(id)
        if not category:
            return make_response(jsonify({"error": "Category not found"}), 404)

        db.session.delete(category)
        db.session.commit()
        return make_response(jsonify({"message": "Category deleted successfully"}), 200)

    @superAdmin_required()
    def patch(self, id):
        category = Category.query.get(id)
        if not category:
            return make_response(jsonify({"error": "Category not found"}), 404)

        data = patch_args.parse_args()
        for key, value in data.items():
            if value is not None:
                setattr(category, key, value)

        db.session.commit()
        result = categorySchema.dump(category)
        return make_response(jsonify(result), 200)

api.add_resource(CategoryById, '/categories/<string:id>')
