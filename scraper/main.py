import asyncio
import os
import json
import google.generativeai as genai
from playwright.async_api import async_playwright
from urllib.parse import urlparse

# Configure Gemini
# Ensure GEMINI_API_KEY is set in your environment variables
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

async def analyze_clinic_status(text):
    """
    Analyzes the provided text using Gemini to determine if the clinic is accepting new patients.
    Enhanced to extract languages as an array.
    """
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        prompt = f"""
        Analyze the following text from a clinic's website (potentially from multiple pages including 'Contact', 'About', 'New Patients', 'Team') and extract the following information.
        
        CRITICAL INSTRUCTIONS FOR STATUS:
        - "OPEN": ONLY if the text EXPLICITLY states they are currently accepting new patients for family practice/primary care (e.g., "Accepting new patients", "Register now", "New patients welcome").
        - "WAITLIST": If they are accepting registrations ONLY for a waitlist.
        - "CLOSED": If they state they are not accepting, full, or only taking referrals for specialists (unless it's a primary care referral).
        - "UNCERTAIN": If there is no clear information.
        
        *PRIORITY*: Give higher weight to information found in sections explicitly labeled "New Patients" or "Register" over general "Contact" info.

        CRITICAL INSTRUCTIONS FOR LANGUAGES:
        - Extract ALL languages spoken at the clinic as a JSON array.
        - Look for phrases like "We speak...", "Services available in...", "Languages:", or doctor bios mentioning languages.
        - If NO specific languages are mentioned, default to ["English"].
        - Format as a JSON array of strings: ["English", "French", "Mandarin"]
        - Common languages to look for: English, French, Mandarin, Cantonese, Spanish, Arabic, Punjabi, Urdu, Hindi, Tamil, etc.

        Respond ONLY with a JSON object in the following format:
        {{
            "clinic_name": "Name of the clinic",
            "address": "Full address if available",
            "district": "City or neighborhood (e.g. Toronto, Scarborough)",
            "phone_number": "Phone number",
            "remaining_vacancy": "Number of spots or 'Unknown'",
            "languages": ["English", "French"],
            "status": "OPEN", "CLOSED", "WAITLIST", or "UNCERTAIN",
            "reason": "Brief explanation of why",
            "evidence": "The EXACT sentence or phrase from the text that led to this decision"
        }}

        Text Context (from multiple pages):
        {text[:25000]}
        """
        response = await model.generate_content_async(prompt)
        
        # Clean up response to ensure it's valid JSON
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:-3]
        elif response_text.startswith("```"):
            response_text = response_text[3:-3]
        
        result = json.loads(response_text)
        
        # Ensure languages is always an array
        if 'languages' in result:
            if isinstance(result['languages'], str):
                # Convert string to array
                result['languages'] = [lang.strip() for lang in result['languages'].split(',')]
        else:
            result['languages'] = ['English']
            
        return result
    except Exception as e:
        return {"status": "ERROR", "reason": f"Analysis failed: {str(e)}", "languages": ["English"]}

async def crawl_clinic(url):
    """
    Deep research: Crawls the main URL and up to 3 relevant sub-pages to gather comprehensive context.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Keywords to find relevant sub-pages
        KEYWORDS = ['contact', 'about', 'doctors', 'team', 'new-patient', 'register', 'physician', 'staff', 'services']
        
        combined_text = ""
        visited_urls = set()
        
        try:
            # 1. Visit Main Page
            page = await context.new_page()
            print(f"  🔍 Main: {url}")
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            main_content = await page.evaluate("document.body.innerText")
            combined_text += f"\n=== MAIN PAGE ({url}) ===\n{main_content}\n"
            visited_urls.add(url)
            
            # 2. Extract relevant links
            links = await page.evaluate("""
                Array.from(document.querySelectorAll('a')).map(a => ({
                    href: a.href,
                    text: a.innerText.toLowerCase()
                }))
            """)
            
            # Filter links: must be internal (same domain) and contain keywords
            base_domain = urlparse(url).netloc
            relevant_links = []
            
            for link in links:
                href = link['href']
                text = link['text']
                
                # Skip invalid links
                if not href or href.startswith('javascript') or href.startswith('mailto') or href.startswith('tel'):
                    continue
                    
                parsed_href = urlparse(href)
                if parsed_href.netloc and parsed_href.netloc != base_domain:
                    continue  # Skip external links
                
                # Check keywords in URL or Link Text
                if any(kw in href.lower() or kw in text for kw in KEYWORDS):
                    # Normalize URL (remove fragments)
                    full_url = href.split('#')[0]
                    if full_url not in visited_urls and full_url not in relevant_links:
                        relevant_links.append(full_url)
            
            # Limit to top 3 links
            targets = relevant_links[:3]
            
            if targets:
                print(f"  📄 Sub-pages: {len(targets)} found")
                
                # 3. Visit sub-pages in parallel
                tasks = []
                for target_url in targets:
                    visited_urls.add(target_url)
                    tasks.append(fetch_page_text(context, target_url))
                
                sub_page_contents = await asyncio.gather(*tasks)
                
                for i, content in enumerate(sub_page_contents):
                    if content:
                        combined_text += f"\n=== SUB-PAGE ({targets[i]}) ===\n{content}\n"
            
            await page.close()
            return combined_text
            
        except Exception as e:
            print(f"  ❌ Error crawling {url}: {e}")
            return combined_text if combined_text else None
        finally:
            await browser.close()

async def fetch_page_text(context, url):
    """Helper to fetch text from a single page"""
    page = await context.new_page()
    try:
        print(f"    ↳ {url}")
        await page.goto(url, timeout=20000, wait_until="domcontentloaded")
        return await page.evaluate("document.body.innerText")
    except Exception as e:
        print(f"      Failed: {e}")
        return None
    finally:
        await page.close()

def check_preferences(result):
    """
    Checks if the result matches the user's preferred languages and areas.
    Returns True if it matches (or if no preferences are set), False otherwise.
    """
    pref_langs = os.environ.get("PREFERRED_LANGUAGES")
    pref_areas = os.environ.get("PREFERRED_AREAS")

    # Check Language
    if pref_langs:
        clinic_langs = result.get('languages', [])
        if isinstance(clinic_langs, str):
            clinic_langs = [clinic_langs]
        
        # Normalize
        clinic_langs_lower = [l.lower() for l in clinic_langs]
        user_langs = [l.strip().lower() for l in pref_langs.split(',')]
        
        # Check if ANY preferred language matches
        if clinic_langs_lower and 'unknown' not in clinic_langs_lower:
            match = any(u_lang in c_lang for u_lang in user_langs for c_lang in clinic_langs_lower)
            if not match:
                return False

    # Check Area/District
    if pref_areas:
        clinic_district = result.get('district', '').lower()
        areas_list = [a.strip().lower() for a in pref_areas.split(',')]
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
    """Updates a single clinic in Firestore immediately and returns old status"""
    if not db:
        return None

    try:
        collection_ref = db.collection('clinics')
        
        # Use ID from seed data if available
        doc_id = data.get('id')
        if not doc_id:
            doc_id = url.replace("https://", "").replace("http://", "").replace("/", "_").replace(".", "_")

        doc_ref = collection_ref.document(doc_id)
        
        # Get old status before updating
        old_doc = doc_ref.get()
        old_status = old_doc.to_dict().get('status') if old_doc.exists else None
        
        toronto_time = datetime.now(ZoneInfo("America/Toronto"))
        
        # Ensure languages is stored as an array in Firestore
        languages = data.get('languages', ['English'])
        if isinstance(languages, str):
            languages = [l.strip() for l in languages.split(',')]
        
        doc_data = {
            "name": data.get('clinic_name', 'Unknown Clinic'),
            "address": data.get('address', 'N/A'),
            "district": data.get('district', 'N/A'),
            "phone": data.get('phone_number', 'N/A'),
            "status": data.get('status', 'UNKNOWN'),
            "updatedAt": toronto_time,
            "url": url,
            "vacancy": data.get('remaining_vacancy', 'N/A'),
            "languages": languages,  # Store as array
            "evidence": data.get('evidence', 'N/A'),
            "reason": data.get('reason', 'N/A'),  # Added missing reason field
            "province": data.get('province', 'N/A')
        }
        
        doc_ref.set(doc_data, merge=True)
        print(f"   🔥 Firestore: {data.get('status')} | Languages: {', '.join(languages)}")
        
        return old_status
        
    except Exception as e:
        print(f"   ❌ Firestore error: {e}")
        return None

async def send_alert_batch(clinic_name, clinic_url, clinic_city, clinic_languages, old_status=None):
    """
    Send SMS alerts to all premium users who have selected this clinic's location.
    Only sends for status flips (CLOSED/WAITLIST → OPEN).
    """
    if not db or not notifier:
        print(f"  📧 Alert batch skipped (DB or notifier not available)")
        return
    
    try:
        # Query all premium users
        users_ref = db.collection('users')
        premium_users = users_ref.where('isPremium', '==', True).stream()
        
        alert_count = 0
        
        for user_doc in premium_users:
            user_data = user_doc.to_dict()
            user_id = user_doc.id
            user_areas = user_data.get('areas', [])
            user_languages = user_data.get('languages', [])
            user_phone = user_data.get('phoneNumber')  # Fixed: was 'phone', should be 'phoneNumber'
            
            # Skip if no phone number
            if not user_phone:
                continue
            
            # Check if user has selected this location
            location_match = False
            if user_areas:
                for area in user_areas:
                    # Match logic:
                    # 1. Exact city match (e.g., user=Toronto, clinic=Toronto)
                    # 2. User selected "Ontario Wide" or "All Locations" (matches any clinic)
                    # 3. Clinic is "Ontario Wide" (matches any ON city like Toronto, Mississauga, etc.)
                    # 4. Partial match (clinic city contains user area or vice versa)
                    if (area.lower() == clinic_city.lower() or 
                        'ontario wide' in area.lower() or 
                        'all locations' in area.lower() or
                        'ontario wide' in clinic_city.lower() or  # Clinic is Ontario-wide, matches any ON user
                        clinic_city.lower() in area.lower() or
                        area.lower() in clinic_city.lower()):
                        location_match = True
                        break
            
            if not location_match:
                continue
            
            # Check language match (if user has language preferences)
            language_match = True
            if user_languages and clinic_languages:
                language_match = any(
                    any(user_lang.lower() in clinic_lang.lower() 
                        for clinic_lang in clinic_languages)
                    for user_lang in user_languages
                )
            
            if not language_match:
                continue
            
            # Send SMS to this user
            # Include status flip information if available
            status_info = ""
            if old_status:
                status_info = f" ({old_status} → OPEN)"
            elif old_status is None:
                status_info = " (NEW → OPEN)"
            
            msg = f"🚨 CLINIC NOW OPEN!{status_info} 🚨\n{clinic_name}\n{clinic_city}\n{clinic_url}"
            
            # Use Twilio to send to this specific user's phone
            try:
                if notifier.enabled and notifier.client:
                    sms_message = notifier.client.messages.create(
                        body=msg,
                        from_=notifier.from_number,
                        to=user_phone
                    )
                    print(f"  📱 SMS sent to {user_phone}: {sms_message.sid}")
                    alert_count += 1
                    
                    # Log to Firestore
                    db.collection('notifications').add({
                        'clinicName': clinic_name,
                        'clinicUrl': clinic_url,
                        'userId': user_id,
                        'phone': user_phone,
                        'type': 'STATUS_FLIP_ALERT',
                        'sid': sms_message.sid,
                        'timestamp': firestore.SERVER_TIMESTAMP
                    })
                else:
                    print(f"  [LOG ONLY] Would send to {user_phone}: {msg}")
                    alert_count += 1
                    
            except Exception as e:
                print(f"  ❌ Failed to send SMS to {user_phone}: {e}")
        
        if alert_count > 0:
            print(f"  ✅ Sent {alert_count} targeted alert(s)")
        else:
            print(f"  ℹ️  No matching users for {clinic_city}")
            
    except Exception as e:
        print(f"  ❌ Error in send_alert_batch: {e}")

async def main():
    # Read target URLs from CSV
    targets = []
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
        print(f"📋 Loaded {len(targets)} clinics from {seed_file}")
    except FileNotFoundError:
        print(f"❌ Error: {seed_file} not found.")
        return

    results = {}

    for target in targets:
        url = target['url']
        clinic_id = target['id']
        
        print(f"\n🕷️  Crawling: {url}")
        # Use deep research crawling
        text_content = await crawl_clinic(url)
        
        if text_content:
            print(f"  🧠 Analyzing...")
            result = await analyze_clinic_status(text_content)
            
            # Add ID and location from seed to result
            result['id'] = clinic_id
            if target.get('city'):
                result['district'] = target['city']
            if target.get('province'):
                result['province'] = target['province']
            
            results[url] = result
            status = result.get('status', 'UNKNOWN')
            print(f"  ✅ Status: {status}")
            
            # Update Firestore and get old status
            old_status = await update_clinic_in_firestore(url, result)
            
            # Detect status flip: CLOSED/WAITLIST/UNCERTAIN → OPEN
            new_status = result.get('status', 'UNKNOWN')
            
            # Condition 1: New clinic (old_status is None) AND new_status is OPEN
            # Condition 2: Status flip (old_status was not OPEN) AND new_status is OPEN
            if new_status == "OPEN" and (old_status is None or old_status != "OPEN"):
                clinic_name = result.get('clinic_name', 'Unknown Clinic')
                clinic_city = result.get('district', 'Unknown')
                clinic_languages = result.get('languages', ['English'])
                
                print(f"  🔔 Status flip detected: {old_status} → {new_status}")
                await send_alert_batch(clinic_name, url, clinic_city, clinic_languages, old_status)
                
        else:
            results[url] = {"status": "ERROR", "reason": "Failed to retrieve content", "languages": ["English"]}
            print(f"  ❌ Failed to scrape")

    print("\n" + "="*60)
    print("📊 SCRAPING COMPLETE")
    print("="*60)

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
                # Format languages array as comma-separated string for CSV
                langs = data.get('languages', ['English'])
                if isinstance(langs, list):
                    langs = ", ".join(langs)
                
                writer.writerow({
                    'Clinic Name': data.get('clinic_name', 'N/A'),
                    'Address': data.get('address', 'N/A'),
                    'District': data.get('district', 'N/A'),
                    'Phone': data.get('phone_number', 'N/A'),
                    'Vacancy': data.get('remaining_vacancy', 'N/A'),
                    'Languages': langs,
                    'Status': data.get('status', 'UNKNOWN'),
                    'Reason': data.get('reason', 'No reason provided'),
                    'Evidence': data.get('evidence', 'N/A'),
                    'URL': url
                })
        print(f"\n💾 Results saved to: {file_path}")
    except Exception as e:
        print(f"\n❌ Error saving to CSV: {e}")

if __name__ == "__main__":
    asyncio.run(main())
