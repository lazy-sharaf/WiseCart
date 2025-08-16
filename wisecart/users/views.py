from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .forms import CustomUserCreationForm, UpdateProfileForm
from .models import CustomUser

def registration(request):
    if request.user.is_authenticated:
        return redirect('users:profile')
        
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)  # Add request.FILES
        if form.is_valid():
            user = form.save()
            # Log the user in after registration
            login(request, user)
            messages.success(request, "Account created successfully! Welcome to wisecart!")
            return redirect('users:profile')
    else:
        form = CustomUserCreationForm()
    return render(request, "users/registration.html", {"form": form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('users:profile')
        
    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username_or_email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.full_name}!")
            next_url = request.GET.get('next', 'users:profile')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username/email or password.")
    
    return render(request, "users/login.html")

@login_required
def profile_view(request):
    return render(request, "users/profile.html")

@login_required
def update_profile(request):
    if request.method == "POST":
        form = UpdateProfileForm(request.POST, request.FILES, instance=request.user)  # Add request.FILES
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect("users:profile")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UpdateProfileForm(instance=request.user)

    return render(request, "users/update_profile.html", {"form": form})

@login_required
def remove_profile_picture(request):
    """Remove user's profile picture"""
    if request.method == "POST":
        user = request.user
        if user.profile_picture:
            # Delete the file from storage
            try:
                user.profile_picture.delete(save=False)
                user.profile_picture = None
                user.save()
                messages.success(request, "Your profile picture has been removed successfully!")
            except Exception as e:
                messages.error(request, "Error removing profile picture. Please try again.")
        else:
            messages.info(request, "You don't have a profile picture to remove.")
    
    return redirect('users:profile')

@login_required
def settings_view(request):
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "change_email":
            new_email = request.POST.get("new_email")
            if new_email and new_email != request.user.email:
                request.user.email = new_email
                request.user.save()
                messages.success(request, "Your email has been updated successfully!")
            else:
                messages.error(request, "Please enter a different email address.")

        elif action == "change_password":
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Your password has been changed successfully!")
            else:
                messages.error(request, "Please correct the password errors.")

    password_form = PasswordChangeForm(request.user)
    return render(request, "users/settings.html", {"password_form": password_form})


def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            associated_users = CustomUser.objects.filter(email=email)
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Request"
                    email_template_name = "users/password_reset_email.html"
                    c = {
                        "email": user.email,
                        'domain': request.META['HTTP_HOST'],
                        'site_name': 'wisecart',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'https' if request.is_secure() else 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                    except Exception as e:
                        messages.error(request, f"Error sending email: {e}")
                        return redirect('users:password_reset')
                    messages.success(request, "Password reset email has been sent to your email address.")
                    return redirect('users:login')
            else:
                messages.error(request, "No user found with this email address.")
    else:
        form = PasswordResetForm()
    return render(request, "users/password_reset_form.html", {"form": form})


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been set successfully. You may go ahead and log in now.")
                return redirect('users:login')
        else:
            form = SetPasswordForm(user)
        return render(request, 'users/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, "The reset link is invalid, possibly because it has already been used or has expired.")
        return redirect('users:login')
