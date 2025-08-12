# app.py (versi diperbaiki)

from flask import Flask, render_template, request, send_file
import csv
import io
import re

app = Flask(__name__)

def filter_results_advanced(data, query_string):
    results = []
    
    # Memisahkan kueri berdasarkan operator AND (&&)
    and_parts = re.split(r'\s*&&\s*', query_string)
    
    for row in data:
        overall_match = True
        
        for and_part in and_parts:
            # Memisahkan kueri berdasarkan operator OR (||)
            or_parts = re.split(r'\s*\|\|\s*', and_part)
            or_match = False
            
            for or_part in or_parts:
                part = or_part.strip()
                if not part:
                    continue

                # Cek apakah kueri memiliki format key="value"
                match = re.match(r'(\w+)\s*=\s*"(.*)"', part)
                if match:
                    key = match.group(1).lower()
                    value = match.group(2).lower()
                    
                    row_value = str(row.get(key, '')).lower()
                    if value in row_value:
                        or_match = True
                        break
                else: # Pencarian kata kunci umum
                    keyword = part.lower()
                    if (keyword in row['ip'].lower() or
                        (row['title'] and keyword in row['title'].lower())):
                        or_match = True
                        break

            if not or_match:
                overall_match = False
                break
        
        if overall_match:
            results.append(row)
            
    return results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST', 'GET'])
def search():
    query = request.form.get('query', '')
    if not query:
        query = request.args.get('query', '')

    all_data = []
    try:
        with open("data/scan_results.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            all_data = list(reader)
    except FileNotFoundError:
        return "File data/scan_results.csv tidak ditemukan. Jalankan crawler.py terlebih dahulu.", 404

    results = filter_results_advanced(all_data, query)
    
    return render_template('results.html', results=results, query=query)

@app.route('/download')
def download():
    query = request.args.get('query', '')
    all_data = []

    try:
        with open("data/scan_results.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            all_data = list(reader)
    except FileNotFoundError:
        return "File data/scan_results.csv tidak ditemukan.", 404

    results = filter_results_advanced(all_data, query)

    output = io.StringIO()
    fieldnames = ["ip", "port", "title", "app", "header", "body"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)
    
    output.seek(0)
    
    return send_file(io.BytesIO(output.getvalue().encode('utf-8')),
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name='shadowcore_results.csv')

if __name__ == '__main__':
    app.run(debug=True)