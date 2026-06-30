from django.contrib import admin
from .models import Category, Application
from .forms import AdminActionForm

admin.site.register(Category)
class ApplicationAdmin(admin.ModelAdmin):
    form = AdminActionForm
    list_display = ('title', 'status', 'comment', 'created_at')
    list_filter = ('status', 'category')
admin.site.register(Application, ApplicationAdmin)