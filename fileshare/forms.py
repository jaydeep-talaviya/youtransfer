from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import DownloadFile,Profile,User

# Create your forms here.

class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True)
	username = forms.CharField(required=True)
	class Meta:
		model = User
		fields = ("username","email", "password1", "password2")


class FileForm(forms.Form):
	# uploads = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
	# auto_delete = forms.IntegerField()
	title=forms.CharField(max_length=50,required=False)
	message= forms.CharField(widget=forms.Textarea,required=False)
	# email_to = forms.EmailField()
	# user_email = forms.EmailField()

class LoginForm(forms.Form):
	username=forms.CharField(max_length=50)
	password = forms.CharField(max_length=32, widget=forms.PasswordInput)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('profile_pic','job_function')


class EmailResetConfirmForm(forms.Form):
	old_email=forms.EmailField()
	new_email=forms.EmailField()
