from flask_restx import Resource
from flask import request, Blueprint, Response
from app import api, db
from app.models import Note
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import NotFound
import json
from app.utils.utils import validate_note_data, make_response

note_bp = Blueprint("notes", __name__)


class NotesAPI(Resource):
    """
    RESTful API for managing notes.
    """

    def get(self, note_id=None):
        """
        GET method to retrieve either all notes or a specific note by ID.

        Args:
            note_id (int, optional): ID of the note to retrieve. Defaults to None.

        Returns:
            Response: JSON response with status, message, and data.
        """
        try:
            if note_id is None:
                notes = Note.query.all()

                return make_response(
                    True,
                    message="Notes Retrieved Successfully",
                    data=[note.to_dict() for note in notes],
                )

            try:
                note = Note.query.get_or_404(note_id)
                return make_response(
                    True, message="Note Retrieved Successfully", data=note.to_dict()
                )

            except NotFound:
                return make_response(False, message="Note not found", status_code=404)

        except SQLAlchemyError as e:
            return make_response(False, message=str(e), status_code=500)

    def post(self):
        """
        POST method to create a new note.

        Returns:
            Response: JSON response containing status, message, and data.
        """
        try:
            data = request.get_json()
            validation_result = validate_note_data(data)
            if not validation_result["status"]:
                return make_response(
                    False, message=validation_result["message"], status_code=400
                )

            new_note = Note(
                title=data["title"],
                content=data["content"],
                user_id=data["user_id"],
                category_id=data["category_id"],
            )
            db.session.add(new_note)
            db.session.commit()
            return make_response(
                True,
                message="Note Created Successfully",
                data=new_note.to_dict(),
                status_code=201,
            )

        except SQLAlchemyError as e:
            db.session.rollback()
            response_data = {"status": False, "error": str(e)}
            return Response(
                json.dumps(response_data), status=500, content_type="application/json"
            )

    def patch(self, note_id):
        """
        PATCH method Partially updates an existing note by `note_id`.

        Args:
            note_id (int): ID of the note to update.

        Returns:
            Response: JSON response containing status, message, and data.
        """
        try:
            data = request.get_json()
            try:
                note = Note.query.get_or_404(note_id)
                if "title" in data:
                    note.title = data["title"]
                if "content" in data:
                    note.content = data["content"]
                if "user_id" in data:
                    note.user_id = data["user_id"]
                if "category_id" in data:
                    note.category_id = data["category_id"]
                db.session.commit()
                return make_response(
                    True, message="Note Updated Successfully", data=note.to_dict()
                )

            except NotFound:
                return make_response(False, message="Note not found", status_code=404)

        except SQLAlchemyError as e:
            db.session.rollback()
            return make_response(False, message=str(e), status_code=500)

    def put(self, note_id):
        """
        PUT method to update a note by ID.

        Args:
            note_id (int): ID of the note to update.

        Returns:
            Response: JSON response containing status, message, and data.
        """
        try:
            data = request.get_json()
            validation_result = validate_note_data(data)
            if not validation_result["status"]:
                return make_response(
                    False, message=validation_result["message"], status_code=400
                )

            try:
                note = Note.query.get_or_404(note_id)
                note.title = data["title"]
                note.content = data["content"]
                note.user_id = data["user_id"]
                note.category_id = data["category_id"]
                db.session.commit()
                return make_response(
                    True, message="Note Updated Successfully", data=note.to_dict()
                )

            except NotFound:
                return make_response(False, message="Note not found", status_code=404)

        except SQLAlchemyError as e:
            db.session.rollback()
            return make_response(False, message=str(e), status_code=500)

    def delete(self, note_id):
        """
        DELETE method to delete a note by ID.

        Args:
            note_id (int): ID of the note to delete.

        Returns:
            Response: Empty response with HTTP status code 204 NO CONTENT.
        """
        try:
            try:
                note = Note.query.get_or_404(note_id)
                db.session.delete(note)
                db.session.commit()
                return Response("", status=204)
            except NotFound:
                return make_response(False, message="Note not found", status_code=404)

        except SQLAlchemyError as e:
            db.session.rollback()
            return make_response(False, message=str(e), status_code=500)


api.add_resource(NotesAPI, "/notes/list/", methods=["GET"])
api.add_resource(NotesAPI, "/notes/get/<int:note_id>/", methods=["GET"])
api.add_resource(NotesAPI, "/notes/post/", methods=["POST"])
api.add_resource(NotesAPI, "/notes/put/<int:note_id>/", methods=["PUT"])
api.add_resource(NotesAPI, "/notes/delete/<int:note_id>/", methods=["DELETE"])
api.add_resource(NotesAPI, "/notes/patch/<int:note_id>/", methods=["PATCH"])
