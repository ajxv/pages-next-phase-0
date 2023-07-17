from flask import Blueprint
from flask_restful import Api, Resource

api_bp = Blueprint('api_bp', __name__)
api = Api(api_bp)

class ProcessPages(Resource):
    def post(self):
        pass

class Pdf2Excel(Resource):
    def post(self):
        pass

class Status(Resource):
    def get(self, process_id):
        return {'id': process_id}

api.add_resource(ProcessPages, '/process_pages')
api.add_resource(Pdf2Excel, '/pdf_to_excel')
api.add_resource(Status, '/status/<int:process_id>')