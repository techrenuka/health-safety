from django.urls import path
from . import views

app_name = 'risk_assessment'

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_assessment, name='create_assessment'),
    path('review/<int:assessment_id>/', views.review_assessment, name='review_assessment'),
    path('generate-pdf/<int:assessment_id>/', views.generate_pdf, name='generate_pdf'),
    path('download-pdf/<int:pdf_id>/', views.download_pdf, name='download_pdf'),
]