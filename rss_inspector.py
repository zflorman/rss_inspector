import requests
import re
import sys

RSS_URL = "https://docs.house.gov/BillsThisWeek-RSS.xml"

def inspect_rss_tail():
    print(f"--- CONNECTING TO {RSS_URL} ---")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (TheCapitolWire Inspector)",
        # We assume they ignore Range, so we won't even send it.
        # We rely on the streaming logic below.
    }

    try:
        # stream=True is critical. It prevents Python from downloading the body immediately.
        with requests.get(RSS_URL, headers=headers, stream=True, timeout=45) as r:
            
            print(f"HTTP Status Code: {r.status_code}")
            
            # The Rolling Buffer
            # We will store data here, but trim it constantly so it never grows > 15KB
            tail_buffer = b""
            MAX_BUFFER_SIZE = 15000 
            total_bytes = 0
            
            print("--- STREAMING DATA (Please Wait)... ---")
            
            # We iterate over the file in small chunks
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    total_bytes += len(chunk)
                    tail_buffer += chunk
                    
                    # If buffer gets too big, trim from the LEFT (discarding old data)
                    if len(tail_buffer) > MAX_BUFFER_SIZE:
                        tail_buffer = tail_buffer[-MAX_BUFFER_SIZE:]
            
            print(f"✅ Stream Complete. Processed {total_bytes / 1024:.2f} KB total.")
            print("--- DECODING TAIL ---")

            # Decode only the last bit we saved
            tail_text = tail_buffer.decode('utf-8', errors='ignore')
            
            print("\n--- RAW TAIL CONTENT (LAST 500 CHARS) ---")
            print(tail_text[-500:]) 
            print("------------------------------------------\n")

            # --- SEARCH FOR LINKS ---
            print("--- EXTRACTING TARGET URLS ---")
            
            # Regex to find Default.aspx links with dates (e.g. date=2026-01-12)
            matches = re.findall(r'href=["\'](http[s]?://docs\.house\.gov/floor/Default\.aspx\?date=[\d-]+)["\']', tail_text)
            
            # Standard fallback check
            base_found = ("Default.aspx" in tail_text) and ("date=" not in tail_text)

            unique_links = sorted(list(set(matches)))

            if unique_links:
                print(f"🎯 FOUND {len(unique_links)} FUTURE WEEKS:")
                for m in unique_links:
                    print(f"   -> {m}")
            else:
                print("❌ NO DATED URLS FOUND in the tail.")
                
            if base_found:
                print("ℹ️  Note: Found reference to 'This Week' (Default.aspx).")

    except Exception as e:
        print(f"CRASH: {e}")

if __name__ == "__main__":
    inspect_rss_tail()
