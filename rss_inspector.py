import requests
import re

RSS_URL = "https://docs.house.gov/BillsThisWeek-RSS.xml"

def inspect_rss_tail():
    print(f"--- CONNECTING TO {RSS_URL} ---")
    
    # 1. We ask for the last 15,000 bytes (approx 15KB)
    # This is small enough to be instant, large enough to catch the last 2-3 updates.
    headers = {
        "User-Agent": "Mozilla/5.0 (TheCapitolWire Inspector)",
        "Range": "bytes=-15000" 
    }

    try:
        # stream=True ensures we don't accidentally download 50MB if the server ignores our Range header
        with requests.get(RSS_URL, headers=headers, stream=True, timeout=10) as r:
            
            print(f"HTTP Status Code: {r.status_code}")
            
            if r.status_code == 206:
                print("✅ SUCCESS: Server accepted Partial Content request (Tail Read).")
            elif r.status_code == 200:
                print("⚠️ WARNING: Server ignored Range header and sent the whole file.")
                print("   (Aborting download to prevent crash)")
                return
            else:
                print(f"❌ ERROR: Unexpected status code.")
                return

            # Read the chunk
            chunk = r.content.decode('utf-8', errors='ignore')
            
            print("\n--- RAW TAIL CONTENT (LAST 1000 CHARS) ---")
            print(chunk[-1000:]) 
            print("------------------------------------------\n")

            # Run the extraction logic to see what it catches
            print("--- EXTRACTING LINKS ---")
            
            # Regex 1: Find specific dated URLs
            matches = re.findall(r'href=["\'](http[s]?://docs\.house\.gov/floor/Default\.aspx\?date=[\d-]+)["\']', chunk)
            
            # Regex 2: Check dates in <title> tags just for human verification
            titles = re.findall(r'<title[^>]*>(.*?)</title>', chunk)

            if matches:
                print(f"🎯 FOUND {len(matches)} TARGET URLS:")
                for m in matches:
                    print(f"   -> {m}")
            else:
                print("❌ NO TARGET URLS FOUND in the tail.")
                
            if titles:
                print(f"\n👀 HUMAN CHECK (Titles found in this chunk):")
                for t in titles:
                    print(f"   - {t}")

    except Exception as e:
        print(f"CRASH: {e}")

if __name__ == "__main__":
    inspect_rss_tail()
