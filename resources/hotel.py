import sqlite3
from flask_restful import Resource, reqparse
from requests import request
from models.hotel import HotelModel
from flask_jwt_extended import jwt_required
from models.site import SiteModel
from resources.filtros import normalize_path_params, consulta_sem_cidade, consulta_com_cidade

path_params = reqparse.RequestParser()
path_params.add_argument('cidade', type=str, required=False, help='Favor informar a cidade')
path_params.add_argument('estrelas_min', type=float, required=False, help='Favor informar a quantidade de estrelas')
path_params.add_argument('estrelas_max', type=float, required=False, help='Favor informar a quantidade de estrelas')
path_params.add_argument('diaria_min', type=float, required=False, help='Favor informar a quantidade de diaria')
path_params.add_argument('diaria_max', type=float, required=False, help='Favor informar a quantidade de diaria')
path_params.add_argument('limit', type=float, required=False, help='Favor informar a quantidade de limit')
path_params.add_argument('offset', type=float, required=False, help='Favor informar a quantidade de offset')


class Hoteis(Resource):
    def get(self):

        connection = sqlite3.connect('banco.db')
        cursor = connection.cursor()

        dados = path_params.parse_args()
        dados_validos = {chave:dados[chave] for chave in dados if dados[chave] is not None}
        parametros = normalize_path_params(**dados_validos)

        if not parametros.get('cidade'):
            tupla = tuple([parametros[chave] for chave in parametros])
            resultado = cursor.execute(consulta_sem_cidade, tupla)
        else:
            tupla = tuple([parametros[chave] for chave in parametros])
            resultado = cursor.execute(consulta_com_cidade, tupla)

        hoteis = []
        
        for linha in resultado:
            hoteis.append({
            'hotel_id': linha[0],
            'nome': linha[1],
            'estrelas': linha[2],
            'diaria': linha[3],
            'cidade': linha[4],
            'site_id': linha[5]
            })

        return {'hoteis': hoteis}

class Hotel(Resource):

    argumentos = reqparse.RequestParser()
    argumentos.add_argument('nome', type=str, required=True, help='The field "nome" cannot be left blank.') 
    argumentos.add_argument('estrelas', type=float, required=True, help='The field "estrelas" cannot be left blank.')
    argumentos.add_argument('diaria')
    argumentos.add_argument('cidade')
    argumentos.add_argument('site_id', type=int, required=True, help="Every hotel needs to be linked with site")


    def get(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            return hotel.json()
        return {'message': 'Hotel not found.'}, 404 

    @jwt_required()
    def post(self, hotel_id):
        if HotelModel.find_hotel(hotel_id):
            return {f'message': 'Hotel id {} already exists.'.format(hotel_id)}, 400 # Bad Requests

        dados = Hotel.argumentos.parse_args()
        hotel = HotelModel(hotel_id, **dados)

        if not SiteModel.find_by_id(dados.get('site_id')):
            return {'message': 'The hotel must be associated to a valid site id!'}, 400
        
        try:
            hotel.save_hotel()
        except Exception as e:
            return {f'message': 'An error occurred inserting the hotel. Error: {e} '}, 500 # Internal Server Error
        return hotel.json()

    @jwt_required()
    def put(self, hotel_id):
        dados = Hotel.argumentos.parse_args()
        hotel = HotelModel.find_hotel(hotel_id)

        if hotel:
            hotel.update_hotel(**dados)
            hotel.save_hotel()
            return hotel.json(), 200
        hotel = HotelModel(hotel_id, **dados)
        
        try:
            hotel.save_hotel()
        except Exception as e:
            return {f'message': 'An error occurred inserting the hotel. Error: {e} '}, 500 # Internal Server Error
        return hotel.json()

    @jwt_required()
    def delete(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            try:
                hotel.delete_hotel()
            except Exception as e:
                return {f'message': 'An error occurred deleting the hotel. Error: {e} '}, 500
            return {'message': 'Hotel deleted.'}, 200
        return {'message': 'Hotel not found.'}, 404