from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required

# Create your views here.
User = get_user_model()


def index(request):
    return render(request, "index.html")


def about(request):
    return render(request, "about.html")


def contact(request):
    return render(request, "contact.html")


def home(request):
    return render(request, "home.html")


def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=email, password=password)
        if user is not None:
            messages.success(request, "Login Successful")
            return redirect("home")
        # if user is not None:
        #     if user.check_password(password):
        #         messages.success(request, "Login Successful")
        #         return redirect("home")
        #     else:
        #         messages.error(request, "invalid password")
        #         return redirect("login")
        else:
            messages.error(request, "user does not exist")
            return redirect("login")
    return render(request, "login.html")


def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("confirm-password")

        if password != password2:
            messages.error(request, "passwords do not match")
            return redirect("signup")

        if User.objects.filter(email=email).exists():
            messages.error(request, "email already exists")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "username already exists")
            return redirect("signup")

        if len(password) < 8:
            messages.error(request, "password must be at least 8 characters")
            return redirect("signup")

        if len(username) < 4:
            messages.error(request, "username must be at least 4 characters")
            return redirect("signup")

        if len(username) > 20:
            messages.error(request, "username must be at most 20 characters")
            return redirect("signup")

        if len(password) > 20:
            messages.error(request, "password must be at most 20 characters")
            return redirect("signup")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        user.save()
        messages.success(request, "User created successfully")
        return redirect("login")
    return render(request, "signup.html")


def logout(request):
    return render(request, "logout.html")


@login_required(login_url="login")
def profile(request):
    return render(request, "profile.html")


def forgot_password(request):
    return render(request, "forgot_password.html")
