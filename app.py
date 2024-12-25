# app.py
from flask import Flask, render_template, request, send_file
import os
from time import sleep
from scripts.scraper import scrap_data  # Import the scraper function

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    show_buttons = False
    scraping_in_progress = False  # Flag for scraping status
    record_count = 0

    if request.method == "POST":
        url = request.form.get("url")
        if url:
            scraping_in_progress = True  # Set flag when scraping starts
            message = "Please wait while data is scraping..."

            # Start scraping and collect results
            result, record_count = scrap_data(url)  # Trigger scraping

            # After scraping completes
            scraping_in_progress = False
            message = f"Web Scraping Completed: {record_count} record(s) found!"
            show_buttons = True  # Enable download buttons

    return render_template("index.html", message=message, show_buttons=show_buttons, 
                           scraping_in_progress=scraping_in_progress, record_count=record_count)

@app.route("/download/csv")
def download_csv():
    file_path = "static/files/output_data.csv"
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found."

@app.route("/download/xlsx")
def download_xlsx():
    file_path = "static/files/output_data.xlsx"
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found."

if __name__ == "__main__":
    app.run(debug=True)
