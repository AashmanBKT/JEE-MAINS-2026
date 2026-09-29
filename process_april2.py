import fitz
import re
import os
import glob
import json

base_dir = r'C:\PIPO\Abhik'
out_dir = os.path.join(base_dir, 'webapp')

answers_db = json.load(open(os.path.join(out_dir, 'answers.json')))
locations_db = json.load(open(os.path.join(out_dir, 'locations.json')))

shifts = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and 'Apr' in d]

for shift in shifts:
    shift_dir = os.path.join(base_dir, shift)
    answers_db[shift] = {}
    locations_db[shift] = {}
    
    pdf_files = glob.glob(os.path.join(shift_dir, '*.pdf'))
    for pdf_path in pdf_files:
        basename = os.path.basename(pdf_path)
        subject = 'Physics'
        if '4' in basename:
            subject = 'Chemistry'
        elif '5' in basename:
            subject = 'Mathematics'
            
        doc = fitz.open(pdf_path)
        
        # Extract answers
        full_text = ""
        for page in doc:
            full_text += page.get_text()
            
        matches = re.findall(r'Ans\.\s*\(\s*([\d\.\-]+)\s*\)', full_text)
        answers_db[shift][subject] = matches
        
        # Extract locations
        locations = {}
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            for b in blocks:
                if "lines" not in b: continue
                text = "".join([s["text"] for l in b["lines"] for s in l["spans"]]).strip()
                match = re.match(r'^(\d+)\.', text)
                if match:
                    q_num = match.group(1)
                    if q_num not in locations:
                        locations[q_num] = {
                            "page": page_num + 1,
                            "y": b["bbox"][1]
                        }
        
        locations_db[shift][subject] = locations
        doc.close()

with open(os.path.join(out_dir, 'answers.json'), 'w') as f:
    json.dump(answers_db, f, indent=2)

with open(os.path.join(out_dir, 'locations.json'), 'w') as f:
    json.dump(locations_db, f, indent=2)

print("Updated answers.json and locations.json for April shifts")
