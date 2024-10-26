from django.shortcuts import render, redirect
from .forms import LoginForm, OTPForm, ProfileForm
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
import random
from django.contrib.auth.models import User
from .models import UserOTP, Profile

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            user_otp, created = UserOTP.objects.get_or_create(user=user)
            user_otp.otp = otp
            user_otp.save()
            print(f"OTP for {user.username}: {otp}")
            request.session['pro_otp_user_id'] = user.id  # corrected session key name
            return redirect('otp_verify')
    
    form = LoginForm()
    return render(request, 'login.html', {'form': form})

def otp_verify_view(request):
    user_id = request.session.get('pro_otp_user_id')
    if not user_id:
        return redirect('login')
    
    user = User.objects.get(id=user_id)
    user_otp = UserOTP.objects.get(user=user)
    
    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            if otp == user_otp.otp:
                user_otp.otp = ''  # Clear OTP after successful login
                user_otp.save()
                login(request, user)
                del request.session['pro_otp_user_id']
                return redirect('home')
            else:
                return HttpResponse("Invalid OTP")
    else:
        form = OTPForm()
    
    return render(request, 'otp_verify.html', {'form': form})

@login_required
def home_view(request):
    return render(request, 'home.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
# in users/views.py
@login_required
def profile_update_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_update')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'profile_update.html', {'form': form})
