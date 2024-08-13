import json
from flask import Response


def validate_data(data):
    if not data:
        return {"status": False, "message": "Enter JSON data"}
    elif not isinstance(data, dict):
        return {"status": False, "message": "Invalid JSON data"}
    elif data.get("name") == "":
        return {"status": False, "message": "Enter the name."}
    else:
        return {"status": True, "data": data}




def validate_note_data(data):
    if not data:
        return {"status": False, "message": "Enter JSON data"}
    elif not isinstance(data, dict):
        return {"status": False, "message": "Invalid JSON data"}
    elif "title" not in data or data.get("title") == "":
        return {"status": False, "message": "Enter the title."}
    # elif "content" not in data or data.get("content") == "":
    #     return {"status": False, "message": "Enter the content."}
    # elif "user_id" not in data or data.get("user_id") == "":
    #     return {"status": False, "message": "Enter the user_id."}
    elif "category_id" not in data or data.get("category_id") == "":
        return {"status": False, "message": "Enter the category_id."}
    else:
        return {"status": True, "data": data}


def validate_user_data(data):
    if not data:
        return {"status": False, "message": "Enter JSON data"}
    elif not isinstance(data, dict):
        return {"status": False, "message": "Invalid JSON data"}
    elif not all(key in data for key in ["name", "username", "email", "password_hash"]):
        return {"status": False, "message": "Missing required fields"}
    elif data["name"] == "":
        return {"status": False, "message": "Enter the name"}
    elif data["username"] == "":
        return {"status": False, "message": "Enter the username"}
    elif data["email"] == "":
        return {"status": False, "message": "Enter the email"}
    elif data["password_hash"] == "":
        return {"status": False, "message": "Enter the password_hash"}
    else:
        return {"status": True, "data": data}


def make_response(status, message=None, data=None, status_code=200):
    response_data = {"status": status, "message": message, "data": data}
    return Response(
        json.dumps(response_data), status=status_code, content_type="application/json"
    )
