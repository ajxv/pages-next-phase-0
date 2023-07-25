import os
from flask import Blueprint, current_app, request, Response, send_file
from flask_restful import Api, Resource
from werkzeug.utils import secure_filename

from service.process_pdf import *

api_bp = Blueprint('api_bp', __name__)
api = Api(api_bp)

class ProcessPages(Resource):
    def post(self):
        file = request.files['input_file']
        search_terms = list(map(str.strip, request.form['search_key'].split(',')))
        # Save the uploaded PDF file
        input_pdf = os.path.join(current_app.root_path, f"uploads{os.path.sep}{secure_filename(file.filename)}")
        file.save(input_pdf)

        # find pdf type
        pdf_type = get_pdf_type(input_pdf)
        if pdf_type:
            if pdf_type == "epf":
                output_pdf = process_pdf_epf(input_pdf, search_terms)
            elif pdf_type == "esic":
                output_pdf = process_pdf_esic(input_pdf, search_terms)
        else:
            return {'error': 'could not identify pdf type'}

        # Return the modified PDF as a response
        return Response(output_pdf, mimetype="application/pdf", headers={"Content-Disposition": f"attachment; filename={file.filename.replace('.pdf', '')}-processed.pdf"})


class Pdf2Excel(Resource):
    def post(self):
        # Get the uploaded PDF file and search term from the form
        file = request.files['input_file']

        # Save the uploaded PDF file
        input_pdf = os.path.join(current_app.root_path, f"uploads{os.path.sep}{secure_filename(file.filename)}")
        file.save(input_pdf)

        # find pdf type
        pdf_type = get_pdf_type(input_pdf)
        if pdf_type:
            out_file = pdf_to_excel(input_pdf, pdf_type)    
        else:
            return {'error': 'could not identify pdf type'}

        # Return the modified PDF as a response
        return send_file(out_file, mimetype="application/pdfapplication/vnd.openxmlformats-officedocument.spreadsheetml.sheet", download_name=out_file)


class Status(Resource):
    def get(self, process_id):
        return {'id': process_id}

api.add_resource(ProcessPages, '/process_pages')
api.add_resource(Pdf2Excel, '/pdf_to_excel')
api.add_resource(Status, '/status/<int:process_id>')