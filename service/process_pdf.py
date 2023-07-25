import pdfkit
import camelot
import os
from flask import current_app
import pandas as pd
from pypdf import PdfReader


def get_pdf_type(input_pdf):
    # Check pdf type - esic/epf
    reader = PdfReader(input_pdf)
    page = reader.pages[0]
    text = page.extract_text()

    # searches for headings corresponding to epf/esic pdfs
    if text.find("EMPLOYEE'S PROVIDENT FUND") != -1:
        return "epf"
    elif text.find("Employees' State Insurance Corporation") != -1:
        return "esic"
    else:
        return False

def process_pdf_epf(input_pdf, search_terms):

    # extract tables
    tables = camelot.read_pdf(input_pdf, pages='all', line_scale=40)

    # process tables remove rows without search term
    for table in tables[1:-2]:
        table.df = table.df.replace(r'\n', ' ', regex=True)
        for index in reversed(range(2, table.df.shape[0])):
            if not any(search_term.lower() in table.df.iloc[index].to_string().lower() for search_term in search_terms):
                table.df.drop(index, inplace=True)

    # Convert dfs into html tables
    combined_html = f"""<html>
        <head>
            <link rel="stylesheet" type="text/css" href="../static/df_table.css"/>
        </head>
        <body style="font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;">
            <header>
                <center>
                    <table>
                        <tr>
                            <td rowspan="2"><img src="{os.path.join(current_app.root_path, "static" + os.path.sep + "images" + os.path.sep + "epf_logo.jpeg")}" height="90" width="90"></td>
                            <td rowspan="2" style="width: 150px;"></td>
                            <td style="text-align: center; vertical-align: bottom;">
                                <h2 style="margin-bottom: 6px;">EMPLOYEE'S PROVIDENT FUND</h2>
                                <h3 style="margin-top: 6px;">ELECTRONIC CHALLAN CUM RETURN (ECR)</h3>
                            </td>
                        </tr>
                    </table>
                </center>
            </header>
            <center>
    """

    # First table
    combined_html += "\n".join([f"{tables[0].df.to_html(index=False, header=False)}"])
    # Main data Tables
    combined_html += "\n".join([f"{pd.concat([t.df.iloc[2:] for t in tables[1:-2]], ignore_index=True).to_html(index=False, header=False, classes='df')}"])
    # Last two tables
    combined_html += "\n".join([f"{table.df.to_html(index=False, header=False)}".replace("table", 'table style="display:inline"') for table in tables[-2:]])
    combined_html += "<center></body></html>"

    # Highlight search text
    for search_term in search_terms:
        combined_html = combined_html.replace(search_term, f"<span class='highlight'>{search_term}</span>")

    # Add table header
    table_th = """
        <table border="1" class="dataframe df">
            <thead>
            <tr>
                <th rowspan="2">Sl. No.</th>
                <th rowspan="2">UAN</th>
                <th colspan="2">Name as per</th>
                <th colspan="4">Wages</th>
                <th colspan="4">Contribution Remitted</th>
                <th rowspan="2">Refunds</th>
                <th colspan="3">PMRPY / ABRY Benefit</th>
                <th rowspan="2">Posting Location of the member</th>
            </tr>
            <tr>
                <th>ECR</th>
                <th>UAN Repository</th>
                <th>Gross</th>
                <th>EPF</th>
                <th>EPS</th>
                <th>EDLI</th>
                <th>EE</th>
                <th>EPS</th>
                <th>ER</th>
                <th>NCP Days</th>
                <th>Pension Share</th>
                <th>ER PF Share</th>
                <th>EE Share</th>
            </tr>
            </thead>

    """
    combined_html = combined_html.replace('<table border="1" class="dataframe df">', table_th)

    # Convert HTML table to PDF using pdfkit
    options = {
        'encoding': 'UTF-8',
        'quiet': '',
        "enable-local-file-access": "",
        'no-outline': None,
        'orientation':'Landscape'
    }

    return pdfkit.from_string(combined_html, css="static/df_table.css", options=options)

def process_pdf_esic(input_pdf, search_terms):
    # extract tables
    table0 = camelot.read_pdf(input_pdf, pages='1', line_scale=40)[0].df.iloc[:2]
    extracted_tables = camelot.read_pdf(input_pdf, pages='all', flavor='stream')

    tables = [table0.drop(table0.columns[[1, 2, 4, 6, 8, 9, 10]], axis=1)]

    # process tables remove rows without search term
    for table in extracted_tables:
        table.df = table.df.replace(r'\n', ' ', regex=True)
        for index in reversed(range(2, table.df.shape[0])):
            # clean data 
            if table.df.at[index, 4] and not table.df.at[index, 3]:
                table.df.at[index - 1, 4] += f" {table.df.at[index, 4]}"
                table.df.drop(index, inplace=True)
                continue

            # search for terms
            if not any(search_term in table.df.iloc[index].to_string() for search_term in search_terms):
                table.df.drop(index, inplace=True)
    
    for t in extracted_tables:
        try:
            tables.append(t.df.drop(t.df.columns[[2, 9]], axis=1))
        except:
            tables.append(t.df.drop(t.df.columns[[2]], axis=1))

    # Convert dfs into html tables
    combined_html = f"""<html>
        <head>
            <link rel="stylesheet" type="text/css" href="../static/df_table.css"/>
        </head>
        <body style="font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;">
            <header>
                <center>
                    <table>
                        <tr>
                            <td rowspan="2"><img src="{os.path.join(current_app.root_path, "static" + os.path.sep + "images" + os.path.sep + "esic_logo.png")}" height="90" width="90"></td>
                            <td rowspan="2" style="width: 150px;"></td>
                            <td style="text-align: center; vertical-align: center;">
                                <h2 style="margin-bottom: 6px;">Employees' State Insurance Corporation</h2>
                            </td>
                        </tr>
                    </table>
                </center>
            </header>
            <center>
    """

    # First table
    combined_html += "\n".join([f"{tables[0].to_html(index=False, header=False)}"])
    # Main data Tables
    combined_html += "\n".join([f"{pd.concat([t.iloc[2:] for t in tables[1:]], ignore_index=True).to_html(index=False, header=False, classes='df')}"])
    combined_html += "<center></body></html>"

    # Highlight search text
    for search_term in search_terms:
        combined_html = combined_html.replace(search_term, f"<span class='highlight'>{search_term}</span>")

    # Add table header
    table_th = """
        <table border="1" class="dataframe df" style="page-break-before: auto !important;">
            <thead>
                <tr>
                    <th>SNo.</th>
                    <th>Is Disable</th>
                    <th>IP Number</th>
                    <th>IP Name</th>
                    <th>No. Of Days</th>
                    <th>Total Wages</th>
                    <th>IP Contribution</th>
                    <th>Reason</th>
                </tr>
            </thead>

    """
    combined_html = combined_html.replace('<table border="1" class="dataframe df">', table_th)

    # Convert HTML table to PDF using pdfkit
    options = {
        'encoding': 'UTF-8',
        'quiet': '',
        "enable-local-file-access": "",
        'no-outline': None,
        'orientation':'Landscape'
    }

    return pdfkit.from_string(combined_html, css="static/df_table.css", options=options)

def pdf_to_excel(input_pdf, pdf_type):
    if pdf_type == "epf":
        # extract tables
        tables = camelot.read_pdf(input_pdf, pages='1-3', line_scale=40)
    elif pdf_type == "esic":
        # extract tables
        tables = camelot.read_pdf(input_pdf, pages='1-3', flavor='stream')

    # write tables to excel
    excel_out_file = f"out.xlsx"
    row = 0
    with pd.ExcelWriter(excel_out_file) as writer:
        for table in tables:
            table.df.to_excel(writer, index=False, header=False, startrow=row)
            row += len(table.df.index) + 2

    # # Return the modified PDF as a response
    # return send_file(excel_out_file, mimetype="application/pdfapplication/vnd.openxmlformats-officedocument.spreadsheetml.sheet", download_name=excel_out_file)

    return excel_out_file