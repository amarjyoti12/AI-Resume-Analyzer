
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ResumeForm
from .models import Resume
from django.shortcuts import render, redirect, get_object_or_404
from .models import Resume
from .utils import extract_resume_text, analyze_resume, match_resume_to_job
from django.http import HttpResponse
from .utils import extract_resume_text
from django.http import HttpResponse
from reportlab.pdfgen import canvas
import re


def home(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, 'Resume uploaded successfully!')
            return redirect('resume_list')
    else:
        form = ResumeForm()

    return render(request, 'home.html', {'form': form})



def resume_list(request):
    resumes = Resume.objects.all().order_by('-uploaded_at')
    return render(request, 'resume_list.html', {'resumes': resumes})





def test_resume_text(request, resume_id):
    resume = Resume.objects.get(id=resume_id)

    text = extract_resume_text(resume.resume_file.path)

    return HttpResponse(
        f"<h2>Extracted Resume Text</h2><pre>{text}</pre>"
    )






def analyze_resume_view(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id)

    resume_text = extract_resume_text(resume.resume_file.path)

    analysis = analyze_resume(resume_text)

    match = re.search(
        r'(?:resume\s*)?score\s*[:\-]?\s*(\d{1,3})\s*(?:/\s*100)?',
        analysis,
        re.IGNORECASE
    )

    score = None
    if match:
        score = min(int(match.group(1)), 100)

    job_match = None

    if request.method == 'POST':
        job_description = request.POST.get(
            'job_description', ''
        ).strip()

        if job_description:
            job_match = match_resume_to_job(
                resume_text,
                job_description
            )

    return render(request, 'analysis_result.html', {
        'resume': resume,
        'analysis': analysis,
        'score': score,
        'job_match': job_match,
    })




def download_analysis_pdf(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id)

    resume_text = extract_resume_text(resume.resume_file.path)
    analysis = analyze_resume(resume_text)

    match = re.search(
        r'(?:resume\s*)?score\s*[:\-]?\s*(\d{1,3})\s*(?:/\s*100)?',
        analysis,
        re.IGNORECASE
    )

    score = min(int(match.group(1)), 100) if match else "Not available"

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="resume_analysis_{resume.id}.pdf"'
    )

    pdf = canvas.Canvas(response)
    pdf.setTitle("Resume Analysis Report")

    width, height = 595, 842
    y = height - 50

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, y, "AI Resume Analysis Report")
    y -= 35

    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, y, f"Candidate: {resume.name}")
    y -= 20
    pdf.drawString(50, y, f"Email: {resume.email}")
    y -= 20
    pdf.drawString(50, y, f"Resume Score: {score}/100")
    y -= 35

    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(50, y, "AI Analysis")
    y -= 25

    pdf.setFont("Helvetica", 9)

    for line in analysis.splitlines():
        words = line.split()
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()

            if pdf.stringWidth(test_line, "Helvetica", 9) > 490:
                if y < 50:
                    pdf.showPage()
                    pdf.setFont("Helvetica", 9)
                    y = height - 50

                pdf.drawString(50, y, current_line)
                y -= 14
                current_line = word
            else:
                current_line = test_line

        if y < 50:
            pdf.showPage()
            pdf.setFont("Helvetica", 9)
            y = height - 50

        if current_line:
            pdf.drawString(50, y, current_line)
            y -= 14

    pdf.save()
    return response
