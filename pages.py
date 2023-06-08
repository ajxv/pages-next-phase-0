from flask import Flask, send_file
from flask import render_template, request
from werkzeug.utils import secure_filename
import camelot

app = Flask(__name__)

@app.route("/", methods=['POST', 'GET'])
def index():

    if request.method == "POST":
        # Get the uploaded PDF file and search term from the form
        file = request.files['input_file']
        search_term = request.form['search_key']

        # Save the uploaded PDF file
        pdf_path = f"uploads/{secure_filename(file.filename)}"
        file.save(pdf_path)

        # Process the PDF file and generate the modified PDF
        output_pdf_path = process_pdf(pdf_path, search_term)

        # Return the modified PDF as a response
        return send_file(output_pdf_path, as_attachment=True)

    return render_template("pages.html")

def process_pdf(pdf_path, search_term):
    # do some stuff here
    #  ̶X̶ ̶|̶ ̶X̶ ̶|̶ ̶X̶ 
    # ---+---+---
    #    | O | O 
    # ---+---+---
    #  O |   | X 
    pass