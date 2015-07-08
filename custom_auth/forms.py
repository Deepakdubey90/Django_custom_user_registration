from django import forms
from custom_auth.models import MyUser
from django.forms import ModelForm


class UserCreationForm(forms.ModelForm):

    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = MyUser
        fields = ('email', 'date_of_birth', 'userprofilename', 'contact_no')

    def clean_username(self):
        email = self.cleaned_data["email"]
        try:
            MyUser.objects.get(email=email)
        except MyUser.DoesNotExist:
            return email
        raise forms.ValidationError(_("A user with that email already exists."))

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.email = self.cleaned_data['email']
        user.userprofilename = self.cleaned_data['userprofilename']
        user.contact_no = self.cleaned_data['contact_no']
        if commit:
            user.is_active = False
            user.save()
        return user

    def authenticate(self, username=None, password=None):
        try:
            user = MyUser.objects.get(email=username)
            if user.check_password(password):
                return user
        except MyUser.DoesNotExist:
            return None

