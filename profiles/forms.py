from django import forms
from django.contrib.auth import get_user_model
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset
from .models import AuthorProfile

User = get_user_model()

class AuthorProfileForm(forms.ModelForm):
    class Meta:
        model = AuthorProfile
        fields = [
            'bio', 'profile_picture', 'website', 'twitter', 'linkedin', 
            'github', 'facebook', 'instagram', 'location', 'birth_date'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Basic Information',
                'bio',
                'profile_picture',
                Row(
                    Column('location', css_class='form-group col-md-6 mb-0'),
                    Column('birth_date', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
            ),
            Fieldset(
                'Social Media & Links',
                'website',
                Row(
                    Column('twitter', css_class='form-group col-md-6 mb-0'),
                    Column('instagram', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('linkedin', css_class='form-group col-md-6 mb-0'),
                    Column('github', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                'facebook',
            ),
            Submit('submit', 'Update Profile', css_class='btn btn-primary')
        )

