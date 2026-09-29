import fitz
import re
import os
import glob
import json
from PIL import Image
import io

base_dir = r'C:\PIPO\Abhik'
out_dir = os.path.join(base_dir, 'webapp')
static_dir = os.path.join(out_dir, 'static', 'questions')
os.makedirs(static_dir, exist_ok=True)

answers_db = json.load(open(os.path.join(out_dir, 'answers.json')))
shifts = list(answers_db.keys())

def extract_all_questions_from_pdf(pdf_path, out_folder):
    doc = fitz.open(pdf_path)
    
    # 1. Find all text blocks and sort them by page, then column (x0), then y0
    # Wait, PyMuPDF's blocks are already somewhat sorted.
    # We will identify all question start positions.
    q_pattern = re.compile(r'(?:^|\n)\s*(\d+)\.')
    
    questions = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]
        
        # filter text blocks
        t_blocks = [b for b in blocks if "lines" in b]
        
        for b in t_blocks:
            # Join lines with newlines so we can match ^ correctly
            text = "\n".join(["".join([s["text"] for s in l["spans"]]) for l in b["lines"]]).strip()
            match = q_pattern.search(text)
            if match:
                q_num = match.group(1)
                
                # To get the exact y0 of the line containing the question number, we can find the line:
                q_y0 = b["bbox"][1]
                for l in b["lines"]:
                    line_text = "".join([s["text"] for s in l["spans"]]).strip()
                    if re.search(r'^\s*'+q_num+r'\.', line_text):
                        q_y0 = l["bbox"][1]
                        break
                        
                x0, _, x1, _ = b["bbox"]
                col = 0 if x0 < 300 else 1
                questions.append({
                    "q_num": q_num,
                    "page": page_num,
                    "col": col,
                    "y0": q_y0
                })
                
    # Now we have the start of every question.
    # The end of a question is the start of the next question.
    # If the next question is in the same column, it ends at next_y0.
    # If the next question is in the next column/page, it ends at the bottom of the current column,
    # and continues from the top of the next column/page until the next question starts.
    # This means a question can consist of 1 or 2 (or more) crops!
    
    images_saved = []
    for i, q in enumerate(questions):
        q_num = q["q_num"]
        
        # Determine the sequence of columns to crop
        crops = []
        
        curr_page = q["page"]
        curr_col = q["col"]
        curr_y0 = q["y0"]
        
        next_q = questions[i+1] if i+1 < len(questions) else None
        
        while True:
            # We need to crop from (curr_page, curr_col, curr_y0) to somewhere.
            page = doc[curr_page]
            crop_x0 = 0 if curr_col == 0 else 300
            crop_x1 = 300 if curr_col == 0 else page.rect.width
            
            # Where does this crop end?
            if next_q and next_q["page"] == curr_page and next_q["col"] == curr_col:
                # Ends before next question
                crop_y1 = next_q["y0"]
                rect_y0 = max(0, curr_y0 - 5)
                rect_y1 = min(page.rect.height, crop_y1 + 5)
                if rect_y1 > rect_y0:
                    rect = fitz.Rect(crop_x0, rect_y0, crop_x1, rect_y1)
                    pix = page.get_pixmap(clip=rect, dpi=150)
                    crops.append(pix)
                break
            else:
                # Ends at bottom of column
                # Find the max y1 of blocks in this column
                max_y1 = curr_y0
                blocks = page.get_text("dict")["blocks"]
                for b in blocks:
                    if "lines" not in b: continue
                    bx0, by0, bx1, by1 = b["bbox"]
                    # Ignore header and footer
                    if by0 > 750 or by1 < 70:
                        continue
                    b_col = 0 if bx0 < 300 else 1
                    if b_col == curr_col and by1 > max_y1:
                        max_y1 = by1
                
                crop_y1 = max_y1 + 10
                rect_y0 = max(0, curr_y0 - 5)
                rect_y1 = min(page.rect.height, crop_y1)
                if rect_y1 > rect_y0:
                    rect = fitz.Rect(crop_x0, rect_y0, crop_x1, rect_y1)
                    pix = page.get_pixmap(clip=rect, dpi=150)
                    crops.append(pix)
                
                # Move to next column
                curr_col += 1
                if curr_col > 1:
                    curr_col = 0
                    curr_page += 1
                    if curr_page >= len(doc):
                        break
                
                curr_y0 = 70
                
                # If we passed the next question (which shouldn't happen with the condition), break
                if not next_q:
                    # If this is the last question, we just crop to the end of the current column
                    break
                    
        # Stitch crops together vertically
        pil_images = []
        for pix in crops:
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            pil_images.append(img)
            
        if pil_images:
            total_height = sum(img.height for img in pil_images)
            max_width = max(img.width for img in pil_images)
            
            stitched = Image.new("RGB", (max_width, total_height), "white")
            y_offset = 0
            for img in pil_images:
                stitched.paste(img, (0, y_offset))
                y_offset += img.height
                
            out_name = f"q_{q_num}.png"
            stitched.save(os.path.join(out_folder, out_name))
            images_saved.append(out_name)
            
    doc.close()
    return images_saved


for shift in shifts:
    print("Processing", shift)
    shift_dir = os.path.join(base_dir, 'webapp', 'static', 'papers', shift)
    # wait, the redacted pdfs are in static/papers/shift
    # let's use the redacted ones so answers are hidden!
    out_shift_dir = os.path.join(static_dir, shift)
    os.makedirs(out_shift_dir, exist_ok=True)
    
    for pdf_path in glob.glob(os.path.join(shift_dir, '*.pdf')):
        basename = os.path.basename(pdf_path)
        subject = 'Physics'
        if 'Chemistry' in basename:
            subject = 'Chemistry'
        elif 'Mathematics' in basename:
            subject = 'Mathematics'
            
        subj_dir = os.path.join(out_shift_dir, subject)
        os.makedirs(subj_dir, exist_ok=True)
        
        extract_all_questions_from_pdf(pdf_path, subj_dir)

print("Done extracting questions!")
