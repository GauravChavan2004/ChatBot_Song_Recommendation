from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

@login_required
def user_register(request):
    if request.method=='POST':
        first_name=request.POST['first_name']
        last_name=request.POST['last_name']
        email=request.POST['email']
        username=request.POST['username']
        password1=request.POST['password1']
        password2=request.POST['password2']     

        # Check if passwords match
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return redirect('user_register')
        
        # Check if username or email already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken')
            return redirect('user_register')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered')
            return redirect('user_register')

        data=User.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,password=password1)
        data.save()
        messages.success(request, 'Account created successfully. You can now log in.')
        return redirect('user_login')
    return render(request, 'register.html')

def user_login(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        user= auth.authenticate(username=username,password=password)

        if user is not None:
            auth.login(request,user)
            messages.success(request, "Login successful!")
            return redirect('/')
        else:
            messages.error(request, 'Invalid username and password !!')
            return redirect('user_login')
        
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('user_login')
