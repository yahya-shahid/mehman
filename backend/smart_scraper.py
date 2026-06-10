import requests
import json
import time
import random
import os

# --- CONFIGURATION ---
INPUT_FILE = 'links.txt'
DATA_FILE = 'mehman_data.json'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def clean_url(url):
    """Ensures the URL ends with .json and handles trailing slashes."""
    url = url.strip()
    # Remove existing .json if present to standardize
    if url.endswith('.json'):
        url = url[:-5]
    if url.endswith('/'):
        url = url[:-1]
    return url + '.json'

def main():
    # 1. Load Existing Data (The "Memory")
    existing_data = []
    seen_urls = set()
    
    if os.path.exists(DATA_FILE):
        print(f"📂 Loading existing database: {DATA_FILE}...")
        try:
            # We use utf-8 here to handle Urdu/Emojis in the saved JSON
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                # Create a set of base URLs (without .json) to compare efficiently
                for entry in existing_data:
                    # Normalize stored URL to compare properly
                    normalized_stored = entry['url'].replace('.json', '').rstrip('/')
                    seen_urls.add(normalized_stored)
            print(f"   ✅ Found {len(existing_data)} existing threads.")
        except Exception as e:
            print(f"   ⚠️ Could not read existing data (starting fresh): {e}")

    # 2. Read the Links File our  Target
    try:
        # FIX: Added encoding='utf-8' here so it can read the file created by harvester.py
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            target_links = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"❌ Error: Could not find {INPUT_FILE}.")
        return
    except UnicodeDecodeError as e:
        print(f"❌ Encoding Error reading {INPUT_FILE}: {e}")
        print("Tip: Make sure harvester.py was saved with encoding='utf-8' fix.")
        return

    # 3. Calculate the Delta (What's New?)
    links_to_scrape = []
    for link in target_links:
        # Normalize input link
        clean_link_check = link.replace('.json', '').rstrip('/')
        if clean_link_check not in seen_urls:
            links_to_scrape.append(link)

    if not links_to_scrape:
        print("🎉 No new links to scrape! Your database is up to date.")
        return

    print(f"🚀 Found {len(links_to_scrape)} NEW links to scrape (out of {len(target_links)} total).")
    print("   Starting incremental scrape...")

    # 4. Scrape ONLY the New Links
    new_entries = []
    
    for i, url in enumerate(links_to_scrape):
        json_url = clean_url(url)
        print(f"   [{i+1}/{len(links_to_scrape)}] Fetching: {json_url}")

        try:
            response = requests.get(json_url, headers=HEADERS)
            
            if response.status_code == 429:
                print("      ⚠️ Rate limited! Sleeping for 10 seconds...")
                time.sleep(10)
                response = requests.get(json_url, headers=HEADERS)

            if response.status_code != 200:
                print(f"      ❌ Failed with status code: {response.status_code}")
                continue

            data = response.json()

            # Extract Post
            post_data = data[0]['data']['children'][0]['data']
            title = post_data.get('title', 'No Title')
            selftext = post_data.get('selftext', '')
            full_question = f"{title}\n\n{selftext}"

            # Extract Comments
            comments_data = data[1]['data']['children']
            top_answers = []
            for comment in comments_data[:]:
                if comment['kind'] == 't1':
                    body = comment['data'].get('body', '')
                    if body and body not in ['[deleted]', '[removed]']:
                        top_answers.append(body)

            # Create Entry
            entry = {
                "url": url, # Save the original URL from text file
                "title": title,
                "question": full_question,
                "answers": top_answers
            }
            
            new_entries.append(entry)
            print(f"      ✅ Success! Got {len(top_answers)} answers.")

            time.sleep(random.uniform(2, 5)) 

        except Exception as e:
            print(f"      ⚠️ Error scraping {url}: {e}")

    # 5. Merge and Save
    if new_entries:
        combined_data = existing_data + new_entries
        print(f"💾 Appending {len(new_entries)} new threads to {DATA_FILE}...")
        
        # Create a backup just in case
        if os.path.exists(DATA_FILE):
             try:
                os.rename(DATA_FILE, DATA_FILE + ".bak")
             except OSError:
                pass # Ignore if rename fails on Windows due to locks
             
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, indent=4, ensure_ascii=False)
            
        print(f"✅ Database updated! Total threads: {len(combined_data)}")
    else:
        print("⚠️ No valid data scraped from the new links.")

if __name__ == "__main__":
    main()