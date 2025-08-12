# crawler.py (menggunakan API FOFA)

import requests
import csv
import base64
import time

# Ganti dengan email dan API key Anda
fofa_email = "bakagusi23@gmail.com"
fofa_key = "7423571a9d91c7a87e1ef776442fa18a"

def get_fofa_data(query_string, page=1, size=100):
    # Encode query string ke Base64 (sesuai format FOFA)
    encoded_query = base64.b64encode(query_string.encode('utf-8')).decode('utf-8')
    
    url = f"https://fofa.info/api/v1/search/all?email={fofa_email}&key={fofa_key}&qbase64={encoded_query}&page={page}&size={size}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['error']:
                print(f"Error dari API FOFA: {data['errmsg']}")
                return None
            return data
        else:
            print(f"Error: Status code {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Error saat menghubungi API: {e}")
        return None

def main():
    # Contoh kueri FOFA yang ingin Anda cari
    fofa_query = 'app="WordPress" && (body="simple-file-list" || header="simple-file-list")'
    
    print(f"Mencari dengan kueri: {fofa_query}")
    fofa_results = []
    
    # Ambil 100 hasil pertama (bisa disesuaikan)
    data = get_fofa_data(fofa_query, size=100)
    
    if data and 'results' in data:
        print(f"Ditemukan {len(data['results'])} hasil.")
        for item in data['results']:
            # Item dalam format FOFA adalah: ['ip', 'port', 'title', 'header', 'body']
            # Anda perlu menyesuaikan format ini ke format CSV Anda
            fofa_results.append({
                "ip": item[0],
                "port": item[1],
                "title": item[2],
                "header": item[3],
                "body": item[4],
                "app": "WordPress" if "wordpress" in item[2].lower() or "wp-content" in item[4].lower() else ""
            })
    
    with open("data/scan_results.csv", "w", newline="", encoding="utf-8") as f:
        fieldnames = ["ip", "port", "title", "app", "header", "body"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(fofa_results)
    
    print(f"Penyimpanan data selesai. Total: {len(fofa_results)} entri.")

if __name__ == "__main__":
    main()