import requests
import json
import time
import os

# --- CONFIGURATION ---
OUTPUT_FILE = 'links.txt'
SUBREDDIT = 'pakistan'
#
KEYWORDS = [   
    
    "jirga decision etiquette",
    "Pashtun conflict de-escalation",
    "why villagers avoid saying no",
    "indirect communication norms Pakistan",
    "how hosts express discomfort Pakistan"
]
LIMIT_PER_KEYWORD = 5

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def harvest_links():
    # 1. Load Existing Links (To prevent deleting your old work)
    existing_links = set()
    if os.path.exists(OUTPUT_FILE):
        try:
            # FIX 1: Use utf-8 encoding to prevent Windows errors
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        existing_links.add(line.strip())
            print(f"📂 Loaded {len(existing_links)} existing links from {OUTPUT_FILE}.")
        except Exception as e:
            print(f"⚠️ Could not read existing file: {e}")

    # 2. Harvest New Links
    new_links = set()
    print(f"🚜 Starting Harvest on r/{SUBREDDIT}...")

    for keyword in KEYWORDS:
        print(f"   🔎 Searching for: '{keyword}'...")
        
        search_url = f"https://www.reddit.com/r/{SUBREDDIT}/search.json?q={keyword}&restrict_sr=1&limit={LIMIT_PER_KEYWORD}&sort=relevance"
        
        try:
            response = requests.get(search_url, headers=HEADERS)
            
            if response.status_code == 200:
                data = response.json()
                posts = data['data']['children']
                
                for post in posts:
                    permalink = post['data']['permalink']
                    full_url = f"https://www.reddit.com{permalink}"
                    
                    # Only add if we haven't seen it before
                    if full_url not in existing_links and full_url not in new_links:
                        new_links.add(full_url)
                    
                print(f"      Found {len(posts)} posts (New unique links: {len(new_links)})")
            else:
                print(f"      Failed (Status: {response.status_code})")

            time.sleep(2) # Be polite

        except Exception as e:
            print(f"      Error: {e}")

    # 3. Merge and Save
    if new_links:
        total_links = existing_links.union(new_links)
        print(f"\n💾 Merging {len(new_links)} new links with {len(existing_links)} old ones...")
        
        # FIX 2: Use utf-8 encoding for writing too
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            for link in total_links:
                f.write(link + "\n")
        
        print(f"Harvest Complete! {OUTPUT_FILE} now has {len(total_links)} total links.")
    else:
        print("\n No new unique links found. Your list is already up to date.")

if __name__ == "__main__":
    harvest_links()