from django import forms
from django.contrib.auth.models import User
import re

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