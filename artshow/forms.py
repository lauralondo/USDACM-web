import re
from django import forms

from django.forms import ModelForm
from models import Submission

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        
