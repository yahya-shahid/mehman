import os
from google import genai

# Initialize client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

print("🔍 Checking available models for your API key...")

try:
    # List all models
    pager = client.models.list()
    
    found_any = False
    print("\n✅ You have access to these models:")
    print("-" * 30)
    
    for model in pager:
        # We only care about models that can generate text (chat)
        if "generateContent" in model.supported_generation_methods:
            # The API returns names like 'models/gemini-1.5-flash'. 
            # We strip 'models/' so you can copy-paste the clean name.
            clean_name = model.name.replace("models/", "")
            print(f"👉 {clean_name}")
            found_any = True
            
    if not found_any:
        print("⚠️ No text generation models found. Check your API key permissions.")
        
except Exception as e:
    print(f"❌ Error listing models: {e}")