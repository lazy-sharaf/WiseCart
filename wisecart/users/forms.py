from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(max_length=255, required=True)
    email = forms.EmailField(required=True)
    gender_choices = [("M", "Male"), ("F", "Female"), ("N", "Not Prefer to Say")]
    gender = forms.ChoiceField(
        choices=gender_choices, required=True, widget=forms.RadioSelect, initial="N"
    )

    class Meta:
        model = CustomUser
        fields = ["username", "full_name", "email", "password1", "password2", "gender"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.full_name = self.cleaned_data["full_name"]
        user.email = self.cleaned_data["email"]
        user.gender = self.cleaned_data["gender"]
        user.user_type = "basic"  # Default user type is always 'basic'
        if commit:
            user.save()
        return user


class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'full_name', 'gender']
        widgets = {"gender": forms.RadioSelect}
