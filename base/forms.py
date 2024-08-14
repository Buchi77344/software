from django import forms

class BulkUploadForm(forms.Form):
    file = forms.FileField(label='Select a CSV file')





class UsernameForm(forms.Form):
    username = forms.CharField(max_length=150)


class LoginForm(forms.Form):
    user_id = forms.CharField(max_length=100, label="User ID")
