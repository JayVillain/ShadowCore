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

def get_web_info(ip):
    try:
        response = requests.get(f"http://{ip}", timeout=2, headers={'User-Agent': 'ShadowCore-Crawler'})
        if response.status_code == 200:
            title = None
            if "<title>" in response.text:
                start = response.text.find("<title>") + 7
                end = response.text.find("</title>", start)
                title = response.text[start:end].strip()

            app = None
            if 'wp-content' in response.text or 'WordPress' in response.text:
                app = "WordPress"

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
    target_ips = ["8.8.8.8", "8.8.4.4", "1.1.1.1"] # Ganti dengan IP yang ingin Anda pindai
    ports_to_scan = [80]
    
    results = []
    
    print("Mulai pemindaian...")
    
    for ip_str in target_ips:
        ip = ip_str
        print(f"Memindai IP: {ip}")
        
        for port in ports_to_scan:
            if scan_port(ip, port):
                print(f"Port {port} terbuka!")
                web_info = get_web_info(ip)
                if web_info:
                    results.append({
                        "ip": ip,
                        "port": port,
                        "title": web_info.get("title"),
                        "app": web_info.get("app"),
                        "header": web_info.get("header"),
                        "body": web_info.get("body")
                    })
    
    with open("data/scan_results.csv", "w", newline="", encoding="utf-8") as f:
        fieldnames = ["ip", "port", "title", "app", "header", "body"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Pemindaian selesai. Hasil disimpan di data/scan_results.csv. Total: {len(results)} entri.")

if __name__ == "__main__":
    main()