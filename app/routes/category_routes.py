from flask_restx import Resource
from flask import request, Blueprint, Response
from app import api, db
from app.models import Category
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import NotFound
import json
from app.utils.utils import validate_data

category_bp = Blueprint("category", __name__)


class CategoryAPI(Resource):

    def get(self, category_id=None):
        try:
            if category_id is None:
                categories = Category.query.all()
                # response_data = [category.to_dict() for category in categories]
                response_data = {
                    "status": True,
                    "data": [category.to_dict() for category in categories],
                }
                return Response(
                    json.dumps(response_data),
                    status=200,
                    content_type="application/json",
                )
            try:
                category = Category.query.get_or_404(category_id)
                response_data = {"status": True, "data": category.to_dict()}
                return Response(
                    json.dumps(response_data),
                    status=200,
                    content_type="application/json",
                )
            except NotFound:
                response_data = {"status": False, "error": "Category not found"}
                return Response(
                    json.dumps(response_data),
                    status=404,
                    content_type="application/json",
                )
        except SQLAlchemyError as e:
            response_data = {"status": False, "error": str(e)}
            return Response(
                json.dumps(response_data),
                status=500,
                content_type="application/json",
            )

    def post(self):
        try:
            data = request.get_json()
            validation_result = validate_data(data)
            if not validation_result["status"]:
                return Response(
                    json.dumps(validation_result),
                    status=400,
                    content_type="application/json",
                )

            new_category = Category(name=data["name"])
            db.session.add(new_category)
            db.session.commit()

            response_data = {
                "message": "Category Created Successfully",
                "status": True,
                "data": new_category.to_dict(),
            }

            return Response(
                json.dumps(response_data), status=201, content_type="application/json"
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            response_data = {"status": False, "error": str(e)}
            return Response(
                json.dumps(response_data),
                status=500,
                content_type="application/json",
            )

    def put(self, category_id):
        try:
            data = request.get_json()
            validation_result = validate_data(data)
            if not validation_result["status"]:
                return Response(
                    json.dumps(validation_result),
                    status=400,
                    content_type="application/json",
                )
            try:
                category = Category.query.get_or_404(category_id)
                category.name = data["name"]
                db.session.commit()
                response_data = {"status": True, "data": category.to_dict()}
                return Response(
                    json.dumps(response_data),
                    status=200,
                    content_type="application/json",
                )
            except NotFound:
                response_data = {"status": False, "error": "Category not found"}
                return Response(
                    json.dumps(response_data),
                    status=404,
                    content_type="application/json",
                )
        except SQLAlchemyError as e:
            db.session.rollback()
            response_data = {"status": False, "error": str(e)}
            return Response(
                json.dumps(response_data),
                status=500,
                content_type="application/json",
            )

    def delete(self, category_id):
        try:
            try:
                category = Category.query.get_or_404(category_id)
                db.session.delete(category)
                db.session.commit()
                return Response("", status=204)
            except NotFound:
                response_data = {"status": False, "error": "Category not found"}
                return Response(
                    json.dumps(response_data),
                    status=404,
                    content_type="application/json",
                )
        except SQLAlchemyError as e:
            db.session.rollback()
            response_data = {"status": False, "error": str(e)}
            return Response(
                json.dumps(response_data),
                status=500,
                content_type="application/json",
            )


api.add_resource(CategoryAPI, "/categories/", methods=["GET"])
api.add_resource(CategoryAPI, "/categories/<int:category_id>/", methods=["GET"])
api.add_resource(CategoryAPI, "/categories/post/", methods=["POST"])
api.add_resource(CategoryAPI, "/categories/put/<int:category_id>/", methods=["PUT"])
api.add_resource(
    CategoryAPI, "/categories/delete/<int:category_id>/", methods=["DELETE"]
)
