from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Module  # ✅ import Module

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'role', 'module', 'is_staff', 'is_active')  # ✅ added 'module'
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'module')}),  # ✅ added 'module'
    )

# ✅ Register Module for superuser access
admin.site.register(Module)
