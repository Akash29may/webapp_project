import os
import json
import PyPDF2 
import google.generativeai as genai
from django.conf import settings
from teachers.models import Resource

def extract_text_from_pdf(file_path):
    """Utility to securely parse text from uploaded PDFs"""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
    return text

def generate_exam_script(exam):
    """
    AI Service Logic:
    1. Extracts text from all lecture notes attached to the Exam.
    2. Calculates Mark Distribution (MCQ: 5 marks, Descriptive: 10/15/20 marks).
       - If both: 60% MCQ, 40% Descriptive.
    3. Prompts LLM to strictly return JSON.
    4. Creates `Resource` of type `question_script` and links it securely.
    """
    
    # 1. Fetch & Accumulate Context Data
    notes = exam.additional_resources.filter(type='lecture')
    context_text = ""
    
    for note in notes:
        if note.media:
            file_path = note.media.path
            if os.path.exists(file_path) and file_path.endswith('.pdf'):
                context_text += f"\n--- SOURCE NOTE: {note.title} ---\n"
                context_text += extract_text_from_pdf(file_path)
                
    if not context_text.strip():
        context_text = f"No specific attached resources. Base questions on the general academic subject of: {exam.title}"
        
    # 2. Logic Matrix for Marks Distribution
    exam_type = exam.exam_type 
    total_marks = exam.marks
    
    mcq_marks = 0
    desc_marks = 0
    
    if exam_type == 'mcq':
        mcq_marks = total_marks
    elif exam_type == 'descriptive':
        desc_marks = total_marks
    else: # mixed / both
        mcq_marks = int(total_marks * 0.6)
        desc_marks = total_marks - mcq_marks
        
    # Breakdown quantities (Rule: MCQ=5, Desc=10 default)
    mcq_count = mcq_marks // 5
    
    # We will let the AI chunk descriptive marks into 10s or 15s to match desc_marks
    desc_count = desc_marks // 10 if desc_marks % 10 == 0 else max(1, desc_marks // 15)
    
    # 3. AI SDK Configuration
    API_KEY = getattr(settings, 'GEMINI_API_KEY', os.getenv('GEMINI_API_KEY'))
    if API_KEY:
        genai.configure(api_key=API_KEY)
        
    # Build System Prompt mapping directly to our students' frontend schema
    prompt = f"""
    You are an expert AI Assessment Generator for an automated examination platform.
    Generate a JSON set of exam questions strictly based on the provided context material.
    
    TARGET SPECS:
    Total Marks: {total_marks}
    Exam Modality: {exam_type}
    
    GENERATION RULES:
    1. If MCQ is required: Generate exactly {mcq_count} MCQ questions. Each must be exactly 5 marks.
    2. If Descriptive is required: Generate Descriptive questions summarizing to exactly {desc_marks} marks (distribute as 10, 15, or 20 marks per question).
    3. Output raw JSON format ONLY. Do NOT wrap it in ```json blocks.
    
    REQUIRED JSON SCHEMA SCHEMA:
    [
        {{
            "id": 1,
            "question_text": "string",
            "type": "mcq",
            "marks": 5,
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "note": "Optional hint if a complex concept, otherwise null",
            "answer": "1" // Index number of the correct option as a string
        }},
        {{
            "id": 2,
            "question_text": "string",
            "type": "descriptive",
            "marks": 10,
            "options": [],
            "note": null,
            "answer": "Descriptive broad answer key for evaluation reference."
        }}
    ]
    
    SOURCE MATERIAL:
    {context_text[:20000]} 
    """
    
    try:
        # Utilizing gemini-1.5-flash which has a massive context window and a great free tier
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        # Clean Output
        raw_json = response.text.replace('```json', '').replace('```', '').strip()
        qs_data = json.loads(raw_json)
        
        # Ensure it's a list (to map existing UI arrays)
        if isinstance(qs_data, dict) and "question" in qs_data:
            script_payload = qs_data["question"]
        elif isinstance(qs_data, dict) and "questions" in qs_data:
            script_payload = qs_data["questions"]
        else:
            script_payload = qs_data
            
        # 4. Save into Database Model securely
        qs_resource = Resource.objects.create(
            title=f"AI Question Script: {exam.title}",
            exam=exam,
            type='question_script',
            script=script_payload
        )
        
        # Formally bind it to the origin Exam
        exam.question_script = qs_resource
        exam.ai_generation_done = True
        exam.save()
        
        return True, qs_resource
        
    except Exception as e:
        print(f"CRITICAL: AI Generation Engine Failed: {str(e)}")
        return False, str(e)
