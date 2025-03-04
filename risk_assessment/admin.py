from django.contrib import admin
from .models import Company, Assessment, Hazard, GeneratedPDF

class HazardInline(admin.TabularInline):
    model = Hazard
    extra = 1

class AssessmentAdmin(admin.ModelAdmin):
    inlines = [HazardInline]
    list_display = ('company', 'assessor_name', 'date_created')
    search_fields = ('company__name', 'assessor_name')
    list_filter = ('date_created',)

class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name', 'category')
    list_filter = ('category',)

class GeneratedPDFAdmin(admin.ModelAdmin):
    list_display = ('assessment', 'date_generated')
    search_fields = ('assessment__company__name',)
    list_filter = ('date_generated',)

admin.site.register(Company, CompanyAdmin)
admin.site.register(Assessment, AssessmentAdmin)
admin.site.register(Hazard)
admin.site.register(GeneratedPDF, GeneratedPDFAdmin)