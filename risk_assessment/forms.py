from django import forms
from .models import Company, Assessment, Hazard

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'address', 'stand_no', 'category', 'activity']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'activity': forms.Textarea(attrs={'rows': 4}),
        }

class AssessmentForm(forms.ModelForm):
    potential_hazards = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
        help_text="Describe any potential hazards you're aware of (optional)"
    )
    
    class Meta:
        model = Assessment
        fields = ['assessor_name']
        
class HazardForm(forms.ModelForm):
    class Meta:
        model = Hazard
        fields = ['hazard', 'severity', 'probability', 'persons', 'controls']
        widgets = {
            'controls': forms.Textarea(attrs={'rows': 3}),
        }

class HazardFormSet(forms.BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = Hazard.objects.none()

HazardFormSet = forms.modelformset_factory(
    Hazard,
    form=HazardForm,
    formset=HazardFormSet,
    extra=1,
    can_delete=True
)

class SafetyRepForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ['hs_name', 'hs_position', 'hs_contact', 'print_name']