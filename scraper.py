import praw
import json
import time

# --- CONFIGURATION ---
# Replace these with your actual values from the Reddit Apps page
CLIENT_ID = 'YOUR_CLIENT_ID_HERE'
CLIENT_SECRET = 'YOUR_CLIENT_SECRET_HERE'
USER_AGENT = 'script:MehmanScraper:v1.0 (by /u/YOUR_REDDIT_USERNAME)'

# Input and Output files
INPUT_FILE = 'links.txt'
OUTPUT_FILE = 'mehman_data.json'

def main():
    # 1. Initialize Reddit Instance
    reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT
    )

    print(f"🔗 Reading links from {INPUT_FILE}...")
    
    try:
        with open(INPUT_FILE, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"❌ Error: Could not find {INPUT_FILE}. Make sure it is in the same folder.")
        return

    dataset = []

    print(f"🚀 Starting scrape for {len(urls)} threads...")

    for i, url in enumerate(urls):
        try:
            print(f"   [{i+1}/{len(urls)}] Processing: {url}")
            
            # Create a submission object
            submission = reddit.submission(url=url)

            # 2. Get the Question (Title + Body)
            title = submission.title
            question_body = submission.selftext
            
            # Combine them for a full context "Question"
            full_question = f"{title}\n\n{question_body}"

            # 3. Get the Answers (Top Comments)
            submission.comments.replace_more(limit=0) # Remove "load more comments" buttons
            
            top_answers = []
            # We want the top 10 comments, skipping stickied ones if possible
            for comment in submission.comments[:10]:
                if not comment.stickied:
                    top_answers.append(comment.body)

            # 4. Structure the data
            entry = {
                "url": url,
                "title": title,
                "question": full_question,
                "answers": top_answers
            }
            
            dataset.append(entry)
            
            # Be polite to the API
            time.sleep(1) 

        except Exception as e:
            print(f"Failed to scrape {url}: {e}")

    # 5. Save to JSON
    print(f"Saving data to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=4, ensure_ascii=False)
        
    print("Done! Data pipeline complete.")

if __name__ == "__main__":
    main()