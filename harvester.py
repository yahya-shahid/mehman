import requests
import json
import time

# --- CONFIGURATION ---
OUTPUT_FILE = 'links.txt'
SUBREDDIT = 'pakistan'  # You can change this to 'travel' or 'solotravel' later
KEYWORDS = [
    "travel advice",
    "safety for foreigners",
    "best food places",
    "northern areas itinerary",
    "scams to avoid",
    "hotels and guest houses",
    "transport uber indrive",
    "women safety travel",
    "cultural etiquette",
    "shopping guide",
    "Swat travel tips",
    "Mingora safety",
    "Kalam itinerary",
    "Malam Jabba guidance",
    "Swat culture basics",
    "Hunza valley itinerary",
    "Karimabad food places",
    "Attabad Lake guide",
    "Passu cones photography tips",
    "Kalash etiquette",
    "Chitral valley travel advice",
    "Skardu hotels",
    "Deosai plains safety",
    "Shangrila guide",
    "responsible tourism Pakistan",
    "eco friendly travel tips",
    "community based tourism",
    "protecting local heritage",
    "waste management awareness",
    "supporting local businesses",
    "location triggered etiquette advice",
    "real time translation Urdu Pashto",
    "village ambassador persona",
    "foreign tourist assistant persona",
    "culturally aware chatbot",
    "offline voice assistant tourism",
    "community centric AI",
    "cross cultural mediation",
    "how to interact with villagers",
    "dealing with crowd curiosity",
    "polite refusal phrases",
    "how to ask for help politely",
    "explaining photography to locals",
    "bridging cultural gaps",
    "respectful conversation tips",
    "rural interaction coaching",
    "best hiking trails Pakistan",
    "hidden gems northern Pakistan",
    "local festivals calendar",
    "cultural experiences",
    "handicrafts shopping guide",
    "markets and bazaars",
    "souvenirs to buy",
    "adventure sports Pakistan",
    "historical sites guide",
    "hotels and guest houses",
    "homestay recommendations",
    "mountain lodges Pakistan",
    "best food spots Swat Hunza",
    "halal food guide",
    "street food checklist",
    "vegetarian options Pakistan",
    "tea spots and dhabas",
    "local cuisine introduction",
    "transport options Pakistan",
    "Uber Careem InDrive guide",
    "renting a car Pakistan",
    "driver recommendation",
    "jeep booking northern areas",
    "public transport schedule",
    "train travel Pakistan",
    "airport pickup advice",
    "petrol stations remote areas",
    "travel safety Pakistan",
    "women solo traveler safety",
    "emergency contacts Pakistan",
    "safe neighborhoods",
    "police assistance for tourists",
    "security updates KPK",
    "scams and fraud alerts",
    "trekking risks and precautions",
    "road safety northern areas",
    "hospitality customs",
    "Pashtunwali etiquette",
    "hujra manners",
    "gift giving norms",
    "how to greet locals",
    "photography etiquette",
    "mosque visit etiquette",
    "village interaction protocol",
    "language phrases basic Urdu Pashto",
    "respecting local traditions",
    "dress code Pakistan",
    "trip planning Pakistan",
    "itinerary builder",
    "northern areas route planning",
    "backpacking Pakistan",
    "seasonal travel tips",
    "weather based travel advice",
    "visa on arrival guidance",
    "border crossing information",
    "solo travel guide",
    "budget travel Pakistan"
]
LIMIT_PER_KEYWORD = 20  # How many threads to grab per keyword (Max is usually 100)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def harvest_links():
    unique_links = set()
    print(f"🚜 Starting Harvest on r/{SUBREDDIT}...")

    for keyword in KEYWORDS:
        print(f"   🔎 Searching for: '{keyword}'...")
        
        # Reddit Search JSON Endpoint
        search_url = f"https://www.reddit.com/r/{SUBREDDIT}/search.json?q={keyword}&restrict_sr=1&limit={LIMIT_PER_KEYWORD}&sort=relevance"
        
        try:
            response = requests.get(search_url, headers=HEADERS)
            
            if response.status_code == 200:
                data = response.json()
                posts = data['data']['children']
                
                for post in posts:
                    # Construct the full URL
                    permalink = post['data']['permalink']
                    full_url = f"https://www.reddit.com{permalink}"
                    unique_links.add(full_url)
                    
                print(f"      ✅ Found {len(posts)} links.")
            else:
                print(f"      ❌ Failed (Status: {response.status_code})")

            # Sleep to be polite to Reddit
            time.sleep(2)

        except Exception as e:
            print(f"      ⚠️ Error: {e}")

    # Save to file
    print(f"\n💾 Saving {len(unique_links)} unique links to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w') as f:
        for link in unique_links:
            f.write(link + "\n")
            
    print("✅ Harvest Complete! Now run 'scraper_no_api.py'.")

if __name__ == "__main__":
    harvest_links()