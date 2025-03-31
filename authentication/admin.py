from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserChangeForm
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    list_display = ('email', 'first_name', 'last_name', 'wallet_balance', 'is_staff', 'is_superuser', 'change_password_link')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    readonly_fields = ('access_token', 'refresh_token')
    search_fields = ('email',)
    ordering = ('-id',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'wallet_balance',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Tokens (Read-only)'), {'fields': ('access_token', 'refresh_token')}),
    )

    def change_password_link(self, obj):
        if obj.pk:
            url = reverse('admin:auth_user_password_change', args=[obj.pk])
            return format_html('<a href="{}">Change Password</a>', url)
        return 'Save the user to change password.'
    
    def has_add_permission(self, request):
        return False



admin.site.register(User, UserAdmin)