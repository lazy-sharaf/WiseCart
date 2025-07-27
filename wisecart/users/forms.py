from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(max_length=255, required=True)
    email = forms.EmailField(required=True)
    gender_choices = [("M", "Male"), ("F", "Female"), ("N", "Not Prefer to Say")]
    gender = forms.ChoiceField(
        choices=gender_choices, required=True, widget=forms.RadioSelect, initial="N"
    )
    profile_picture = forms.ImageField(
        required=False, 
        help_text="Upload your profile picture (JPG, PNG, max 5MB)",
        widget=forms.FileInput(attrs={
            'class': 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = CustomUser
        fields = ["username", "full_name", "email", "password1", "password2", "gender", "profile_picture"]

    def clean_profile_picture(self):
        """Validate profile picture file"""
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            # Check file size (5MB limit)
            if profile_picture.size > 5 * 1024 * 1024:
                raise ValidationError("Image file too large ( > 5MB )")
            
            # Check file type
            if not profile_picture.content_type.startswith('image/'):
                raise ValidationError("File is not an image")
                
        return profile_picture

    def save(self, commit=True):
        user = super().save(commit=False)
        user.full_name = self.cleaned_data["full_name"]
        user.email = self.cleaned_data["email"]
        user.gender = self.cleaned_data["gender"]
        user.user_type = "basic"  # Default user type is always 'basic'
        if self.cleaned_data.get("profile_picture"):
            user.profile_picture = self.cleaned_data["profile_picture"]
        if commit:
            user.save()
        return user


class UpdateProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(
        required=False,
        help_text="Upload your profile picture (JPG, PNG, max 5MB)",
        widget=forms.FileInput(attrs={
            'class': 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'full_name', 'gender', 'profile_picture']
        widgets = {
            "gender": forms.RadioSelect,
            "username": forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'}),
            "full_name": forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'}),
        }

    def clean_profile_picture(self):
        """Validate profile picture file"""
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            # Check file size (5MB limit)
            if profile_picture.size > 5 * 1024 * 1024:
                raise ValidationError("Image file too large ( > 5MB )")
            
            # Check file type
            if not profile_picture.content_type.startswith('image/'):
                raise ValidationError("File is not an image")
                
        return profile_picture
