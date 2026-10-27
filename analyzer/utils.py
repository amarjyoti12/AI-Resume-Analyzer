
from pypdf import PdfReader
from docx import Document

import ollama



def extract_resume_text(file_path):
    if file_path.lower().endswith('.pdf'):
        reader = PdfReader(file_path)
        text = ""

        for page in reader.pages:
            text += page.extract_text() or ""

        return text

    elif file_path.lower().endswith('.docx'):
        document = Document(file_path)
        text = ""

        for paragraph in document.paragraphs:
            text += paragraph.text + "\n"

        return text

    else:
        return "Unsupported file format"





def analyze_resume(resume_text):
    response = ollama.chat(
        model='llama3.2:1b',
        messages=[
            {
                'role': 'user',
                'content': f"""
                Analyze the following resume.

                Identify:
1. Resume Score out of 100
2. Important technical skills
3. Candidate strengths
4. Missing or recommended skills
5. Suggestions to improve the resume

For the resume score:
- Give a score between 0 and 100.
- Evaluate skills, experience, education, projects,
  and resume clarity based on the available information.
- Briefly explain why you assigned this score.
- Do not invent missing qualifications.

                Resume text:
                {resume_text}
                """
            }
        ]
    )

    return response['message']['content']




def match_resume_to_job(resume_text, job_description):
    response = ollama.chat(
        model='llama3.2:1b',
        messages=[
            {
                'role': 'user',
                'content': f"""
Compare the resume with the job description.

Provide:
1. Matching skills
2. Missing or weak skills
3. Job match percentage out of 100
4. Suggestions to improve the match

Do not invent skills or qualifications.
Calculate the percentage based on the job requirements
that are supported by the resume.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}
"""
            }
        ]
    )

    return response['message']['content']
