from flask_restful import Resource, Api
from app import app
from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt 
from app.models.user import User
import re
from app import db
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt

user_bp = Blueprint('users',__name__)
api = Api(user_bp)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)


def validate_user_data(data):
    email = data.get("email")
    username = data.get("username", None)
    name = data.get("name", None)
    password = data.get("password_hash", None)
    
    if name is None or str(name).strip() == "" or name != str(name):
        return {'Error': 'Please enter a valid name'}
    
    if User.query.filter_by(username=username).first() or len(str(username)) <= 4 or str(username).strip() == "" or username is None or username != str(username):
        return {'Error': 'Username is already present or username must contain at least 5 characters'}
    
    if User.query.filter_by(email=email).first():
        return {'Error': 'Email is already present'}
    
    if email is None:
        return {'Error': 'Please enter your email'}
    
    regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
    if not re.fullmatch(regex, email):
        return {'Error': 'Please enter a valid email'}
    
    if password is None or len(password) < 8:
        return {'Error': 'Password must be at least 8 characters long'}

    return None 


class Hello(Resource):
      def post(self):
        data = request.get_json()
        validation_error = validate_user_data(data)
        if validation_error:
            return jsonify(validation_error)
    
        user = User(
            name=data['name'],
            username=data['username'],
            email=data['email'],
            password_hash=bcrypt.generate_password_hash(data['password_hash']).decode('utf-8')
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({'data': 'User is created'})


class LoginView(Resource):
        def post(self):
            data = request.get_json()
            username = data['username']
            password = data['password_hash']
            print('Received data:', username , password)

            user = User.query.filter_by(username=username).first()

            if user and bcrypt.check_password_hash(user.password_hash, password):
                access_token = create_access_token(identity=user.id)
                return jsonify({'message': 'Login Success', 'access_token': access_token})
            else:
                return jsonify({'message': 'Login Failed'}), 401


api.add_resource(Hello,"/", methods=['POST'])
api.add_resource(LoginView,"/login",methods=['POST'])