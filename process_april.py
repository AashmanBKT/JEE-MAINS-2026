import fitz
import re
import os
import glob
import json

base_dir = r'C:\PIPO\Abhik'
out_dir = os.path.join(base_dir, 'webapp')
os.makedirs(os.path.join(out_dir, 'static', 'papers'), exist_ok=True)

# shifts are the subdirectories like "2 Apr - 1st"
shifts = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and 'Apr' in d]

for shift in shifts:
    shift_dir = os.path.join(base_dir, shift)
    out_shift_dir = os.path.join(out_dir, 'static', 'papers', shift)
    os.makedirs(out_shift_dir, exist_ok=True)
    
    pdf_files = glob.glob(os.path.join(shift_dir, '*.pdf'))
    for pdf_path in pdf_files:
        basename = os.path.basename(pdf_path)
        subject = 'Physics'
        if '4' in basename:
            subject = 'Chemistry'
        elif '5' in basename:
            subject = 'Mathematics'
            
        doc = fitz.open(pdf_path)
        
        # 2. Redact
        for page in doc:
            text_instances = page.search_for("Ans.")
            for inst in text_instances:
                rect = fitz.Rect(inst.x0, inst.y0, inst.x0 + 150, inst.y1)
                page.add_redact_annot(rect, fill=(1,1,1))
            page.apply_redactions()
            
        out_pdf_path = os.path.join(out_shift_dir, basename)
        doc.save(out_pdf_path)
        doc.close()
        print(f"Processed {shift} - {subject}")

print("Done processing April PDFs for redaction!")
