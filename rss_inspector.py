import requests
import re

RSS_URL = "https://docs.house.gov/BillsThisWeek-RSS.xml"

def inspect_rss_tail():
    print(f"--- CONNECTING TO {RSS_URL} ---")
    
    # 1. Ask for the last 15,000 bytes (Tail Read)
    # 2. IMPORTANT: 'Accept-Encoding: identity' tells the server NOT to gzip the response.
    #    (Partial gzip files are impossible to decode, so we need raw text).
    headers = {
        "User-Agent": "Mozilla/5.0 (TheCapitolWire Inspector)",
        "Range": "bytes=-15000",
        "Accept-Encoding": "identity" 
    }

    try:
        # stream=True ensures we don't accidentally download 50MB if headers are ignored
        with requests.get(RSS_URL, headers=headers, stream=True, timeout=10) as r:
            
            print(f"HTTP Status Code: {r.status_code}")
            
            if r.status_code == 206:
                print("✅ SUCCESS: Server accepted Partial Content request (Tail Read).")
            elif r.status_code == 200:
                print("⚠️ WARNING: Server ignored Range header and sent the whole file.")
                print("   (Aborting download to prevent crash)")
                return
            else:
                print(f"❌ ERROR: Unexpected status code {r.status_code}")
                return

            # Read the chunk
            chunk = r.content.decode('utf-8', errors='ignore')
            
            print("\n--- RAW TAIL CONTENT (LAST 1000 CHARS) ---")
            print(chunk[-1000:]) 
            print("------------------------------------------\n")

            # Run the extraction logic
            print("--- EXTRACTING LINKS ---")
            
            # Regex to find specific dated URLs
            matches = re.findall(r'href=["\'](http[s]?://docs\.house\.gov/floor/Default\.aspx\?date=[\d-]+)["\']', chunk)
            
            # Check for current week fallback
            base_found = ("Default.aspx" in chunk)

            if matches:
                print(f"🎯 FOUND {len(matches)} TARGET URLS:")
                for m in matches:
                    print(f"   -> {m}")
            else:
                print("❌ NO TARGET URLS FOUND in the tail.")
                
            if base_found:
                print("ℹ️  Note: Standard 'Default.aspx' reference found (Current Week).")

    except Exception as e:
        print(f"CRASH: {e}")

if __name__ == "__main__":
    inspect_rss_tail()
