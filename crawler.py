import socket
import requests
import csv
import ipaddress
import time

def scan_port(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1) # Timeout 1 detik
    try:
        s.connect((ip, port))
        return True
    except (socket.timeout, socket.error):
        return False
    finally:
        s.close()

def get_title(ip):
    try:
        response = requests.get(f"http://{ip}", timeout=2)
        if response.status_code == 200 and "<title>" in response.text:
            start = response.text.find("<title>") + 7
            end = response.text.find("</title>", start)
            return response.text[start:end].strip()
    except requests.RequestException:
        return None
    return None

def main():
    target_ips = ["8.8.8.8", "8.8.4.4", "1.1.1.1"] # Contoh IP. Ganti dengan rentang IP yang ingin Anda pindai.
    ports_to_scan = [80, 443, 8080, 22]
    
    results = []
    
    print("Mulai pemindaian...")
    
    for ip_str in target_ips:
        ip = ip_str
        print(f"Memindai IP: {ip}")
        
        for port in ports_to_scan:
            if scan_port(ip, port):
                print(f"Port {port} terbuka!")
                title = get_title(ip) if port in [80, 443] else "N/A"
                results.append({"ip": ip, "port": port, "title": title})
    
    with open("data/scan_results.csv", "w", newline="", encoding="utf-8") as f:
        fieldnames = ["ip", "port", "title"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Pemindaian selesai. Hasil disimpan di data/scan_results.csv. Total: {len(results)} entri.")

if __name__ == "__main__":
    main()