from django.shortcuts import render,redirect ,get_object_or_404
from base.models import User
from django.contrib import messages
from django.contrib import auth

# Create your views here.
def dashboard(request):
    return render (request, 'admins/dashboard.html')

def signup(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name =request.POST.get('last_name')
        school_name =request.POST.get('school_name')
        username =request.POST.get('username')
        password = request.POST.get('password')
        password1 =request.POST.get('password1')
        
        if password == password1:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'recovery code alrealdy exist')
                return redirect('admins:signup')
            else:
               User.objects.create_user(first_name=first_name,last_name=last_name ,username=username,school_name=school_name,password=password)
               return redirect('admins:login')
            

        else:
            messages.error(request, 'password do not match')
            return redirect('admins:signup')
               

    return render (request, 'admins/create-account.html')

def login(request):
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = auth.authenticate( username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('admins:dashboard')
        else:         
            messages.error(request, 'Invalid username or password.')
    return render(request, 'admins/login.html')



def forget(request):
    if request.method == "POST":
        recovery_code = request.POST.get('recovery_code')
        