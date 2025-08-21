import subprocess
import requests
import zipfile
import io
import csv
import mysql.connector
import socket
from urllib.parse import urlparse

# Function to resolve URL to IP
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

# Function to block IP using UFW
def block_url(url):
    ip = resolve_ip(url)
    if ip:
        try:
            subprocess.run(
                ["sudo", "ufw", "deny", "out", "to", ip],
                check=True
            )
            print(f"🛡️ Blocked IP {ip} for {url}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to block {url} with IP {ip}: {e}")

def fetch_abusech_data():
    url = "https://urlhaus.abuse.ch/downloads/csv/"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print("❌ Failed to fetch Abuse.ch ZIP file.")
            return

        zip_content = io.BytesIO(response.content)
        with zipfile.ZipFile(zip_content) as archive:
            print("🧾 ZIP archive contains:")
            csv_file = None
            for name in archive.namelist():
                print(f"   - {name}")
                if name.endswith(".csv") or name.endswith(".txt"):
                    csv_file = archive.open(name)
                    print("📥 Opened CSV file:", name)
                    break

            if csv_file is None:
                print("❌ No CSV file found in ZIP archive.")
                return

            print("📖 Reading CSV data...")
            row_count = 0
            max_rows = 10  #
            
           # Use csv.DictReader for safe parsing
            text_stream = io.TextIOWrapper(csv_file, encoding="utf-8", newline='')
            reader = csv.reader(
                (line for line in text_stream if not line.startswith("#")),
                delimiter=",", quotechar='"'
            )

            for row in reader:
                if not row or row[0].startswith("#"):
                    continue

                try:
                    phish_id = row[0].strip()
                    url_val = row[2].strip()
                    url_status = row[3].strip()
                    threat_type = row[5].strip()

                    print(f"➡️ Processing row {row_count + 1}: {url_val} [{threat_type}]")

                    
                    conn = mysql.connector.connect(
                        host="localhost",
                        user="kali",
                        password="kali",
                        database="threat_dashboard"
                    )
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO phishing_urls (url, phish_id, online, target)
                        VALUES (%s, %s, %s, %s)""",
                        (url_val, phish_id[:100], url_status, threat_type))

                    if cursor.rowcount == 0:
                        print(f"⚠️ Duplicate entry skipped: {phish_id}")

                    conn.commit()
                    cursor.close()
                    conn.close()

                    
                    block_url(url_val)

                    row_count += 1
                    print(f"✅ Inserted and blocked: {url_val}")

                    if row_count >= max_rows:
                        print("🛑 Stopping after 10 rows (debug mode)")
                        break

                except Exception as insert_err:
                    print(f"⚠️ Skipping row due to error: {insert_err}")

            print(f"✅ Successfully processed {row_count} rows.")

    except Exception as fetch_err:
        print("❌ Error fetching Abuse.ch data:", fetch_err)
