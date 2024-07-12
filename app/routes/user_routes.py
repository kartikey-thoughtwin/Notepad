from flask_restx import Resource
from flask import request, Blueprint, jsonify
from app import api, db
from app.models import User
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import NotFound
from app.utils.utils import validate_user_data, make_response

user_bp = Blueprint("user", __name__)


class UserAPI(Resource):
    """
    RESTful API for managing users.
    """

    def get(self, user_id=None):
        """
        GET method to retrieve either all users or a specific user by ID.

        Args:
            user_id (int, optional): ID of the user to retrieve. Defaults to None.

        Returns:
            Response: JSON response with status, message, and data.
        """
        try:
            if user_id is None:
                users = User.query.all()
                return make_response(
                    True,
                    message="Users retrieved successfully",
                    data=[user.to_dict() for user in users],
                )

            user = User.query.get_or_404(user_id)
            return make_response(
                True, message="User retrieved successfully", data=user.to_dict()
            )

        except SQLAlchemyError as e:
            return make_response(False, message=str(e), status_code=500)

        except NotFound:
            return make_response(False, message="User not found", status_code=404)

    def post(self):
        """
        POST method to create a new user.

        Returns:
            Response: JSON response containing status, message, and data.
        """
        try:
            data = request.get_json()
            validation_result = validate_user_data(data)
            if not validation_result["status"]:
                return make_response(
                    False, message=validation_result["message"], status_code=400
                )

            new_user = User(
                name=data["name"],
                username=data["username"],
                email=data["email"],
                password_hash=data["password_hash"],
            )
            db.session.add(new_user)
            db.session.commit()
            return make_response(
                True,
                message="User Created Successfully",
                data=new_user.to_dict(),
                status_code=201,
            )

        except SQLAlchemyError as e:
            db.session.rollback()
            return make_response(False, message=str(e), status_code=500)

    def put(self, user_id):
        """
        PUT method to update a user by ID.

        Args:
            user_id (int): ID of the user to update.

        Returns:
            Response: JSON response containing status, message, and data.
        """
        try:
            data = request.get_json()
            validation_result = validate_user_data(data)
            if not validation_result["status"]:
                return make_response(
                    False, message=validation_result["message"], status_code=400
                )

            user = User.query.get_or_404(user_id)
            user.name = data["name"]
            user.username = data["username"]
            user.email = data["email"]
            user.password_hash = data["password_hash"]
            db.session.commit()
            return make_response(
                True, message="User updated successfully", data=user.to_dict()
            )

        except SQLAlchemyError as e:
            db.session.rollback()
            return make_response(False, message=str(e), status_code=500)

        except NotFound:
            return make_response(False, message="User not found", status_code=404)

    def patch(self, user_id):
        """
        PATCH method Partially updates an existing user by `user_id`.

        Args:
            user_id (int): ID of the user to update.

        Returns:
            Response: JSON response containing status, message, and data.
        """
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
            return make_response(
                True, message="User updated successfully", data=user.to_dict()
            )

        except SQLAlchemyError as e:
            db.session.rollback()
            return make_response(False, message=str(e), status_code=500)

        except NotFound:
            return make_response(False, message="User not found", status_code=404)

    def delete(self, user_id):
        """
        DELETE method to delete a user by ID.

        Args:
            user_id (int): ID of the user to delete.

        Returns:
            Response: Empty response with HTTP status code 204 NO CONTENT.
        """
        try:
            user = User.query.get_or_404(user_id)
            db.session.delete(user)
            db.session.commit()
            return make_response(
                True, message="User deleted successfully", status_code=200
            )

        except SQLAlchemyError as e:
            db.session.rollback()
            return make_response(False, message=str(e), status_code=500)

        except NotFound:
            return make_response(False, message="User not found", status_code=404)


api.add_resource(UserAPI, "/users/list/", methods=["GET"])
api.add_resource(UserAPI, "/users/get/<int:user_id>/", methods=["GET"])
api.add_resource(UserAPI, "/users/post/", methods=["POST"])
api.add_resource(UserAPI, "/users/patch/<int:user_id>/", methods=["PATCH"])
api.add_resource(UserAPI, "/users/put/<int:user_id>/", methods=["PUT"])
api.add_resource(UserAPI, "/users/delete/<int:user_id>/", methods=["DELETE"])
