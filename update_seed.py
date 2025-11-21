import csv
import os

def update_seed_file(new_clinics, seed_file="clinic_seed.csv"):
    """
    Appends new clinics to the seed file, avoiding duplicates based on URL.
    """
    existing_urls = set()
    
    # Read existing URLs
    if os.path.exists(seed_file):
        with open(seed_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('url'):
                    existing_urls.add(row['url'].strip())
    
    # Append new clinics
    file_exists = os.path.exists(seed_file)
    mode = 'a' if file_exists else 'w'
    
    with open(seed_file, mode, newline='', encoding='utf-8') as f:
        fieldnames = ['id', 'name', 'url', 'city']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
            
        added_count = 0
        for clinic in new_clinics:
            url = clinic.get('url', '').strip()
            if url and url not in existing_urls:
                writer.writerow({
                    'id': clinic.get('id', ''),
                    'name': clinic.get('name', ''),
                    'url': url,
                    'city': clinic.get('city', '')
                })
                existing_urls.add(url)
                added_count += 1
                
    print(f"Added {added_count} new clinics to {seed_file}")

if __name__ == "__main__":
    # Example usage or manual run
    pass
