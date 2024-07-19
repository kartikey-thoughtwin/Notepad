from flask_restx import Resource
from flask import request, Blueprint, Response
from app import api, db
from app.models import Category
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import NotFound
import json
from app.utils.utils import validate_data, make_response

category_bp = Blueprint("category", __name__)


class CategoryAPI(Resource):
    """
    RESTful API for managing categories.
    """

    def get(self, category_id=None):
        """
        GET method to retrieve either all categories or a specific category by ID.

        Args:
            category_id (int, optional): ID of the category to retrieve. Defaults to None.

        Returns:
            Response: JSON response with status, message, and data.
        """
        try:
            if category_id is None:
                categories = Category.query.all()
                return make_response(
                    status=True,
                    message="Categories retrieved successfully",
                    data=[category.to_dict() for category in categories],
                )

            try:
                category = Category.query.get_or_404(category_id)
                return make_response(
                    status=True,
                    message="Category retrieved successfully",
                    data=category.to_dict(),
                )

            except NotFound:
                return make_response(
                    status=False, message="Category not found", status_code=404
                )

        except SQLAlchemyError as e:
            return make_response(status=False, message=str(e), status_code=500)

    def post(self):
        """
        POST method to create a new category.

        Returns:
            Response: JSON response containing status, message, and data.
        """
        try:
            data = request.get_json()
            validation_result = validate_data(data)
            if not validation_result["status"]:
                return make_response(
                    status=False, message=validation_result["message"], status_code=400
                )

            new_category = Category(name=data["name"])
            db.session.add(new_category)
            db.session.commit()
            return make_response(
                status=True,
                message="Category Created Successfully",
                data=new_category.to_dict(),
                status_code=201,
            )

        except SQLAlchemyError as e:
            db.session.rollback()
            return make_response(status=False, message=str(e), status_code=500)

    def put(self, category_id):
        """
        PUT method updates an existing category by `category_id`.

        Args:
            category_id (int): ID of the category to update.

        Returns:
            Response: JSON response containing status, message, and data.
        """
        try:
            data = request.get_json()
            validation_result = validate_data(data)
            if not validation_result["status"]:
                return make_response(
                    status=False, message=validation_result["message"], status_code=400
                )

            try:
                category = Category.query.get_or_404(category_id)
                category.name = data["name"]
                db.session.commit()
                return make_response(
                    status=True,
                    message="Category updated successfully",
                    data=category.to_dict(),
                )

            except NotFound:
                return make_response(
                    status=False, message="Category not found", status_code=404
                )

        except SQLAlchemyError as e:
            db.session.rollback()
            return make_response(status=False, message=str(e), status_code=500)

    def delete(self, category_id):
        """
        DELETE method to delete a category by ID.

        Args:
            category_id (int): ID of the category to delete.

        Returns:
            Response: Empty response with HTTP status code 204 NO CONTENT.
        """
        try:
            try:
                category = Category.query.get_or_404(category_id)
                db.session.delete(category)
                db.session.commit()
                return make_response(
                    status=True,
                    message="Category deleted successfully",
                    status_code=204,
                )
            except NotFound:
                return make_response(
                    status=False, message="Category not found", status_code=404
                )

        except SQLAlchemyError as e:
            db.session.rollback()
            return make_response(status=False, message=str(e), status_code=500)


api.add_resource(CategoryAPI, "/categories/list/", methods=["GET"])
api.add_resource(CategoryAPI, "/categories/get/<int:category_id>/", methods=["GET"])
api.add_resource(CategoryAPI, "/categories/post/", methods=["POST"])
api.add_resource(CategoryAPI, "/categories/put/<int:category_id>/", methods=["PUT"])
api.add_resource(
    CategoryAPI, "/categories/delete/<int:category_id>/", methods=["DELETE"]
)
