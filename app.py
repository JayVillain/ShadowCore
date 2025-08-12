# app.py (versi modifikasi)

from flask import Flask, render_template, request, send_file
import csv
import io
import re

app = Flask(__name__)

# Fungsi untuk memfilter hasil pencarian (tidak berubah)
def filter_results_advanced(data, query_string):
    results = []
    and_parts = re.split(r'\s*&&\s*', query_string)
    for row in data:
        overall_match = True
        for and_part in and_parts:
            or_parts = re.split(r'\s*\|\|\s*', and_part)
            or_match = False
            for or_part in or_parts:
                part = or_part.strip()
                if not part:
                    continue
                match = re.match(r'(\w+)\s*=\s*"(.*)"', part)
                if match:
                    key = match.group(1).lower()
                    value = match.group(2).lower()
                    row_value = str(row.get(key, '')).lower()
                    if value in row_value:
                        or_match = True
                        break
                else:
                    keyword = part.lower()
                    if (keyword in str(row['ip']).lower() or
                        (row['title'] and keyword in str(row['title']).lower())):
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
    
    # Ambil hanya IP dan Port untuk ditampilkan
    display_results = [{'ip': r['ip'], 'port': r['port'], 'title': r.get('title', '')} for r in results]
    
    return render_template('results.html', results=display_results, query=query)

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
    # Hanya kolom URL yang akan diunduh
    writer = csv.writer(output)
    writer.writerow(["URL"])

    for row in results:
        ip = row['ip']
        port = row['port']
        protocol = "https" if str(port) == "443" else "http"
        url = f"{protocol}://{ip}:{port}"
        writer.writerow([url])
    
    output.seek(0)
    
    return send_file(io.BytesIO(output.getvalue().encode('utf-8')),
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name='shadowcore_urls.csv')

if __name__ == '__main__':
    app.run(debug=True)