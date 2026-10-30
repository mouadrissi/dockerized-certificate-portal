from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur

class CustomUserAdmin(UserAdmin):
    model = Utilisateur
    # This tells Django to use the default user fields, but adds a section for your custom roles
    fieldsets = UserAdmin.fieldsets + (
        ('Rôle Utilisateur (PFA)', {'fields': ('role',)}),
    )
    # This ensures the role shows up in the main list view too
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_staff']

# Register the model with our new custom admin configuration
admin.site.register(Utilisateur, CustomUserAdmin)