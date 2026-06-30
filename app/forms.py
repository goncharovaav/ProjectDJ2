from django import forms
from django.contrib.auth.models import User
import re

from app.models import Application


class RegistrationForm(forms.ModelForm):
    fio = forms.CharField(max_length=150, label='Fio', widget=forms.TextInput(attrs={'class':'form-control'}))
    password =  forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={'class':'form-control'}))
    password_confirm = forms.CharField(label="Повтор пароля", widget=forms.PasswordInput(attrs={'class':'form-control'}))
    polic_agree = forms.BooleanField(label="Согласие на обработку персональных данных", required=True)
    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {
            'username': 'Логин',
            'email': 'Email',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class':'form-control'}),
            'email': forms.EmailInput(attrs={'class':'form-control'}),
        }
    def clean_fio(self):
        fio = self.cleaned_data['fio']
        if not re.match(r'^[а-яА-ЯёЁ\s\-]+$', fio):
            raise forms.ValidationError("ФИО может содержать только кириллические буквы, дефис и пробелы.")
        return fio

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.match(r'^[a-zA-Z\-]+$', username):
            raise forms.ValidationError("Логин может содержать только латинские буквы и дефис.")

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Пользователь с таким логином уже существует.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError({"password_confirm": "Введенные пароли не совпадают"})
        return cleaned_data

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['title', 'description', 'category', 'image']
        labels = {
            'title': 'Название заявки',
            'description': 'Описание(что необходимо сделать)',
            'category': 'Выбор категории',
            'image': 'План помещения или фото',
        }
        widgets = {
            'title': forms.TextInput(),
            'description': forms.Textarea(attrs={'row': 4}),
            'category': forms.Select(),
            'image': forms.FileInput(),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 2 * 1024 * 1024:
                raise forms.ValidationError("Максимальный размер файла не должен превышать 2 мб")
        return image


class AdminActionForm(forms.ModelForm):
    """Специальная форма для валидации действий администратора в панели управления"""

    class Meta:
        # Указываем, что форма управляет записями из модели Application (Заявка)
        model = Application
        # Администратор может изменять только три этих поля
        fields = ['status', 'comment', 'design_image']

    def clean(self):
        """Метод сквозной валидации полей формы перед сохранением в БД"""
        # Сначала получаем все очищенные данные формы, которые ввел админ
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        comment = cleaned_data.get('comment')
        design_image = cleaned_data.get('design_image')

        if self.instance and self.instance.pk:
            current_status = Application.objects.get(pk=self.instance.pk).status

            if current_status in ['in_progress', 'completed'] and status != current_status:
                raise forms.ValidationError(
                    "Критическая ошибка: нельзя изменить статус у заявки, которая уже была обработана!")

        if status == 'in_progress' and not comment:
            raise forms.ValidationError({"comment": "При принятии заявки в работу вы обязаны указать комментарий."})

        if status == 'completed' and not design_image:
            raise forms.ValidationError(
                {"design_image": "При завершении заявки вы обязаны загрузить изображение готового дизайна."})
        return cleaned_data