import requests
import json
import time
import os

# --- CONFIGURATION ---
OUTPUT_FILE = 'links.txt'
SUBREDDIT = 'pakistan'
KEYWORDS = [
    "village customs Pakistan",
    "Pashtun hospitality norms",
    "how to behave as a guest in Pakistan",
    "rural Pakistan social hierarchy",
    "customs when entering someone’s home Pakistan",
    "Pashto honor culture explanation",
    "tea offering etiquette Pakistan",
    "village privacy norms Pakistan",
    "how to address elders Pakistan",
    "community spaces Pakistan villages",
    "women interaction rules Pakistan rural",
    "rural conflict avoidance Pakistan",
    "Pashtunwali everyday examples",
    "nonverbal communication Pakistan",
    "body language in Pakistani villages",
    "greeting rituals Pashtun regions",
    "respecting family boundaries Pakistan",
    "hujra stories and traditions",
    "Swat oral history traditions",
    "cultural dos and don'ts Pakistan villages",
    "local transport challenges Pakistan villages",
    "village road conditions Pakistan",
    "mobile network coverage northern Pakistan",
    "electricity outages travel Pakistan",
    "water safety Pakistan travel",
    "hygiene expectations Pakistan rural",
    "village market tips Pakistan",
    "local guides Swat Chitral",
    "what to expect in Pakistani homestays",
    "small town hotel reviews Pakistan",
    "weather hazards KPK travel",
    "river crossing safety Pakistan",
    "navigating small bazaars Pakistan",
    "food hygiene rural Pakistan",
    "handwashing etiquette Pakistan",
    "traditional foods Pakistan villages",
    "mountain road closure updates Pakistan",
    "local jeep driver reviews Pakistan",
    "remote area travel planning Pakistan",
    "emergency supplies for northern Pakistan"
    "how villagers perceive foreigners Pakistan",
    "curiosity toward tourists Pakistan",
    "responding politely to staring Pakistan",
    "explaining boundaries to locals",
    "saying no politely Urdu",
    "how to introduce yourself in villages",
    "how to decline food respectfully",
    "how to ask permission for photography",
    "explaining hobbies to villagers",
    "how to manage crowd curiosity in rural areas",
    "safe conversation topics Pakistan",
    "avoiding sensitive topics in Pakistan",
    "explaining technology to villagers",
    "how to calm tense situations Pakistan",
    "foreigner safety etiquette Pakistan",
    "how to speak respectfully Urdu phrases",
    "tourist behavior mistakes Pakistan",
    "dress code misunderstandings Pakistan",
    "foreign women expectations Pakistan",
    "managing cultural shyness Pakistan",
    "basic Pashto conversation tips",
    "simple Urdu phrases for villagers",
    "Pashto compliments and politeness",
    "how to request directions in Pashto",
    "rural dialect differences Swat",
    "phrases for asking permission Urdu",
    "how to express gratitude Pashto",
    "simple apology phrases Urdu",
    "how to explain your purpose Urdu",
    "how to talk to shopkeepers Pakistan",
    "flood risk northern Pakistan",
    "wildlife safety Pakistan mountains",
    "landslide zones Swat Chitral",
    "travel after sunset rural Pakistan",
    "interacting with LEAs Pakistan",
    "dealing with roadside checks Pakistan",
    "understanding village disputes Pakistan",
    "what to avoid saying Pakistan rural",
    "respectful behavior in mosques small towns",
    "local sensitivities Pakistan travel",
    "understanding Sufi culture Pakistan",
    "folklore northern Pakistan",
    "musical traditions Swat Chitral",
    "artisanal craft traditions north",
    "village festivals and rituals",
    "storytelling culture Pakistan",
    "nomadic tribes Pakistan",
    "shepherd communities northern Pakistan",
    "how to talk to craftsmen Pakistan",
    "pastoral lifestyle customs Pakistan",
    "pastoral lifestyle customs Pakistan",
    "cultural change in Swat",
    "tourism impact on local culture Pakistan",
    "youth perceptions rural Pakistan",
    "tech curiosity in villages Pakistan", 
    "how villagers see social media",
    "urban rural cultural differences Pakistan",
    "modern etiquette confusion Pakistan",
    "foreigners in remote areas Pakistan",
    "cross cultural blending Pakistan",
    "future of tourism KPK"
]
LIMIT_PER_KEYWORD = 20 

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
                    
                print(f"      ✅ Found {len(posts)} posts (New unique links: {len(new_links)})")
            else:
                print(f"      ❌ Failed (Status: {response.status_code})")

            time.sleep(2) # Be polite

        except Exception as e:
            print(f"      ⚠️ Error: {e}")

    # 3. Merge and Save
    if new_links:
        total_links = existing_links.union(new_links)
        print(f"\n💾 Merging {len(new_links)} new links with {len(existing_links)} old ones...")
        
        # FIX 2: Use utf-8 encoding for writing too
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            for link in total_links:
                f.write(link + "\n")
        
        print(f"✅ Harvest Complete! {OUTPUT_FILE} now has {len(total_links)} total links.")
    else:
        print("\n🎉 No new unique links found. Your list is already up to date.")

if __name__ == "__main__":
    harvest_links()