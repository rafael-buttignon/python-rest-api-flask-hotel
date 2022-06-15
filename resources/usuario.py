from venv import create
from flask_restful import Resource, reqparse
from blacklist import BLACKLIST
from models.usuario import UserModel
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from werkzeug.security import safe_str_cmp


atributos = reqparse.RequestParser()
atributos.add_argument('login', type=str, required=True, help='The field "login" cannot be left blank.')
atributos.add_argument('senha', type=str, required=True, help='The field "senha" cannot be left blank.')

class User(Resource):

    def get(self, user_id):
        user = UserModel.find_user(user_id)
        if user:
            return user.json()
        return {'message': 'user not found.'}, 404 

    @jwt_required()
    def delete(self, user_id):
        user = UserModel.find_user(user_id)
        if user:
            try:
                user.delete_user()
            except Exception:
                return {f'message': 'An error occurred deleting the user. Error: {e} '}, 500
            return {'message': 'User deleted.'}, 200
        return {'message': 'User not found.'}, 404

class UserRegister(Resource):
    def post(self):
        dados = atributos.parse_args()

        if UserModel.find_by_login(dados['login']):
            return {'message': 'User already exists.'}, 400

        user = UserModel(**dados)
        user.save_user()
        return {'User created'}, 201

class UserLogin(Resource):
    @classmethod
    def post(cls):
        dados = atributos.parse_args() 

        user = UserModel.find_by_login(dados['login'])

        if user and safe_str_cmp(user.senha, dados['senha']):
            token_de_acesso = create_access_token(identity=user.user_id)
            return {'access_token': token_de_acesso}, 200
        return {'message': 'The username or password is incorrect.'}, 401 # Unauthorized

class UserLogout(Resource):

    @jwt_required()
    def post(self):
        jwt_id = get_jwt()['jti'] # JWT Token Identifier
        BLACKLIST.add(jwt_id)
        return {'message': 'Successfully logged out.'}, 200
