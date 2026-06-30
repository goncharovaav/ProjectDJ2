from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import  login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistrationForm
from .models import Application, Category
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

    user = request.user
    if user.is_staff:
        if 'add_category' in request.POST:
            cat_name = request.POST.get('category_name', '').strip()
            if cat_name:
                Category.objects.create(name=cat_name)
                messages.success(request, f"Категория '{cat_name}' успешно добавлена.")
            return redirect('profile')

        if 'delete_category' in request.POST:
            cat_id = request.POST.get('category_id')
            category = get_object_or_404(Category, id=cat_id)
            category.delete()  # Удалит категорию и каскадно все заявки в ней
            messages.success(request, "Категория и все её заявки удалены.")
            return redirect('profile')

        if 'change_status' in request.POST:
            app_id = request.POST.get('app_id')
            application = get_object_or_404(Application, id=app_id)
            new_status = request.POST.get('new_status')
            if application.status == 'completed':
                messages.error(request, "Невозможно изменить статус уже выполненной заявки.")
                return redirect('profile')

            if new_status == 'in_progress':
                if application.status != 'new':
                    messages.error(request, "В работу можно взять только новую заявку.")
                    return redirect('profile')

                comment = request.POST.get('comment', '').strip()
                if not comment:
                    messages.error(request, "Для статуса 'Принято в работу' обязателен комментарий!")
                else:
                    application.status = 'in_progress'
                    application.comment = comment
                    application.save()
                    messages.success(request, "Заявка принята в работу.")

            elif new_status == 'completed':
                if 'design_image' not in request.FILES:
                    messages.error(request, "Для статуса 'Выполнено' обязательно прикрепите изображение дизайна!")
                else:
                    application.status = 'completed'
                    application.design_image = request.FILES['design_image']
                    application.save()
                    messages.success(request, "Заявка успешно выполнена и добавлена в галерею.")

            return redirect('profile')

        # Данные для вывода админу
        all_applications = Application.objects.all().order_by('-created_at')
        all_categories = Category.objects.all()

        context = {
            'applications': all_applications,
            'categories': all_categories,
        }
        return render(request, 'app/profile.html', context)
    else:
        if request.method == 'POST':
            form = ApplicationForm(request.POST, request.FILES)
            if form.is_valid():
                app = form.save(commit=False)
                app.user = user
                app.save()
                messages.success(request, "Заявка успешно создана!")
                return redirect('profile')
        else:
            form = ApplicationForm()

        user_applications = Application.objects.filter(user=user).order_by('-created_at')

        context = {
            'form': form,
            'applications': user_applications,
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