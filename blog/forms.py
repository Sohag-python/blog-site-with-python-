from django import forms
from django.contrib.auth import get_user_model
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from .models import Blog, Category, Rating

User = get_user_model()

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'body', 'excerpt', 'category', 'status', 'featured_image']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 10}),
            'excerpt': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'title',
            'excerpt',
            'body',
            Row(
                Column('category', css_class='form-group col-md-6 mb-0'),
                Column('status', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'featured_image',
            Submit('submit', 'Save Blog', css_class='btn btn-primary')
        )

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'description',
            Submit('submit', 'Save Category', css_class='btn btn-primary')
        )

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['score', 'review']
        widgets = {
            'score': forms.Select(choices=Rating.RATING_CHOICES),
            'review': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your review (optional)'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'score',
            'review',
            Submit('submit', 'Submit Rating', css_class='btn btn-primary')
        )

class SearchForm(forms.Form):
    query = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search blogs...',
            'class': 'form-control'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    author = forms.ModelChoiceField(
        queryset=User.objects.filter(role__in=['author', 'admin']),
        required=False,
        empty_label="All Authors",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            Row(
                Column('query', css_class='form-group col-md-4 mb-0'),
                Column('category', css_class='form-group col-md-2 mb-0'),
                Column('author', css_class='form-group col-md-2 mb-0'),
                Column('date_from', css_class='form-group col-md-2 mb-0'),
                Column('date_to', css_class='form-group col-md-2 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Search', css_class='btn btn-primary')
        )

