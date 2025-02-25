from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'fullname', 'email', 'is_staff', 'is_active')
    
    fieldsets = (
        (None, {'fields': ('fullname', 'username', 'password')}),
        ('Personal info', {'fields': ('email',)}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('id', 'username', 'fullname', 'email', 'password1', 'password2'),
        }),
    )
    
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'email')

admin.site.register(CustomUser, CustomUserAdmin)