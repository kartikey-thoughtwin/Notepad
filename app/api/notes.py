from flask_restx import Resource
from flask import request, jsonify
from app import api, db
from app.models import Note
from app.schemas import NoteSchema
from pydantic import ValidationError


class NotesAPI(Resource):

    # def list(self, note_id=None):
    #     if note_id is None:
    #         notes = Note.query.all()
    #         # return jsonify([NoteSchema.from_orm(note).dict() for note in notes])
    #         return jsonify([NoteSchema.model_validate(note) for note in notes])
    #     note = Note.query.get_or_404(note_id)
    #     return jsonify(NoteSchema.from_orm(note).dict())

    def get(self, note_id=None):
        if note_id is None:
            notes = Note.query.all()
            # return jsonify([NoteSchema.from_orm(note).dict() for note in notes])
            return jsonify([NoteSchema.model_validate(note) for note in notes])
        note = Note.query.get_or_404(note_id)
        return jsonify(NoteSchema.model_validate(note))

    def post(self):
        try:
            data = request.get_json()
            note_data = NoteSchema(**data)
        except ValidationError as e:
            return jsonify(e.errors()), 400

        new_note = Note(
            title=note_data.title,
            content=note_data.content,
            user_id=note_data.user_id,
            category_id=note_data.category_id,
        )
        db.session.add(new_note)
        db.session.commit()
        return jsonify(NoteSchema.from_orm(new_note).dict()), 201

    def put(self, note_id):
        try:
            data = request.get_json()
            note_data = NoteSchema(**data)
        except ValidationError as e:
            return jsonify(e.errors()), 400

        note = Note.query.get_or_404(note_id)
        note.title = note_data.title
        note.content = note_data.content
        note.user_id = note_data.user_id
        note.category_id = note_data.category_id
        db.session.commit()
        return jsonify(NoteSchema.from_orm(note).dict())

    def delete(self, note_id):
        note = Note.query.get_or_404(note_id)
        db.session.delete(note)
        db.session.commit()
        return "", 204


api.add_resource(NotesAPI, "/get/<int:note_id>/", methods=["GET"])
api.add_resource(NotesAPI, "/post", methods=["POST"])
api.add_resource(NotesAPI, "/put/<int:note_id>/", methods=["PUT"])
api.add_resource(NotesAPI, "/delete/<int:note_id>/", methods=["DELETE"])
