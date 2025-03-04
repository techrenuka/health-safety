import os
import json
from datetime import datetime
from io import BytesIO

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, FileResponse
from django.conf import settings
from django.forms import modelformset_factory

from .models import Company, Assessment, Hazard, GeneratedPDF
from .forms import CompanyForm, AssessmentForm, HazardForm, HazardFormSet, SafetyRepForm
from .utils.ai_helper import get_ai_recommendation
from .utils.spaces_config import get_spaces_client

import pdfkit
from jinja2 import Environment, FileSystemLoader

def home(request):
    return render(request, 'risk_assessment/home.html')

def create_assessment(request):
    if request.method == 'POST':
        
        company_form = CompanyForm(request.POST)
        assessment_form = AssessmentForm(request.POST)
        
        if company_form.is_valid() and assessment_form.is_valid():
            # Save company
            company = company_form.save()
            
            # Save assessment
            assessment = assessment_form.save(commit=False)
            assessment.company = company
            assessment.save()
            
            # Get AI recommendations
            data = {
                'name': assessment.assessor_name,
                'company': company.name,
                'category': company.category,
                'activity': company.activity,
                'potential_hazards': assessment_form.cleaned_data.get('potential_hazards', '')
            }
            
            try:
                ai_response = get_ai_recommendation(data)
                
                # Create hazards from AI recommendations
                if 'assessments' in ai_response:
                    for hazard_data in ai_response['assessments']:
                        Hazard.objects.create(
                            assessment=assessment,
                            hazard=hazard_data.get('Hazard', ''),
                            severity=hazard_data.get('Severity', 'Low'),
                            probability=hazard_data.get('Probability', 'Low'),
                            persons=hazard_data.get('Persons at Risk', ''),
                            controls=hazard_data.get('Controls to Minimise Risk', '')
                        )
                
                messages.success(request, 'Risk assessment created successfully!')
                return redirect('risk_assessment:review_assessment', assessment_id=assessment.id)
            
            except Exception as e:
                messages.error(request, f'Error generating AI recommendations: {str(e)}')
                return redirect('risk_assessment:home')
    else:
        company_form = CompanyForm()
        assessment_form = AssessmentForm()
    
    return render(request, 'risk_assessment/create_assessment.html', {
        'company_form': company_form,
        'assessment_form': assessment_form,
    })

def review_assessment(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id)
    company = assessment.company
    
    # Create formset for hazards
    HazardFormSet = modelformset_factory(
        Hazard, 
        form=HazardForm,
        extra=1,
        can_delete=True
    )
    
    if request.method == 'POST':
        company_form = CompanyForm(request.POST, instance=company)
        assessment_form = AssessmentForm(request.POST, instance=assessment)
        hazard_formset = HazardFormSet(
            request.POST, 
            queryset=Hazard.objects.filter(assessment=assessment)
        )
        
        if company_form.is_valid() and assessment_form.is_valid() and hazard_formset.is_valid():
            company_form.save()
            assessment_form.save()
            
            # Save hazards
            instances = hazard_formset.save(commit=False)
            for instance in instances:
                instance.assessment = assessment
                instance.save()
            
            # Handle deleted forms
            for obj in hazard_formset.deleted_objects:
                obj.delete()
            
            messages.success(request, 'Assessment updated successfully!')
            return redirect('risk_assessment:generate_pdf', assessment_id=assessment.id)
    else:
        company_form = CompanyForm(instance=company)
        assessment_form = AssessmentForm(instance=assessment)
        hazard_formset = HazardFormSet(queryset=Hazard.objects.filter(assessment=assessment))
    
    return render(request, 'risk_assessment/review_assessment.html', {
        'company_form': company_form,
        'assessment_form': assessment_form,
        'hazard_formset': hazard_formset,
        'assessment': assessment,
    })

def generate_pdf(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id)
    
    if request.method == 'POST':
        safety_rep_form = SafetyRepForm(request.POST, instance=assessment)
        
        if safety_rep_form.is_valid():
            safety_rep_form.save()
            
            try:
                # Get wkhtmltopdf path
                def get_wkhtmltopdf_path():
                    if os.name == 'nt':  # Windows
                        paths = [
                            'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe',
                            '.\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'
                        ]
                        for path in paths:
                            if os.path.exists(path):
                                return path
                    elif os.name == 'posix':  # Linux/Mac
                        return '/usr/bin/wkhtmltopdf'
                    else:
                        return 'wkhtmltopdf'  # Linux/Mac default
                
                # Configure PDFKit
                config = pdfkit.configuration(wkhtmltopdf=get_wkhtmltopdf_path())
                
                # Set up Jinja environment
                env = Environment(loader=FileSystemLoader(os.path.join(settings.BASE_DIR, 'templates')))
                template = env.get_template("risk_assessment/health.html")
                
                # Prepare data for PDF generation
                hazards = []
                for hazard in assessment.hazards.all():
                    hazards.append({
                        'hazard': hazard.hazard,
                        'severity': hazard.severity,
                        'probability': hazard.probability,
                        'persons': hazard.persons,
                        'controls': hazard.controls
                    })
                
                pdf_data = {
                    'company_name': assessment.company.name,
                    'assessors_name': assessment.assessor_name,
                    'address': assessment.company.address,
                    'date': assessment.date_created.strftime('%Y-%m-%d'),
                    'stand_no': assessment.company.stand_no,
                    'category': assessment.company.category,
                    'activity': assessment.company.activity,
                    'hazards': hazards,
                    'hs_name': assessment.hs_name,
                    'hs_position': assessment.hs_position,
                    'hs_contact': assessment.hs_contact,
                    'print_name': assessment.print_name
                }
                
                # Generate HTML from template
                rendered_html = template.render(**pdf_data)
                
                # PDF generation options
                options = {
                    'encoding': 'UTF-8',
                    'no-outline': None,
                    'quiet': '',
                    'enable-local-file-access': None,
                    'disable-smart-shrinking': None,
                    'print-media-type': None,
                    'page-size': 'A4'
                }
                
                # Generate PDF
                pdf = pdfkit.from_string(
                    rendered_html, 
                    False,  # Don't save to file
                    configuration=config, 
                    options=options
                )
                
                # Create sanitized filename
                safe_company_name = "".join(x for x in assessment.company.name 
                                          if x.isalnum() or x in (' ', '-', '_'))
                filename = f"risk_assessment_{safe_company_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
                
                # Save PDF to model
                pdf_buffer = BytesIO(pdf)
                pdf_file = GeneratedPDF(assessment=assessment)
                pdf_file.file.save(filename, pdf_buffer)
                
                # Try to upload to Digital Ocean Spaces
                try:
                    spaces_client = get_spaces_client()
                    pdf_buffer.seek(0)  # Reset buffer position
                    
                    spaces_client.upload_fileobj(
                        pdf_buffer,
                        "slateai",
                        f"risk-assessments/{filename}",
                        ExtraArgs={'ACL': 'public-read', 'ContentType': 'application/pdf'}
                    )
                    
                    # Generate temporary URL for download (valid for 1 hour)
                    pdf_url = spaces_client.generate_presigned_url(
                        'get_object',
                        Params={
                            'Bucket': "slateai",
                            'Key': f"risk-assessments/{filename}"
                        },
                        ExpiresIn=3600  # URL valid for 1 hour
                    )
                    
                    pdf_file.cloud_url = pdf_url
                    pdf_file.save()
                    
                except Exception as upload_error:
                    # Just log the error, we'll still have the local PDF
                    print(f"Error uploading to Digital Ocean Spaces: {str(upload_error)}")
                
                messages.success(request, 'PDF generated successfully!')
                return redirect('risk_assessment:download_pdf', pdf_id=pdf_file.id)
            
            except Exception as e:
                messages.error(request, f'Error generating PDF: {str(e)}')
                return redirect('risk_assessment:generate_pdf', assessment_id=assessment.id)
    else:
        safety_rep_form = SafetyRepForm(instance=assessment)
    
    return render(request, 'risk_assessment/generate_pdf.html', {
        'assessment': assessment,
        'safety_rep_form': safety_rep_form,
    })

def download_pdf(request, pdf_id):
    pdf_file = get_object_or_404(GeneratedPDF, id=pdf_id)
    
    # Display download page
    return render(request, 'risk_assessment/download_pdf.html', {
        'pdf_file': pdf_file,
    })