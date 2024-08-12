from curses import meta
from datetime import date, datetime
from flask_restx import Resource
from flask import request, Blueprint, Response, render_template, redirect, url_for
from app import api, db
from app.models import Note, Category, User
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import NotFound
import json
from app.utils.utils import validate_note_data, make_response
from sqlalchemy import func, and_
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, create_access_token, set_access_cookies,verify_jwt_in_request

note_bp = Blueprint("notes", __name__)



@note_bp.route("/home", methods=["GET"])
def home():
    try:
        
        try:
            verify_jwt_in_request()
        except Exception as e:
            try:
                jwt_data = get_jwt()
                current_user_id = get_jwt_identity()

                if jwt_data.get('type') == 'refresh':
                    # Create a new access token
                    new_access_token = create_access_token(identity=current_user_id)

                    # Create a response with the home page
                    response = redirect(url_for('notes.home'))
                    set_access_cookies(response, new_access_token)
                    return response
            except Exception as e:
                return redirect(url_for('users.login'))
            
        current_user_id = get_jwt_identity()

        # Check if the token is valid or expired
        jwt_data = get_jwt()

        # Case 1: User is authorized, proceed to home page
        if current_user_id:
            user = User.query.get(current_user_id)

            if not user:
                # Redirect to login page if user not found (though unlikely)
                return redirect(url_for('users.login'))

            notes = Note.query.filter_by(user_id=current_user_id).all()
            categories = Category.query.all()

            context = {
                "notes": [note.to_dict() for note in notes],
                "categories": [category.to_dict() for category in categories],
                "user":user.name,
                "user_email":user.email,
                "username":user.username
            }
            return render_template("imports/index.html", context=context)

        # Case 3: Both tokens are expired, redirect to login page
        return redirect(url_for('users.login'))

    except SQLAlchemyError as e:
        return redirect(url_for('users.login'))
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return redirect(url_for('users.login'))



class NotesAPI(Resource):


    """
    RESTful API for managing notes.
    """
    
    @jwt_required()
    def get(self, note_id=None):
        """
        GET method to retrieve either all notes or a specific note by ID.

        Returns:
            Response: JSON response with status, message, and data.
        """
        try:
            current_user_id = get_jwt_identity()
            if note_id:
                note = Note.query.filter_by(id=note_id, user_id=current_user_id).first()
                if not note:
                    return make_response(False, message="Note not found", status_code=404)
                return make_response(
                    True,
                    message="Note Retrieved Successfully",
                    data=note.to_dict(),
                )
            else:
                notes = Note.query.filter_by(user_id=current_user_id).all()
                return make_response(
                    True,
                    message="Notes Retrieved Successfully",
                    data=[note.to_dict() for note in notes],
                )

        except SQLAlchemyError as e:
            return make_response(False, message=str(e), status_code=500)

    @jwt_required()
    def post(self):
        """
        POST method to create a new note. This method is JWT protected.

        Returns:
            Response: JSON response containing status, message, and data.
        """
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()
            validation_result = validate_note_data(data)
            if not validation_result["status"]:
                return make_response(
                    False, message=validation_result["message"], status_code=400
                )

            new_note = Note(
                title=data["title"],
                content=data["content"],
                user_id=current_user_id,
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

    @jwt_required()
    def patch(self, note_id):
        """
        PATCH method Partially updates an existing note by `note_id`.

        Returns:
            Response: JSON response containing status, message, and data.
        """
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()
            try:
                note = Note.query.filter_by(id=note_id, user_id=current_user_id).first()
                if not note:
                    return make_response(False, message="Note not found", status_code=404)
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

    @jwt_required()
    def put(self, note_id):
        """
        PUT method to update a note by `note_id`.

        Returns:
            Response: JSON response containing status, message, and data.
        """
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()
            validation_result = validate_note_data(data)
            if not validation_result["status"]:
                return make_response(
                    False, message=validation_result["message"], status_code=400
                )

            try:
                note = Note.query.filter_by(id=note_id, user_id=current_user_id).first()
                if not note:
                    return make_response(False, message="Note not found", status_code=404)
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

    @jwt_required()
    def delete(self, note_id):
        """
        DELETE method to delete a note by ID.

        Returns:
            Response: Empty response with HTTP status code 204 NO CONTENT.
        """
        try:
            current_user_id = get_jwt_identity()
            try:
                note = Note.query.filter_by(id=note_id, user_id=current_user_id).first()
                db.session.delete(note)
                db.session.commit()
                return Response("", status=204)
            except NotFound:
                return make_response(False, message="Note not found", status_code=404)

        except SQLAlchemyError as e:
            db.session.rollback()
            return make_response(False, message=str(e), status_code=500)                            



class FilterNotesAPI(Resource):
    """
        GET method to retrieve notes based on filters.

        Returns:
            Response: JSON response containing the status, message, and data.

        Description:
            - If 'title' is provided in the request data, the method searches for notes with the specified title (case-insensitive).
            - If 'created_at' is provided in the request data, the method retrieves notes created on the specified date.
            - If 'category_id' is provided in the request data, the method fetches notes associated with the specified category ID.
            - If none of the above filters are provided, it returns a response indicating that no notes were found.

        Response:
            - On success, returns a response with a list of notes matching the filter criteria.
            - On failure, returns a response indicating that no notes were found.
    """

    def get(self):
        # breakpoint()
        data = request.args  # validate  params 
        title = data.get("title", None)
        date = data.get("created_at", None)
        category = data.get("category_name", None)

        if 'title' in data and 'created_at' in data and 'category_name' in data: 
                # breakpoint()
                cat = Category.query.filter_by(name=category).first()
                note_data = Note.query.filter(Note.title == title, Note.category == cat, func.date(Note.created_at)==date).all()
                if note_data != []:
                    print(func.date(Note.created_at))
                    return make_response(
                    True,
                    message="Notes Retrieved Successfully",
                    data=[note.to_dict() for note in note_data], 
                    )
                else:
                    return make_response(False, message="Note not found", status_code=404, data=[])
                
        if 'title' in data:
            title_data = str(title)
            note = Note.query.filter(Note.title.ilike(f'%{title_data}%')).all()
            if not note:
                return make_response(False, message="Note not found", status_code=404)
            return make_response(
                    True,
                    message="Notes Retrieved Successfully",
                    data=[note.to_dict() for note in note],
             )
        elif 'created_at' in data:
            if date:
                try:
                    date = datetime.strptime(date, '%Y-%m-%d').date()
                except ValueError:
                    return {"status": False, "message": "Invalid date format. Use YYYY-MM-DD."}
            note = Note.query.filter(func.date(Note.created_at) == date).order_by(Note.created_at.desc())
            if not note:
                return make_response(False, message="Note not found", status_code=404)
            return make_response(
                    True,
                    message="Notes Retrieved Successfully",
                    data=[note.to_dict() for note in note]
                )
        elif 'category_name' in data:
                # category = data.get("category_name")
                cat = Category.query.filter_by(name=category)
                ans = None
                for i in cat:
                    ans = i.id
                note = Note.query.filter_by(category_id=ans).all() 
                return make_response(
                    True,
                    message="Notes Retrieved Successfully",
                    data=[note.to_dict() for note in note], 
                )

            
        else:
            # if there is no filter recieved return all the notes
            notes = Note.query.all()
            return make_response(
                    True,
                    message="Notes Retrieved Successfully",
                    data=[note.to_dict() for note in notes],
                    )
    


api.add_resource(NotesAPI, "/notes/list/", methods=["GET"])
api.add_resource(NotesAPI, "/notes/get/<int:note_id>/", methods=["GET"])
api.add_resource(NotesAPI, "/notes/post/", methods=["POST"])
api.add_resource(NotesAPI, "/notes/put/<int:note_id>/", methods=["PUT"])
api.add_resource(NotesAPI, "/notes/delete/<int:note_id>/", methods=["DELETE"])
api.add_resource(NotesAPI, "/notes/patch/<int:note_id>/", methods=["PATCH"])
api.add_resource(FilterNotesAPI, "/notes/filter/", methods=["GET"])

