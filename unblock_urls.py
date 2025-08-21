import mysql.connector
import socket
import subprocess
from urllib.parse import urlparse

def fetch_urls():
    conn = mysql.connector.connect(
        host="localhost",
        user="kali",
        password="kali",
        database="threat_dashboard"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT url FROM phishing_urls ORDER BY id DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [r[0] for r in rows]

def resolve_ip(url):
    try:
        parsed = urlparse(url)
        domain = parsed.hostname
        if not domain:
            print(f"❌ Invalid URL: {url}")
            return None
        return socket.gethostbyname(domain)
    except Exception as e:
        print(f"❌ Couldn’t resolve {url}: {e}")
        return None

def unblock_ip(ip):
    try:
        subprocess.run(
            ["sudo", "ufw", "delete", "deny", "out", "to", ip],
            check=True
        )
        print(f"✅ Unblocked outbound to {ip}")
    except subprocess.CalledProcessError:
        print(f"⚠️ Skipping — no rule found for {ip} or already deleted")

def main():
    urls = fetch_urls()
    print(f"🧹 Unblocking from {len(urls)} threat URLs...")
    for url in urls:
        ip = resolve_ip(url)
        if ip:
            unblock_ip(ip)

if __name__ == "__main__":
    main()
