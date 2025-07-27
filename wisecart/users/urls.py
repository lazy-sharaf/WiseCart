from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'users'

urlpatterns = [
    # Authentication URLs
    path("register/", views.registration, name="registration"),
    path("login/", views.login_view, name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    
    # Profile URLs
    path("profile/", views.profile_view, name="profile"),
    path("profile/update/", views.update_profile, name="update_profile"),
    path("profile/remove-picture/", views.remove_profile_picture, name="remove_profile_picture"),
    path("settings/", views.settings_view, name="settings"),
    
    # Password Reset URLs
    path("password-reset/", views.password_reset_request, name="password_reset"),
    path("password-reset-confirm/<uidb64>/<token>/", views.password_reset_confirm, name="password_reset_confirm"),
]
