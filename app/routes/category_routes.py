from flask import Blueprint, jsonify, request
from app.schemas import CategorySchema
from app.models.category import Category
from app import db
from pydantic import ValidationError


category_bp = Blueprint('categories', __name__)

@category_bp.route("/create", methods=['POST'])
def create_category():
    data = request.get_json()
    category_data = CategorySchema(**data)
    new_category = Category(name=category_data.name)
    db.session.add(new_category)
    db.session.commit()
    return jsonify(CategorySchema.from_orm(new_category).dict()), 201


@category_bp.route("/list", methods=['GET'])
def get_all_category():
    data = Category.query.all()
    return jsonify([CategorySchema.from_orm(i).dict() for i in data])

@category_bp.route("/get/<int:id>")
def get_one(id):
    cat = Category.query.get_or_404(id)
    return jsonify(CategorySchema.from_orm(cat).dict())

@category_bp.route("/update/<int:id>", methods=['PUT'])
def update_category(id):
    data = request.get_json()
    category = CategorySchema(**data)
    cat = Category.query.get_or_404(id)
    cat.name = category.name
    db.session.commit()
    return jsonify(CategorySchema.from_orm(cat).dict())

@category_bp.route("/delete/<int:id>", methods=['DELETE'])
def delete_category(id):
    cat = Category.query.get_or_404(id)
    db.session.delete(cat)
    db.session.commit()
    return jsonify({'msg':'data is deleted'})