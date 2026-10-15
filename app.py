from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os

app = Flask(__name__)

# Load answers
with open('answers.json', 'r') as f:
    answers_db = json.load(f)

# Load locations
with open('locations.json', 'r') as f:
    locations_db = json.load(f)

shifts = list(answers_db.keys())

# Percentile matrix based on user provided image
PERCENTILE_MATRIX = {
    '21 Jan - 1st': [(224, 99.9), (189, 99.5), (158, 99), (143, 98.5), (132, 98), (125, 97.5), (119, 97), (113, 96.5), (108, 96), (104, 95.5), (100, 95), (93, 94), (87, 93), (82, 92), (78, 91), (74, 90)],
    '21 Jan - 2nd': [(230, 99.9), (200, 99.5), (174, 99), (162, 98.5), (153, 98), (145, 97.5), (139, 97), (133, 96.5), (128, 96), (124, 95.5), (121, 95), (113, 94), (106, 93), (100, 92), (95, 91), (91, 90)],
    '22 Jan - 1st': [(243, 99.9), (212, 99.5), (186, 99), (173, 98.5), (163, 98), (156, 97.5), (149, 97), (143, 96.5), (138, 96), (134, 95.5), (129, 95), (121, 94), (114, 93), (108, 92), (102, 91), (97, 90)],
    '22 Jan - 2nd': [(219, 99.9), (184, 99.5), (154, 99), (140, 98.5), (130, 98), (122, 97.5), (116, 97), (110, 96.5), (105, 96), (101, 95.5), (97, 95), (89, 94), (83, 93), (78, 92), (74, 91), (70, 90)],
    '23 Jan - 1st': [(227, 99.9), (193, 99.5), (166, 99), (152, 98.5), (141, 98), (134, 97.5), (127, 97), (121, 96.5), (116, 96), (112, 95.5), (108, 95), (100, 94), (94, 93), (88, 92), (82, 91), (78, 90)],
    '23 Jan - 2nd': [(224, 99.9), (188, 99.5), (158, 99), (144, 98.5), (134, 98), (126, 97.5), (120, 97), (114, 96.5), (108, 96), (104, 95.5), (100, 95), (92, 94), (86, 93), (81, 92), (76, 91), (72, 90)],
    '24 Jan - 1st': [(232, 99.9), (200, 99.5), (174, 99), (160, 98.5), (149, 98), (141, 97.5), (134, 97), (128, 96.5), (123, 96), (119, 95.5), (115, 95), (107, 94), (101, 93), (96, 92), (91, 91), (87, 90)],
    '24 Jan - 2nd': [(236, 99.9), (205, 99.5), (178, 99), (164, 98.5), (154, 98), (146, 97.5), (138, 97), (132, 96.5), (127, 96), (123, 95.5), (119, 95), (112, 94), (105, 93), (99, 92), (94, 91), (89, 90)],
    '28 Jan - 1st': [(242, 99.9), (213, 99.5), (188, 99), (173, 98.5), (162, 98), (154, 97.5), (146, 97), (140, 96.5), (134, 96), (130, 95.5), (125, 95), (117, 94), (110, 93), (104, 92), (99, 91), (94, 90)],
    '28 Jan - 2nd': [(237, 99.9), (207, 99.5), (180, 99), (165, 98.5), (155, 98), (148, 97.5), (140, 97), (134, 96.5), (129, 96), (124, 95.5), (119, 95), (112, 94), (105, 93), (100, 92), (95, 91), (91, 90)],
    
    # Generic fallback for April shifts (using 24 Jan 1st as baseline until user provides specific matrix)
    '2 Apr - 1st': [(232, 99.9), (200, 99.5), (174, 99), (160, 98.5), (149, 98), (141, 97.5), (134, 97), (128, 96.5), (123, 96), (119, 95.5), (115, 95), (107, 94), (101, 93), (96, 92), (91, 91), (87, 90)],
    '2 Apr - 2nd': [(232, 99.9), (200, 99.5), (174, 99), (160, 98.5), (149, 98), (141, 97.5), (134, 97), (128, 96.5), (123, 96), (119, 95.5), (115, 95), (107, 94), (101, 93), (96, 92), (91, 91), (87, 90)],
    '4 Apr - 1st': [(232, 99.9), (200, 99.5), (174, 99), (160, 98.5), (149, 98), (141, 97.5), (134, 97), (128, 96.5), (123, 96), (119, 95.5), (115, 95), (107, 94), (101, 93), (96, 92), (91, 91), (87, 90)],
    '4 Apr - 2nd': [(232, 99.9), (200, 99.5), (174, 99), (160, 98.5), (149, 98), (141, 97.5), (134, 97), (128, 96.5), (123, 96), (119, 95.5), (115, 95), (107, 94), (101, 93), (96, 92), (91, 91), (87, 90)],
    '5 Apr - 1st': [(232, 99.9), (200, 99.5), (174, 99), (160, 98.5), (149, 98), (141, 97.5), (134, 97), (128, 96.5), (123, 96), (119, 95.5), (115, 95), (107, 94), (101, 93), (96, 92), (91, 91), (87, 90)],
    '5 Apr - 2nd': [(232, 99.9), (200, 99.5), (174, 99), (160, 98.5), (149, 98), (141, 97.5), (134, 97), (128, 96.5), (123, 96), (119, 95.5), (115, 95), (107, 94), (101, 93), (96, 92), (91, 91), (87, 90)],
    '6 Apr - 1st': [(232, 99.9), (200, 99.5), (174, 99), (160, 98.5), (149, 98), (141, 97.5), (134, 97), (128, 96.5), (123, 96), (119, 95.5), (115, 95), (107, 94), (101, 93), (96, 92), (91, 91), (87, 90)],
    '6 Apr - 2nd': [(232, 99.9), (200, 99.5), (174, 99), (160, 98.5), (149, 98), (141, 97.5), (134, 97), (128, 96.5), (123, 96), (119, 95.5), (115, 95), (107, 94), (101, 93), (96, 92), (91, 91), (87, 90)],
    '8 Apr - 2nd': [(232, 99.9), (200, 99.5), (174, 99), (160, 98.5), (149, 98), (141, 97.5), (134, 97), (128, 96.5), (123, 96), (119, 95.5), (115, 95), (107, 94), (101, 93), (96, 92), (91, 91), (87, 90)]
}

def get_percentile(score, shift):
    if shift not in PERCENTILE_MATRIX:
        return 0.0
    
    matrix = PERCENTILE_MATRIX[shift]
    
    # Check top bounds
    if score >= matrix[0][0]:
        return min(100.0, 99.9 + (100.0 - 99.9) * ((score - matrix[0][0]) / (300.0 - matrix[0][0] + 1e-5)))
        
    # Interpolate inside matrix bounds (down to 90 percentile)
    for i in range(len(matrix) - 1):
        upper_mark, upper_perc = matrix[i]
        lower_mark, lower_perc = matrix[i+1]
        
        if lower_mark <= score <= upper_mark:
            ratio = (score - lower_mark) / (upper_mark - lower_mark)
            return lower_perc + ratio * (upper_perc - lower_perc)
            
    # For scores below the matrix minimum (below 90 percentile)
    # Generic fallback based on user table
    generic_pts = [
        (70, 87.51), (61, 87.06), (60, 82.01), (51, 81.57),
        (50, 73.28), (41, 73.08), (40, 59.84), (31, 58.15),
        (30, 40.34), (21, 37.69), (20, 20.95), (10, 13.49), (0, 0.84)
    ]
    
    # Create a smooth transition curve from the matrix's 90 percentile mark down to 0
    bottom_mark, bottom_perc = matrix[-1] # This is 90 percentile
    
    # Filter generic points that are strictly below the bottom mark
    valid_generic = [pt for pt in generic_pts if pt[0] < bottom_mark]
    
    # Combine the bottom of the matrix with the generic curve
    full_lower_curve = [(bottom_mark, bottom_perc)] + valid_generic
        
    for i in range(len(full_lower_curve) - 1):
        u_mark, u_perc = full_lower_curve[i]
        l_mark, l_perc = full_lower_curve[i+1]
        
        if l_mark <= score <= u_mark:
            ratio = (score - l_mark) / (max(0.1, u_mark - l_mark))
            return l_perc + ratio * (u_perc - l_perc)
            
    # If it's somehow below 0 (negative marks)
    if score <= 0:
        return max(0.0, 0.84 - abs(score) * 0.05)
        
    return 0.0

@app.route('/')
def index():
    return render_template('index.html', shifts=shifts)

@app.route('/test/<shift>')
def test(shift):
    if shift not in shifts:
        return "Shift not found", 404
        
    # Get pdf filenames
    pdfs = os.listdir(os.path.join('static', 'papers', shift))
    phys_pdf = next((p for p in pdfs if 'physics' in p.lower()), '')
    chem_pdf = next((p for p in pdfs if 'chemistry' in p.lower()), '')
    math_pdf = next((p for p in pdfs if 'mathematics' in p.lower()), '')
    return render_template('test.html', shift=shift, phys_pdf=phys_pdf, chem_pdf=chem_pdf, math_pdf=math_pdf, locations=locations_db.get(shift, {}))

def evaluate_mcq(u_ans, real_ans):
    if not u_ans:
        return False
    if real_ans == 'Dropped':
        return True
    valid = [opt.strip() for opt in str(real_ans).split(',') if opt.strip()]
    return u_ans in valid

def evaluate_numeric(u_ans, real_ans):
    if not u_ans:
        return False
    real_str = str(real_ans).strip()
    if real_str == 'Dropped':
        return True
    if 'any' in real_str.lower():
        try:
            return float(u_ans) >= 0
        except ValueError:
            return False
    if 'or' in real_str.lower():
        parts = re.findall(r'[-+]?\d*\.?\d+', real_str)
        try:
            u_float = float(u_ans)
            for p in parts:
                if abs(u_float - float(p)) < 1e-4:
                    return True
        except ValueError:
            if u_ans.strip() in [p.strip() for p in parts]:
                return True
        return False
    # Standard numerical comparison
    try:
        return abs(float(u_ans) - float(real_str)) < 1e-4
    except ValueError:
        return u_ans.strip() == real_str

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    shift = data.get('shift')
    user_answers = data.get('answers') # dict: { 'Physics': { 'mcq': { '1': '2', ... }, 'num': {'1': '15', ...} }, ... }
    
    if shift not in answers_db:
        return jsonify({'error': 'invalid shift'}), 400
        
    results = {}
    total_score = 0
    mistakes = []
    
    for subject in ['Physics', 'Chemistry', 'Mathematics']:
        score = 0
        correct = 0
        incorrect = 0
        unattempted = 0
        
        start_q = 1
        if subject == 'Physics': start_q = 26
        if subject == 'Chemistry': start_q = 51
        
        # Real answers for this subject
        real_ans_list = answers_db[shift].get(subject, [])
        mcq_ans = real_ans_list[:20]
        num_ans = real_ans_list[20:25]
        
        subj_data = user_answers.get(subject, {'mcq': {}, 'num': {}})
        
        # Evaluate MCQs (20 questions: +4 / -1)
        for i in range(20):
            q_num = str(i + 1)
            u_ans = subj_data['mcq'].get(q_num, '').strip()
            if not u_ans:
                unattempted += 1
            else:
                correct_target = mcq_ans[i] if i < len(mcq_ans) else 'N/A'
                if evaluate_mcq(u_ans, correct_target):
                    score += 4
                    correct += 1
                else:
                    score -= 1
                    incorrect += 1
                    mistakes.append({'subject': subject, 'q_num': f"Q{start_q + i}", 'user_ans': u_ans, 'correct_ans': correct_target})
                    
        # Evaluate Numericals (5 questions: +4 / 0)
        attempted_num_count = 0
        for i in range(5):
            q_num = str(i + 1)
            u_ans = subj_data['num'].get(q_num, '').strip()
            if u_ans:
                attempted_num_count += 1
                correct_target = num_ans[i] if i < len(num_ans) else 'N/A'
                if evaluate_numeric(u_ans, correct_target):
                    score += 4
                    correct += 1
                else:
                    incorrect += 1
                    mistakes.append({'subject': subject, 'q_num': f"Q{start_q + 20 + i}", 'user_ans': u_ans, 'correct_ans': correct_target})
            else:
                unattempted += 1
        
        results[subject] = {
            'score': score,
            'correct': correct,
            'incorrect': incorrect,
            'unattempted': unattempted
        }
        total_score += score
        
    percentile = get_percentile(total_score, shift)
    
    return jsonify({
        'results': results,
        'total_score': total_score,
        'percentile': percentile,
        'mistakes': mistakes
    })

@app.route('/answer_key/<shift>/<subject>')
def answer_key(shift, subject):
    import os
    import glob
    from flask import send_file
    
    base_dir = os.path.join(app.root_path, 'static', 'originals')
    shift_dir = os.path.join(base_dir, shift)
    
    if not os.path.exists(shift_dir):
        return "Shift not found", 404
        
    sub_lower = subject.lower()
    
    # Check for Answer Key
    if sub_lower in ['key', 'answer_key', 'answerkey']:
        key_pdf = os.path.join(shift_dir, 'Answer_Key.pdf')
        if os.path.exists(key_pdf):
            return send_file(key_pdf)
            
    # Check for Full Paper
    if sub_lower in ['full', 'full_paper', 'fullpaper']:
        full_pdf = os.path.join(shift_dir, 'Full_Paper.pdf')
        if os.path.exists(full_pdf):
            return send_file(full_pdf)
            
    for pdf_path in glob.glob(os.path.join(shift_dir, '*.pdf')):
        basename = os.path.basename(pdf_path)
        base_lower = basename.lower()
        if sub_lower in base_lower:
            return send_file(pdf_path)
            
    return "Subject PDF not found", 404

@app.route('/download_result', methods=['POST'])
def download_result():
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    import io
    
    data = request.json
    results = data.get('results', {})
    total_score = data.get('total_score', 0)
    percentile = data.get('percentile', 0)
    mistakes = data.get('mistakes', [])
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "JEE Mains 2026 - Mock Test Result")
    
    # Score summary
    c.setFont("Helvetica", 14)
    c.drawString(50, height - 90, f"Total Score: {total_score} / 300")
    c.drawString(50, height - 110, f"Expected Percentile: {percentile:.2f} %ile")
    
    # Table header
    y = height - 150
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Subject")
    c.drawString(200, y, "Score")
    c.drawString(300, y, "Correct")
    c.drawString(400, y, "Incorrect")
    
    y -= 20
    c.line(50, y + 15, 500, y + 15)
    
    # Subject rows
    c.setFont("Helvetica", 12)
    for subj in ['Physics', 'Chemistry', 'Mathematics']:
        if subj in results:
            res = results[subj]
            c.drawString(50, y, subj)
            c.drawString(200, y, str(res['score']))
            c.drawString(300, y, str(res['correct']))
            c.drawString(400, y, str(res['incorrect']))
            y -= 20
            
    # Mistakes
    if mistakes:
        y -= 20
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "Mistakes Summary")
        y -= 20
        
        c.setFont("Helvetica", 11)
        for m in mistakes:
            if y < 50:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 11)
                
            text = f"{m['subject']} {m['q_num']}: You answered {m['user_ans']} (Correct: {m['correct_ans']})"
            c.drawString(50, y, text)
            y -= 15
            
    c.save()
    buffer.seek(0)
    
    from flask import send_file
    return send_file(buffer, as_attachment=True, download_name='JEE_Mock_Result.pdf', mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
