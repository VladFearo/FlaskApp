from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, create_refresh_token, get_jwt_identity

from db import db
from models import UserModel, TokenBlocklistModel
from schemas import UserSchema


blp = Blueprint('Users', 'users', description='User related operations')

@blp.route('/register')
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        if UserModel.query.filter(UserModel.username == user_data['username']).first():
            abort(409, message='User already exists')
        
        user = UserModel(
            username=user_data['username'],
            password=pbkdf2_sha256.hash(user_data['password'])
        )
        db.session.add(user)
        db.session.commit()

        return {'message': 'User created successfully'}, 201
    

@blp.route('/login')
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(UserModel.username == user_data['username']).first()
        
        if user and pbkdf2_sha256.verify(user_data['password'], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)
            return {'access_token': access_token, 'refresh_token': refresh_token}, 200
        abort(401, message='Invalid username or password')

@blp.route('/refresh')
class UserRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        user_id = get_jwt_identity()
        access_token = create_access_token(identity=user_id, fresh=False)
        return {'access_token': access_token}, 200

@blp.route('/logout')
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        db.session.add(TokenBlocklistModel(jti=jti))
        db.session.commit()
        return {"message": "Successfully logged out"}, 200

@blp.route('/user/<int:user_id>')
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user
    
    @jwt_required()
    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {'message': 'User deleted successfully'}, 200