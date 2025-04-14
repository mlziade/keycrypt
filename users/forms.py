from django import forms

class CreateUserForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, required=True, label="Confirm Password")
    email = forms.EmailField(required=True)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username.isalnum():
            raise forms.ValidationError("Username must be alphanumeric.")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email or '@' not in email:
            raise forms.ValidationError("Invalid email address.")
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")
        
        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords don't match")
        return cleaned_data