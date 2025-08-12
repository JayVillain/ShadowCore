# crawler.py (versi diperbaiki)

import socket
import requests
import csv
import ipaddress
import time

def scan_port(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect((ip, port))
        return True
    except (socket.timeout, socket.error):
        return False
    finally:
        s.close()

def get_web_info(ip, port):
    protocol = "https" if port == 443 else "http"
    try:
        response = requests.get(f"{protocol}://{ip}", timeout=2, headers={'User-Agent': 'ShadowCore-Crawler'}, verify=False) # verify=False untuk HTTPS
        if response.status_code == 200:
            title = None
            if "<title>" in response.text:
                start = response.text.find("<title>") + 7
                end = response.text.find("</title>", start)
                title = response.text[start:end].strip()

            app = None
            if 'wp-content' in response.text or 'WordPress' in response.text:
                app = "WordPress"
            elif 'cloudflare' in response.headers.get('Server', '').lower():
                app = "Cloudflare"

            header_str = str(response.headers)
            body_str = response.text

            return {
                "title": title,
                "app": app,
                "header": header_str,
                "body": body_str
            }
    except requests.RequestException:
        return None
    return None

def main():
    target_ips = ["1.1.1.1", "8.8.8.8"] # Contoh IP. Ganti dengan rentang IP yang ingin Anda pindai.
    ports_to_scan = [80, 443]
    
    results = []
    
    print("Mulai pemindaian...")
    
    for ip_str in target_ips:
        ip = ip_str
        print(f"Memindai IP: {ip}")
        
        for port in ports_to_scan:
            if scan_port(ip, port):
                print(f"Port {port} terbuka!")
                web_info = get_web_info(ip, port)
                if web_info:
                    results.append({
                        "ip": ip,
                        "port": port,
                        "title": web_info.get("title", ""),
                        "app": web_info.get("app", ""),
                        "header": web_info.get("header", ""),
                        "body": web_info.get("body", "")
                    })
    
    with open("data/scan_results.csv", "w", newline="", encoding="utf-8") as f:
        fieldnames = ["ip", "port", "title", "app", "header", "body"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Pemindaian selesai. Hasil disimpan di data/scan_results.csv. Total: {len(results)} entri.")

if __name__ == "__main__":
    # Menonaktifkan peringatan SSL
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    main()