from django.shortcuts import render, redirect
from django.contrib.auth import  login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistrationForm
from .models import Application
from .forms import ApplicationForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.first_name = form.cleaned_data['fio']
            user.save()
            login(request, user)
            return redirect('profile')
    else:
        form = RegistrationForm()
    return render(request, 'app/register.html', {'form': form})

def main_view(request):
    completed_applications = Application.objects.filter(status='completed')[:4]

    in_progress_count = Application.objects.filter(status='in_progress').count()

    context = {
        'completed_applications': completed_applications,
        'in_progress_count': in_progress_count,
    }
    return render(request, 'app/main.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_staff:
                    return redirect('/superadmin/')
                return redirect('profile')
    else:
        form = AuthenticationForm()
    return render(request, 'app/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    status_filter = request.GET.get('status')
    user_applications = Application.objects.filter(user=request.user)
    if status_filter in ['new', 'in_progress', 'completed']:
        user_applications = user_applications.filter(status=status_filter)
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            return redirect('profile')
    else:
        form = ApplicationForm()
    context = {
        'applications': user_applications,
        'form': form,
        'status_filter': status_filter,
    }

    return render(request, 'app/profile.html', context)

def delete_application_view(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        application = Application.objects.get(pk=pk, user=request.user)

        if application.status == 'new':
            application.delete()

    except Application.DoesNotExist:
        pass
    return redirect('profile')