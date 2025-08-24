from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm
import uuid

User = get_user_model()

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # User needs to verify email first
            user.save()
            
            # Send verification email
            verification_url = request.build_absolute_uri(
                reverse('accounts:verify_email', kwargs={'token': user.email_verification_token})
            )
            
            send_mail(
                'Verify your email address',
                f'Please click the following link to verify your email: {verification_url}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
            messages.success(request, 'Registration successful! Please check your email to verify your account.')
            return redirect('accounts:login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_email_verified:
                messages.error(request, 'Please verify your email address before logging in.')
                return redirect('accounts:login')
            login(request, user)
            next_url = request.GET.get('next', 'blog:home')
            return redirect(next_url)
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('blog:home')

def verify_email(request, token):
    try:
        user = User.objects.get(email_verification_token=token)
        if not user.is_email_verified:
            user.is_email_verified = True
            user.is_active = True
            user.save()
            messages.success(request, 'Email verified successfully! You can now log in.')
        else:
            messages.info(request, 'Email already verified.')
    except User.DoesNotExist:
        messages.error(request, 'Invalid verification token.')
    
    return redirect('accounts:login')

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})

@login_required
def change_role_view(request):
    if request.method == 'POST':
        new_role = request.POST.get('role')
        if new_role in dict(User.USER_ROLES):
            request.user.role = new_role
            request.user.save()
            messages.success(request, f'Role changed to {new_role} successfully!')
        else:
            messages.error(request, 'Invalid role selected.')
    
    return redirect('accounts:profile')
