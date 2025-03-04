from django.db import models
from django.utils import timezone

class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    stand_no = models.CharField(max_length=50, blank=True)
    CATEGORY_CHOICES = [
        ('Construction', 'Construction'),
        ('Event Management', 'Event Management'),
        ('Healthcare', 'Healthcare'),
        ('Education', 'Education'),
        ('Hospitality', 'Hospitality'),
        ('Retail', 'Retail'),
        ('Other', 'Other'),
    ]
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    activity = models.TextField()
    
    def __str__(self):
        return self.name

class Assessment(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='assessments')
    assessor_name = models.CharField(max_length=255)
    date_created = models.DateField(default=timezone.now)
    hs_name = models.CharField(max_length=255, blank=True)
    hs_position = models.CharField(max_length=255, blank=True)
    hs_contact = models.CharField(max_length=255, blank=True)
    print_name = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return f"Assessment for {self.company.name} by {self.assessor_name}"

class Hazard(models.Model):
    SEVERITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]
    
    PROBABILITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]
    
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='hazards')
    hazard = models.CharField(max_length=255)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='Low')
    probability = models.CharField(max_length=10, choices=PROBABILITY_CHOICES, default='Low')
    persons = models.CharField(max_length=255)
    controls = models.TextField()
    
    def __str__(self):
        return self.hazard

class GeneratedPDF(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='pdfs')
    file = models.FileField(upload_to='risk_assessments/')
    date_generated = models.DateTimeField(auto_now_add=True)
    cloud_url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return f"PDF for {self.assessment.company.name} - {self.date_generated.strftime('%Y-%m-%d')}"