import requests
import json
import time
import random

# --- CONFIGURATION ---
INPUT_FILE = 'links.txt'
OUTPUT_FILE = 'mehman_data.json'

# We need a "fake" User-Agent so Reddit thinks we are a browser, not a bot.
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def clean_url(url):
    """Ensures the URL ends with .json and handles trailing slashes."""
    url = url.strip()
    if url.endswith('/'):
        url = url[:-1]
    if not url.endswith('.json'):
        url += '.json'
    return url

def main():
    print(f"🔗 Reading links from {INPUT_FILE}...")
    
    try:
        with open(INPUT_FILE, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"❌ Error: Could not find {INPUT_FILE}.")
        return

    dataset = []
    print(f"🚀 Starting scrape for {len(urls)} threads using JSON endpoints...")

    for i, url in enumerate(urls):
        json_url = clean_url(url)
        print(f"   [{i+1}/{len(urls)}] Fetching: {json_url}")

        try:
            # 1. Make the request
            response = requests.get(json_url, headers=HEADERS)
            
            # Check for "Too Many Requests" (Rate Limiting)
            if response.status_code == 429:
                print("      ⚠️ Rate limited! Sleeping for 10 seconds...")
                time.sleep(10)
                response = requests.get(json_url, headers=HEADERS) # Try once more

            if response.status_code != 200:
                print(f"      ❌ Failed with status code: {response.status_code}")
                continue

            data = response.json()

            # 2. Extract Question (Post Data)
            # Reddit JSON structure: List of 2 items. Item 0 is the Post, Item 1 is the Comments.
            post_data = data[0]['data']['children'][0]['data']
            title = post_data.get('title', 'No Title')
            selftext = post_data.get('selftext', '')
            full_question = f"{title}\n\n{selftext}"

            # 3. Extract Answers (Comments)
            comments_data = data[1]['data']['children']
            top_answers = []
            
            for comment in comments_data[:]:
                # Ignore "more" tags or empty data
                if comment['kind'] == 't1': # t1 is a comment
                    body = comment['data'].get('body', '')
                    # explicit check to avoid empty or deleted comments
                    if body and body != '[deleted]' and body != '[removed]':
                        top_answers.append(body)

            # 4. Structure Data
            entry = {
                "url": url,
                "title": title,
                "question": full_question,
                "answers": top_answers
            }
            dataset.append(entry)
            
            print(f"      ✅ Success! Got {len(top_answers)} answers.")

            # IMPORTANT: Sleep to avoid getting banned
            time.sleep(random.uniform(2, 5)) 

        except Exception as e:
            print(f"      ⚠️ Error scraping {url}: {e}")

    # 5. Save
    print(f"💾 Saving data to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=4, ensure_ascii=False)
        
    print("✅ Done! Data pipeline complete.")

if __name__ == "__main__":
    main()