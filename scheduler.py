import time
from fetcher.abusech import fetch_abusech_data

FETCH_INTERVAL = 30  # every 30 seconds

def main():
    while True:
        print("⏳ Fetching Abuse.ch data...")
        fetch_abusech_data()
        print("✅ Done. Waiting for next fetch cycle...")
        time.sleep(FETCH_INTERVAL)

if __name__ == "__main__":
    main()
