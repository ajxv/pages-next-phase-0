from flask import Flask, Response, current_app, send_file
from flask import render_template, request
from werkzeug.utils import secure_filename
import os
from api.api import api_bp
from service.process_pdf import *

app = Flask(__name__)

# register api bleprint
app.register_blueprint(api_bp, url_prefix='/api')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/process_pages", methods=['POST', 'GET'])
def process_pages():

    if request.method == "POST":
        # Get the uploaded PDF file and search term from the form
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

    return render_template("process_pages.html")

@app.route("/pdf2excel", methods=['POST', 'GET'])
def pdf2excel():
    if request.method == "POST":
    
        # Get the uploaded PDF file and search term from the form
        file = request.files['input_file']

        # Save the uploaded PDF file
        input_pdf = os.path.join(current_app.root_path, f"uploads{os.path.sep}{secure_filename(file.filename)}")
        file.save(input_pdf)

        # find pdf type
        pdf_type = get_pdf_type(input_pdf)
        if pdf_type:
            out_file = pdf_to_excel(input_pdf)    
        else:
            return {'error': 'could not identify pdf type'}

        # Return the modified PDF as a response
        return send_file(out_file, mimetype="application/pdfapplication/vnd.openxmlformats-officedocument.spreadsheetml.sheet", download_name=out_file)

    return render_template("pdf2excel.html")

if __name__ == "__main__":
    # Check if required folders exist
    if not os.path.exists("./uploads"):
        os.mkdir("./uploads")
    if not os.path.exists("./output"):
        os.mkdir("./output")

    app.run(host="0.0.0.0", port=8000, debug=True)