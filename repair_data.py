#this file repairs the mehman_data.json file if it is corrupted or incomplete. and that usaully happens if the server flags your request and start playing with your requests.
import json
import os

INPUT_FILE = 'mehman_data.json'
OUTPUT_FILE = 'mehman_data_clean.json'

def repair_json():
    print(f"🔧 Inspecting {INPUT_FILE}...")
    
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            raw_data = f.read()
            
        # 1. Try standard load first
        try:
            data = json.loads(raw_data)
            print("   ✅ JSON is valid. No structural repair needed.")
        except json.JSONDecodeError:
            print("   ⚠️ JSON is corrupted (likely crashed mid-write). Attempting repair...")
            # Common crash error: Missing ']' at the end
            # We strip the last comma if it exists, then add ']'
            stripped_data = raw_data.strip()
            if stripped_data.endswith(','):
                stripped_data = stripped_data[:-1]
            if not stripped_data.endswith(']'):
                stripped_data += ']'
            
            try:
                data = json.loads(stripped_data)
                print("   ✅ Repair successful!")
            except json.JSONDecodeError:
                print("   ❌ Repair failed. The file is too damaged.")
                return

        # 2. Deduplicate (Remove accidental duplicates)
        unique_data = {}
        for entry in data:
            if entry['url'] not in unique_data:
                unique_data[entry['url']] = entry
        
        final_list = list(unique_data.values())
        
        # 3. Save clean version
        print(f"💾 Saving {len(final_list)} unique, clean threads to {OUTPUT_FILE}...")
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(final_list, f, indent=4, ensure_ascii=False)
            
        print("🚀 You are ready for the RAG Backend!")

    except FileNotFoundError:
        print(f"❌ Could not find {INPUT_FILE}.")

if __name__ == "__main__":
    repair_json()