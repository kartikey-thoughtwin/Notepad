from flask import Blueprint, request, jsonify, Response, make_response, redirect, url_for, render_template
from flask_restful import Resource, Api
from app import app, db
from flask_bcrypt import Bcrypt
from app.models.user import User
from app.models.note import Note
from app.models.category import Category
import re
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token, set_access_cookies, decode_token,
    jwt_required, get_jwt_identity, get_jwt, unset_jwt_cookies, verify_jwt_in_request, exceptions as jwt_exceptions
)
import json
from datetime import datetime
import pytz

user_bp = Blueprint('users', __name__)


api = Api(user_bp)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# A set to store revoked tokens (for demonstration purposes; use a more persistent storage in production)
revoked_tokens = set()


@user_bp.route("/login", methods=['GET'])
def login():
    return render_template("login.html")

    

@user_bp.route("/register", methods=['GET', 'POST'])
@jwt_required(optional=True)  # Allow access without requiring a valid token
def create():
    try:
        # Attempt to verify JWT token
        verify_jwt_in_request(optional=True)
        if get_jwt_identity():
            # If the user is authenticated, redirect to home
            return redirect(url_for('notes.home'))
    except jwt_exceptions.NoAuthorizationError:
        # No token or missing token - allow access to the registration page
        pass
    except jwt_exceptions.ExpiredSignatureError:
        # Expired token - allow access to the registration page
        pass
    except Exception as e:
        # Other unexpected exceptions
        print(e)
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

    # If the request method is GET, show the registration page
    if request.method == 'GET':
        return render_template("registration.html")
    
    # If the request method is POST, process the registration form
    if request.method == 'POST':
        obj = RegisterView()
        return obj.post()



def validate_user_data(data):
    email = data.get("email")
    username = data.get("username", None)
    name = data.get("name", None)
    password = data.get("password_hash", None)

    if name is None or str(name).strip() == "" or name != str(name):
        return {'Error': 'Please enter a valid name'}

    if User.query.filter_by(username=username).first():
        return {'Error': 'Username already exists.'}
    
    if email == '':
        return {'Error': 'Please enter Email'}
    
    if password == '':
        return {'Error': 'Please enter Password'}
    
    if username == '':
        return {'Error': 'Please enter Username'}
    
    if len(str(username)) <= 4 or str(username).strip() == "" or username is None or username != str(username):
        return {'Error': 'Username must contain at least 5 characters'}
    
    if User.query.filter_by(email=email).first():
        return {'Error': 'Email already present'}
    
    if email is None:
        return {'Error': 'Please enter your email'}

    if password is None or len(password) < 8:
        return {'Error': 'Password must be at least 8 characters long'}

    return None

class RegisterView(Resource):
    def post(self):
        try:
            data = request.get_json()
            validation_error = validate_user_data(data)
            if validation_error:
                return Response(json.dumps({'error': validation_error}), status=400, content_type="application/json")
            user = User(
                name=data['name'],
                username=data['username'],
                email=data['email'],
                password_hash=bcrypt.generate_password_hash(
                    data['password_hash']).decode('utf-8')
            )
            db.session.add(user)
            db.session.commit()

            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            
            return jsonify({'message': 'User created', 'access_token': access_token, 'refresh_token': refresh_token})

        except Exception as e:
            return Response(json.dumps({'message': 'An error occurred', 'error': str(e)}), status=500, content_type="application/json")

class LoginView(Resource):
    def post(self):
        try:
            data = request.get_json()
            username = data.get('username', None)
            password = data.get('password', None)

            user = User.query.filter_by(username=username).first()

            if user and bcrypt.check_password_hash(user.password_hash, password):
                access_token = create_access_token(identity=user.id)
                refresh_token = create_refresh_token(identity=user.id)

                response = jsonify({'success': True, 'message': 'Login Success'})

                # Set domain to None so it works on localhost and IP
                domain = request.host.split(':')[0]  # Extract domain from request host

                response.set_cookie('access_token_cookie', access_token, httponly=True, secure=False, samesite='Lax', domain=domain)
                response.set_cookie('refresh_token_cookie', refresh_token, httponly=True, secure=False, samesite='Lax', domain=domain)

                return response
            else:
                return jsonify({'message': 'Login failed'})

        except Exception as e:
            print(e)
            return jsonify({'message': f'Missing field: {str(e)}'})
        
        
class TokenRefreshView(Resource):
    @jwt_required(refresh=True)
    def post(self):
        try:

            '''By this post method passing a refresh token,
               User will get new access token'''
            
            jwt_data = get_jwt()
        
            if jwt_data.get('type') == 'refresh':
            
                current_user = get_jwt_identity()
                access_token = create_access_token(identity=current_user)
                response = jsonify({'status':200,'success': True,'message': 'Token refreshed'})
                set_access_cookies(response, access_token)
                return response
            
            return jsonify({"success":False, "message": "Invalid token type"}), 401

        except Exception as e:
            return Response(json.dumps({'message': 'An error occurred', 'error': str(e)}), status=500, content_type="application/json")
        

class LogoutView(Resource):
    def post(self):
        try:
            # jti = get_jwt()["jti"]
            # revoked_tokens.add(jti)
            
            response = jsonify({'status':200,'success': True, "message": "Successfully logged out"})
            unset_jwt_cookies(response)
            response.delete_cookie('access_token_cookie')
            response.delete_cookie('refresh_token_cookie')
            
            return response
            
        except Exception as e:
            return jsonify({'message': 'An error occurred', 'error': str(e)})
            
# @app.errorhandler(NoAuthorizationError)
# def handle_no_auth_error(e):
#     return jsonify({'message': 'Token is missing'}), 401

class HomeView(Resource):
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        if current_user:
            return Response(json.dumps({'message': 'Home View'}), status=200, content_type="application/json")
        else:
            return Response(json.dumps({'message': 'user not found'}), status=404, content_type="application/json")


# Revocation checking function
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return jti in revoked_tokens

# Define the API resource routes
api.add_resource(RegisterView, "/register", methods=['POST'])
api.add_resource(LoginView, "/token/auth", methods=['POST'])
api.add_resource(TokenRefreshView, "/token/refresh", methods=['POST'])
api.add_resource(LogoutView, "/logout", methods=['POST'])
api.add_resource(HomeView,'/home',methods=['POST'])
