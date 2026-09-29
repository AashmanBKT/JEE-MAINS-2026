import os
import shutil
import glob

base_dir = r'C:\PIPO\Abhik'
dest_dir = os.path.join(base_dir, 'webapp', 'static', 'originals')
os.makedirs(dest_dir, exist_ok=True)

shifts = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and ('Jan' in d or 'Apr' in d)]

for shift in shifts:
    src_shift_dir = os.path.join(base_dir, shift)
    dest_shift_dir = os.path.join(dest_dir, shift)
    os.makedirs(dest_shift_dir, exist_ok=True)
    
    pdfs = glob.glob(os.path.join(src_shift_dir, '*.pdf'))
    for pdf in pdfs:
        shutil.copy(pdf, dest_shift_dir)
        print(f"Copied {os.path.basename(pdf)} to {shift}")
print("Done!")
