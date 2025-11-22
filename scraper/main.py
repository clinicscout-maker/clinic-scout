import asyncio
import os
import json
import google.generativeai as genai
from playwright.async_api import async_playwright

# Configure Gemini
# Ensure GEMINI_API_KEY is set in your environment variables
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

async def analyze_clinic_status(text):
    """
    Analyzes the provided text using Gemini to determine if the clinic is accepting new patients.
    """
    try:
        model = genai.GenerativeModel('gemini-flash-latest') # Using a standard model, adjust if needed
        prompt = f"""
        Analyze the following text from a clinic's website and extract the following information.
        
        CRITICAL INSTRUCTIONS FOR STATUS:
        - "OPEN": ONLY if the text EXPLICITLY states they are currently accepting new patients for family practice/primary care (e.g., "Accepting new patients", "Register now", "New patients welcome").
        - "WAITLIST": If they are accepting registrations ONLY for a waitlist.
        - "CLOSED": If they state they are not accepting, full, or only taking referrals for specialists (unless it's a primary care referral).
        - "UNCERTAIN": If there is no clear information.

        Respond ONLY with a JSON object in the following format:
        {{
            "clinic_name": "Name of the clinic",
            "address": "Full address if available",
            "district": "City or neighborhood (e.g. Toronto, Scarborough)",
            "phone_number": "Phone number",
            "remaining_vacancy": "Number of spots or 'Unknown'",
            "languages": "List of languages spoken or 'Unknown'",
            "status": "OPEN", "CLOSED", "WAITLIST", or "UNCERTAIN",
            "reason": "Brief explanation of why",
            "evidence": "The EXACT sentence or phrase from the text that led to this decision"
        }}

        Text:
        {text[:15000]} # Increased limit slightly for better context
        """
        response = await model.generate_content_async(prompt)
        
        # Clean up response to ensure it's valid JSON (sometimes models add markdown)
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:-3]
        
        return json.loads(response_text)
    except Exception as e:
        return {"status": "ERROR", "reason": f"Analysis failed: {str(e)}"}

async def scrape_clinic(url):
    """
    Visits the URL using Playwright and extracts the body text.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = await context.new_page()
        
        try:
            # Go to URL with a timeout
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            
            # Extract text
            content = await page.evaluate("document.body.innerText")
            
            return content
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
        finally:
            await browser.close()

def check_preferences(result):
    """
    Checks if the result matches the user's preferred languages and areas.
    Returns True if it matches (or if no preferences are set), False otherwise.
    """
    pref_langs = os.environ.get("PREFERRED_LANGUAGES")
    pref_areas = os.environ.get("PREFERRED_AREAS")

    # Check Language
    if pref_langs:
        clinic_langs = result.get('languages', '').lower()
        # If clinic languages are unknown, we might want to notify anyway, or be strict.
        # Let's be permissive if unknown, but strict if known.
        if clinic_langs != 'unknown':
            langs_list = [l.strip().lower() for l in pref_langs.split(',')]
            # Check if ANY preferred language is in the clinic's languages
            if not any(lang in clinic_langs for lang in langs_list):
                return False

    # Check Area/District
    if pref_areas:
        clinic_district = result.get('district', '').lower()
        areas_list = [a.strip().lower() for a in pref_areas.split(',')]
        # Check if the clinic's district contains any of the preferred areas
        if not any(area in clinic_district for area in areas_list):
            return False

    return True

# Initialize Firebase Global
db = None
notifier = None

try:
    import firebase_admin
    from firebase_admin import credentials
    from firebase_admin import firestore
    from datetime import datetime
    try:
        from zoneinfo import ZoneInfo
    except ImportError:
        from backports.zoneinfo import ZoneInfo

    # Check for service account key
    key_path = "serviceAccountKey.json"
    if not os.path.exists(key_path):
        key_path = "../serviceAccountKey.json"
    
    if os.path.exists(key_path):
        if not firebase_admin._apps:
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("✅ Firebase initialized successfully")
        
        # Initialize notifier with Firestore client
        try:
            import sys
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from notifications import NotificationManager
            notifier = NotificationManager(db=db)
            print("✅ NotificationManager initialized with Firestore logging")
        except ImportError as e:
            print(f"⚠️ Failed to import NotificationManager: {e}")
    else:
        print("⚠️ serviceAccountKey.json not found. Firestore updates disabled.")

except ImportError:
    print("⚠️ firebase-admin not installed. Firestore updates disabled.")

async def update_clinic_in_firestore(url, data):
    """Updates a single clinic in Firestore immediately"""
    if not db:
        return

    try:
        collection_ref = db.collection('clinics')
        
        # Create a unique ID based on URL (same logic as before)
        # BUT wait, seed_firebase.py used 'id' column from CSV.
        # The scraper uses URL-based ID. This creates DUPLICATES or mismatched updates.
        # We need to match the ID used in seeding if possible.
        # Since we don't have the ID here easily (unless we pass it), we might have an issue.
        # However, seed_firebase.py used the 'id' column.
        # The scraper reads the CSV. Let's modify main() to read ID too.
        
        # For now, let's use the URL-based ID as a fallback, but ideally we pass the ID.
        # I will modify main() to pass ID.
        
        # Fallback ID generation (legacy)
        doc_id = url.replace("https://", "").replace("http://", "").replace("/", "_").replace(".", "_")
        
        # If data has 'id', use that
        if 'id' in data and data['id']:
            doc_id = data['id']

        doc_ref = collection_ref.document(doc_id)
        
        toronto_time = datetime.now(ZoneInfo("America/Toronto"))
        
        doc_data = {
            "name": data.get('clinic_name', 'Unknown Clinic'),
            "address": data.get('address', 'N/A'),
            "district": data.get('district', 'N/A'),
            "phone": data.get('phone_number', 'N/A'),
            "status": data.get('status', 'UNKNOWN'),
            "updatedAt": toronto_time,
            "url": url,
            "vacancy": data.get('remaining_vacancy', 'N/A'),
            "languages": data.get('languages', 'N/A'),
            "evidence": data.get('evidence', 'N/A'),
            "province": data.get('province', 'N/A')
        }
        
        doc_ref.set(doc_data, merge=True)
        print(f"   🔥 Updated Firestore: {data.get('status')} (ID: {doc_id})")
        
    except Exception as e:
        print(f"   ❌ Failed to update Firestore: {e}")

async def main():
    # Read target URLs from CSV
    targets = [] # List of dicts {url, id}
    seed_file = os.environ.get("SEED_FILE", "clinic_seed.csv")
    
    try:
        import csv
        with open(seed_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('url'):
                    targets.append({
                        'url': row['url'].strip(),
                        'id': row.get('id', '').strip(),
                        'city': row.get('city', '').strip(),
                        'province': row.get('province', '').strip()
                    })
        print(f"Loaded {len(targets)} clinics from {seed_file}")
    except FileNotFoundError:
        print(f"Error: {seed_file} not found.")
        return

    results = {}

    for target in targets:
        url = target['url']
        clinic_id = target['id']
        
        print(f"Scraping {url}...")
        text_content = await scrape_clinic(url)
        
        if text_content:
            print(f"Analyzing content for {url}...")
            result = await analyze_clinic_status(text_content)
            
            # Add ID and location from seed to result for Firestore update
            result['id'] = clinic_id
            if target.get('city'):
                result['district'] = target['city']
            if target.get('province'):
                result['province'] = target['province']
            
            results[url] = result
            status = result.get('status', 'UNKNOWN')
            print(f"Result for {url}: {status}")
            
            # Update Firestore IMMEDIATELY
            await update_clinic_in_firestore(url, result)
            
            # Send notification if OPEN and matches preferences
            if status == "OPEN":
                if check_preferences(result):
                    msg = f"🚨 OPEN CLINIC FOUND! 🚨\nName: {result.get('clinic_name')}\nDistrict: {result.get('district')}\nPhone: {result.get('phone_number')}\nURL: {url}"
                    # Pass clinic_id for logging (user_id would come from user preferences in production)
                    if notifier:
                        notifier.send_notification(msg, clinic_id=clinic_id, user_id="admin")
                else:
                    print(f"Skipping notification for {url} (Does not match preferences)")
                
        else:
            results[url] = {"status": "ERROR", "reason": "Failed to retrieve content"}
            print(f"Failed to scrape {url}")

    print("\nFinal Results:")
    # print(json.dumps(results, indent=2)) # Too verbose for 255 items

    # Save to CSV on Desktop
    import csv
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    desktop_path = os.path.expanduser("~/Desktop")
    filename = f"clinic_scout_{timestamp}.csv"
    file_path = os.path.join(desktop_path, filename)

    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Clinic Name', 'Address', 'District', 'Phone', 'Vacancy', 'Languages', 'Status', 'Reason', 'Evidence', 'URL']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for url, data in results.items():
                writer.writerow({
                    'Clinic Name': data.get('clinic_name', 'N/A'),
                    'Address': data.get('address', 'N/A'),
                    'District': data.get('district', 'N/A'),
                    'Phone': data.get('phone_number', 'N/A'),
                    'Vacancy': data.get('remaining_vacancy', 'N/A'),
                    'Languages': data.get('languages', 'N/A'),
                    'Status': data.get('status', 'UNKNOWN'),
                    'Reason': data.get('reason', 'No reason provided'),
                    'Evidence': data.get('evidence', 'N/A'),
                    'URL': url
                })
        print(f"\nResults saved to: {file_path}")
    except Exception as e:
        print(f"\nError saving to CSV: {e}")

if __name__ == "__main__":
    asyncio.run(main())
