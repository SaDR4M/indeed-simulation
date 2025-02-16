from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
# Register your models here.

class CustomUserAdmin(UserAdmin) :
    fieldsets = None
    fields = ('phone', 'email', 'password' , 'first_name', 'last_name', 'is_active', 'is_staff' , 'is_superuser' , 'date_joined', 'last_login')
    add_fieldsets = (
    (None, {
    'fields': ('phone', 'email', 'first_name', 'last_name', 'password1', 'password2', 'is_active', 'is_staff')}
    ),
    )
    list_display =  ('phone', 'email', 'first_name', 'last_name' , 'is_staff',)
    ordering = ('phone',)

admin.site.register(User , CustomUserAdmin)