from flask_restx import Resource
from flask import request, Blueprint, Response, jsonify
from app import api, db
from app.models import User
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import NotFound
import json
from app.utils.utils import validate_user_data

user_bp = Blueprint("user", __name__)


class UserAPI(Resource):

    def get(self, user_id=None):
        try:
            if user_id is None:
                users = User.query.all()
                response_data = {
                    "status": True,
                    "data": [user.to_dict() for user in users],
                    "message": "Users retrieved successfully",
                }
                return jsonify(response_data)
            user = User.query.get_or_404(user_id)
            response_data = {
                "status": True,
                "data": user.to_dict(),
                "message": "User retrieved successfully",
            }
            return jsonify(response_data)
        except SQLAlchemyError as e:
            response_data = {"status": False, "error": str(e)}
            return Response(
                json.dumps(response_data), status=500, content_type="application/json"
            )
        except NotFound:
            response_data = {"status": False, "error": "User not found"}
            return Response(
                json.dumps(response_data), status=404, content_type="application/json"
            )

    def post(self):
        try:
            data = request.get_json()
            validation_result = validate_user_data(data)
            if not validation_result["status"]:
                return Response(
                    json.dumps(validation_result),
                    status=400,
                    content_type="application/json",
                )

            new_user = User(
                name=data["name"],
                username=data["username"],
                email=data["email"],
                password_hash=data["password_hash"],
            )
            db.session.add(new_user)
            db.session.commit()

            response_data = {
                "message": "User Created Successfully",
                "status": True,
                "data": new_user.to_dict(),
            }

            return Response(
                json.dumps(response_data), status=201, content_type="application/json"
            )

        except SQLAlchemyError as e:
            db.session.rollback()
            response_data = {"status": False, "error": str(e)}
            return Response(
                json.dumps(response_data), status=500, content_type="application/json"
            )

    def put(self, user_id):
        try:
            data = request.get_json()
            validation_result = validate_user_data(data)
            if not validation_result["status"]:
                return Response(
                    json.dumps(validation_result),
                    status=400,
                    content_type="application/json",
                )

            user = User.query.get_or_404(user_id)
            user.name = data["name"]
            user.username = data["username"]
            user.email = data["email"]
            user.password_hash = data["password_hash"]
            db.session.commit()

            response_data = {
                "status": True,
                "data": user.to_dict(),
                "message": "User updated successfully",
            }
            return Response(
                json.dumps(response_data), status=200, content_type="application/json"
            )

        except SQLAlchemyError as e:
            db.session.rollback()
            response_data = {"status": False, "error": str(e)}
            return Response(
                json.dumps(response_data), status=500, content_type="application/json"
            )
        except NotFound:
            response_data = {"status": False, "error": "User not found"}
            return Response(
                json.dumps(response_data), status=404, content_type="application/json"
            )

    def patch(self, user_id):
        try:
            data = request.get_json()
            user = User.query.get_or_404(user_id)

            if "name" in data:
                user.name = data["name"]
            if "username" in data:
                user.username = data["username"]
            if "email" in data:
                user.email = data["email"]
            if "password_hash" in data:
                user.password_hash = data["password_hash"]

            db.session.commit()

            response_data = {
                "status": True,
                "data": user.to_dict(),
                "message": "User updated successfully",
            }
            return Response(
                json.dumps(response_data), status=200, content_type="application/json"
            )

        except SQLAlchemyError as e:
            db.session.rollback()
            response_data = {"status": False, "error": str(e)}
            return Response(
                json.dumps(response_data), status=500, content_type="application/json"
            )
        except NotFound:
            response_data = {"status": False, "error": "User not found"}
            return Response(
                json.dumps(response_data), status=404, content_type="application/json"
            )

    def delete(self, user_id):
        try:
            user = User.query.get_or_404(user_id)
            db.session.delete(user)
            db.session.commit()

            response_data = {"status": True, "message": "User deleted successfully"}
            return Response(
                json.dumps(response_data), status=200, content_type="application/json"
            )

        except SQLAlchemyError as e:
            db.session.rollback()
            response_data = {"status": False, "error": str(e)}
            return Response(
                json.dumps(response_data), status=500, content_type="application/json"
            )
        except NotFound:
            response_data = {"status": False, "error": "User not found"}
            return Response(
                json.dumps(response_data), status=404, content_type="application/json"
            )


api.add_resource(UserAPI, "/users/", methods=["GET"])
api.add_resource(UserAPI, "/users/<int:user_id>/", methods=["GET"])
api.add_resource(UserAPI, "/users/post/", methods=["POST"])
api.add_resource(UserAPI, "/users/patch/", methods=["PATCH"])
api.add_resource(UserAPI, "/users/put/<int:user_id>/", methods=["PUT"])
api.add_resource(UserAPI, "/users/delete/<int:user_id>/", methods=["DELETE"])
