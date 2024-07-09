from flask import Blueprint, request, jsonify
from app.models.note import Note
from app import db
from datetime import datetime
from app.schemas import NoteSchema
from pydantic import ValidationError

note_bp = Blueprint('notes', __name__)

@note_bp.route('/notes', methods=['GET'])
def get_notes():
    notes = Note.query.all()
    return jsonify([NoteSchema.from_orm(note).dict() for note in notes])

@note_bp.route('/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    note = Note.query.get_or_404(note_id)
    return jsonify(NoteSchema.from_orm(note).dict())

@note_bp.route('/notes', methods=['POST'])
def create_note():
    try:
        data = request.get_json()
        note_data = NoteSchema(**data)
    except ValidationError as e:
        return jsonify(e.errors()), 400


    new_note = Note(
        title=note_data.title,
        content=note_data.content,
        user_id=note_data.user_id,
        category_id=note_data.category_id
    )
    db.session.add(new_note)
    db.session.commit()
    return jsonify(NoteSchema.from_orm(new_note).dict()), 201

@note_bp.route('/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
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

@note_bp.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    return '', 204

