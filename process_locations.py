import fitz
import re
import os
import glob
import json

base_dir = r'C:\PIPO\Abhik'
out_dir = os.path.join(base_dir, 'webapp')

locations_db = {}
shifts = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and 'Jan' in d]

for shift in shifts:
    shift_dir = os.path.join(base_dir, shift)
    locations_db[shift] = {}
    
    pdf_files = glob.glob(os.path.join(shift_dir, '*.pdf'))
    for pdf_path in pdf_files:
        basename = os.path.basename(pdf_path)
        subject = 'Physics'
        if 'Chemistry' in basename:
            subject = 'Chemistry'
        elif 'Mathematics' in basename:
            subject = 'Mathematics'
            
        doc = fitz.open(pdf_path)
        
        # We need to find the location for Q1 to Q30 (or whatever numbering is used)
        # Actually, the numbering in the PDFs is sometimes 1-25, 26-50, 51-75.
        # So we should just find ALL numbers followed by a dot at the start of a line.
        # But we know that in our webapp, we re-number them to 1-30 for each subject!
        # Wait, the answers.json has the REAL question numbers (like 51, 52...).
        # We should find the location of these REAL question numbers.
        
        # Let's read the real question numbers from our answers_db?
        # Wait, earlier I saved the answers as a LIST in process2.py!
        # So in the app, I map 1..20 to the first 20 in the list.
        # But I don't know the real question number from the list.
        
        # Let's extract questions by looking for numbers 1 to 90.
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
                            "page": page_num + 1, # 1-indexed for PDF.js
                            "y": b["bbox"][1] # y0
                        }
        
        locations_db[shift][subject] = locations
        doc.close()

with open(os.path.join(out_dir, 'locations.json'), 'w') as f:
    json.dump(locations_db, f, indent=2)

print("Created locations.json")
