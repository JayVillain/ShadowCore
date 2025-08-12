from flask import Flask, render_template, request, send_file
import csv
import io

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query', '').lower()
    results = []
    try:
        with open("data/scan_results.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Logika pencarian sederhana
                if query in row['ip'].lower() or \
                   (row['title'] and query in row['title'].lower()):
                    results.append(row)
    except FileNotFoundError:
        return "File data/scan_results.csv tidak ditemukan. Jalankan crawler.py terlebih dahulu.", 404
        
    return render_template('results.html', results=results)

@app.route('/download')
def download():
    query = request.args.get('query', '').lower()
    results = []
    try:
        with open("data/scan_results.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if query in row['ip'].lower() or \
                   (row['title'] and query in row['title'].lower()):
                    results.append(row)
    except FileNotFoundError:
        return "File data/scan_results.csv tidak ditemukan.", 404

    # Buat file CSV di memori
    output = io.StringIO()
    fieldnames = ["ip", "port", "title"]
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