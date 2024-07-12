from flask_restx import Resource
from flask import request, Blueprint, Response, render_template
from app import api, db
from app.models import Note, Category
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import NotFound
import json
from app.utils.utils import validate_note_data

note_bp = Blueprint("notes", __name__)


@note_bp.route("/home", methods=["GET"])
def home():
    try:
        notes = Note.query.all()
        categories = Category.query.all()
        context = {
            "notes": [note.to_dict() for note in notes],
            "categories": [category.to_dict() for category in categories],
        }
        return render_template("base.html", context=context)
    except SQLAlchemyError as e:
        return render_template("base.html", error=str(e))


class NotesAPI(Resource):

    def get(self, note_id=None):
        try:
            if note_id is None:
                notes = Note.query.all()
                response_data = {
                    "status": True,
                    "data": [note.to_dict() for note in notes],
                }
                return Response(
                    json.dumps(response_data),
                    status=200,
                    content_type="application/json",
                )
            try:
                note = Note.query.get_or_404(note_id)
                response_data = {"status": True, "data": note.to_dict()}
                return Response(
                    json.dumps(response_data),
                    status=200,
                    content_type="application/json",
                )
            except NotFound:
                response_data = {"status": False, "error": "Note not found"}
                return Response(
                    json.dumps(response_data),
                    status=404,
                    content_type="application/json",
                )
        except SQLAlchemyError as e:
            response_data = {"status": False, "error": str(e)}
            return Response(
                json.dumps(response_data), status=500, content_type="application/json"
            )

    def post(self):
        try:
            data = request.get_json()
            validation_result = validate_note_data(data)
            if not validation_result["status"]:
                return Response(
                    json.dumps(validation_result),
                    status=400,
                    content_type="application/json",
                )

            new_note = Note(
                title=data["title"],
                content=data["content"],
                user_id=data["user_id"],
                category_id=data["category_id"],
            )
            db.session.add(new_note)
            db.session.commit()

            # print(">>>>>>>>>>>>>...",new_note.__dict__)

            response_data = {
                "message": "Note Created Successfully",
                "status": True,
                "data": new_note.to_dict(),
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

    def put(self, note_id):
        try:
            data = request.get_json()
            validation_result = validate_note_data(data)
            if not validation_result["status"]:
                return Response(
                    json.dumps(validation_result),
                    status=400,
                    content_type="application/json",
                )
            try:
                note = Note.query.get_or_404(note_id)
                note.title = data["title"]
                note.content = data["content"]
                note.user_id = data["user_id"]
                note.category_id = data["category_id"]
                db.session.commit()

                response_data = {"status": True, "data": note.to_dict()}
                return Response(
                    json.dumps(response_data),
                    status=200,
                    content_type="application/json",
                )
            except NotFound:
                response_data = {"status": False, "error": "Note not found"}
                return Response(
                    json.dumps(response_data),
                    status=404,
                    content_type="application/json",
                )
        except SQLAlchemyError as e:
            db.session.rollback()
            response_data = {"status": False, "error": str(e)}
            return Response(
                json.dumps(response_data), status=500, content_type="application/json"
            )

    def delete(self, note_id):
        try:
            try:
                note = Note.query.get_or_404(note_id)
                db.session.delete(note)
                db.session.commit()
                return Response("", status=204)
            except NotFound:
                response_data = {"status": False, "error": "Note not found"}
                return Response(
                    json.dumps(response_data),
                    status=404,
                    content_type="application/json",
                )
        except SQLAlchemyError as e:
            db.session.rollback()
            response_data = {"status": False, "error": str(e)}
            return Response(
                json.dumps(response_data), status=500, content_type="application/json"
            )


api.add_resource(NotesAPI, "/notes/", methods=["GET"])
api.add_resource(NotesAPI, "/notes/<int:note_id>/", methods=["GET"])
api.add_resource(NotesAPI, "/notes/post/", methods=["POST"])
api.add_resource(NotesAPI, "/notes/put/<int:note_id>/", methods=["PUT"])
api.add_resource(NotesAPI, "/notes/delete/<int:note_id>/", methods=["DELETE"])
