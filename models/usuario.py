import email
from flask import request, url_for
from requests import post
import requests
from sql_alchemy import banco

MAILGUN_DOMAIN = 'sandboxc86bc6de256a46a39d6bd7075e136545.mailgun.org'
MAILGUN_API_KEY = '5fd0bdfdadac78424d7d766ba04b531c-77985560-8000aa8b'
FROM_TITLE = 'NO-REPLY - CONFIRMAÇÃO DE CRIAÇÃO DE CONTA'
FROM_EMAIL = 'iphotni49@hotmail.com'

class UserModel(banco.Model):
    __tablename__ = 'usuarios' # nome da tabela no banco de dados

    user_id = banco.Column(banco.Integer, primary_key=True)
    login = banco.Column(banco.String(40), nullable=False, unique=True)
    senha = banco.Column(banco.String(40), nullable=False)
    email = banco.Column(banco.String(80), nullable=False, unique=True)
    ativado = banco.Column(banco.Boolean, default=False)

    def __init__(self, login, senha, ativado, email):
        self.login = login
        self.senha = senha
        self.email = email
        self.ativado = ativado

    def json(self):
        return {
            'user_id': self.user_id,
            'login': self.login,
            'email': self.email,
            'ativado': self.ativado
        }

    def send_confirmation_email(self):
        link = request.url_root[:-1] + url_for('userconfirm', user_id=self.user_id) #  #https://127.0.0.01:5000/confirmacao/user_id'

        return post(f'https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages', 
                auth=('api', MAILGUN_API_KEY), 
                data={'from': '{} <{}>'.format(FROM_TITLE, FROM_EMAIL),
                    'To': self.email,
                    'subject': 'Confirmação de Cadastro',
                    'text': f'Por favor, confirme seu cadastro clicando no link a seguir: {link}',
                    'html': '<html><p>Confirme seu cadastro clicando no link a seguir: <a href="{}"> Confirmar EMAIL</a></p></html> '.format(link)})
    
                    
    @classmethod
    def find_user(cls, user_id):
        user = cls.query.filter_by(user_id=user_id).first()
        if user:
            return user
        return None

    @classmethod
    def find_by_login(cls, user_login):
        user = cls.query.filter_by(login=user_login).first()
        if user:
            return user
        return None

    @classmethod
    def find_by_email(cls, user_email):
        email = cls.query.filter_by(login=user_email).first()
        if email:
            return email
        return None
        
    def save_user(self):
        banco.session.add(self)
        banco.session.commit()

    def delete_user(self):
        banco.session.delete(self)
        banco.session.commit()
