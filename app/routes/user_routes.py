from flask import Blueprint, request, jsonify, Response, make_response
from flask_restful import Resource, Api
from app import app, db
from flask_bcrypt import Bcrypt
from app.models.user import User
import re
from flask import request, Blueprint, Response, render_template
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token, set_access_cookies, set_refresh_cookies,
    jwt_required, get_jwt_identity, get_jwt,unset_jwt_cookies
)
from datetime import datetime, timezone
from flask_jwt_extended.exceptions import NoAuthorizationError, JWTDecodeError, RevokedTokenError
import json

user_bp = Blueprint('users', __name__)
api = Api(user_bp)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# A set to store revoked tokens (for demonstration purposes; use a more persistent storage in production)
revoked_tokens = set()

@user_bp.route("/register", methods=['GET','POST'])
def create():
    if request.method=='GET':
        return render_template("registration.html")
    if request.method == 'POST':
        obj = RegisterView()
        return obj.post()

def validate_user_data(data):
    # breakpoint()
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
            username = data['username']
            password = data['password']

            user = User.query.filter_by(username=username).first()
            if user and bcrypt.check_password_hash(user.password_hash, password):
                access_token = create_access_token(identity=user.id)
                refresh_token = create_refresh_token(identity=user.id)

                response = jsonify({'message': 'Login Success'})
                set_access_cookies(response, access_token)
                set_refresh_cookies(response, refresh_token)
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
            current_user = get_jwt_identity()
            access_token = create_access_token(identity=current_user)
            response = jsonify({'message': 'Token refreshed'})
            set_access_cookies(response, access_token)
            return response

        except Exception as e:
            return Response(json.dumps({'message': 'An error occurred', 'error': str(e)}), status=500, content_type="application/json")
        

class LogoutView(Resource):
    @jwt_required()
    def post(self):
        try:
            print("HERERE")
            jti = get_jwt()["jti"]
            revoked_tokens.add(jti)
            
            response = jsonify({"message": "Successfully logged out"})
            response.delete_cookie('access_token_cookie')
            response.delete_cookie('refresh_token_cookie')
            
            return response
            
        except Exception as e:
            return jsonify({'message': 'An error occurred', 'error': str(e)})
            
@app.errorhandler(NoAuthorizationError)
def handle_no_auth_error(e):
    return jsonify({'message': 'Token is missing'}), 401

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
api.add_resource(LoginView, "/login", methods=['POST'])
api.add_resource(TokenRefreshView, "/token/refresh", methods=['POST'])
api.add_resource(LogoutView, "/logout", methods=['POST'])
api.add_resource(HomeView,'/home',methods=['POST'])
