from django import forms

class BulkUploadForm(forms.Form):
    subject = forms.CharField(max_length=1000,label='subject')
    file = forms.FileField(label='Select a CSV file')


class SearchForm(forms.Form):
    query = forms.CharField(max_length=500)


class UsernameForm(forms.Form):
    username = forms.CharField(max_length=150)


class LoginForm(forms.Form):
    user_id = forms.CharField(max_length=100, label="User ID")
