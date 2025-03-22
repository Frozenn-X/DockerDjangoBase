from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserPermission, AuthToken


class UserPermissionInline(admin.TabularInline):
    model = UserPermission
    extra = 1


class UserAdmin(BaseUserAdmin):
    inlines = (UserPermissionInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')


class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token_preview', 'created_at', 'expires_at', 'is_active')
    list_filter = ('is_active', 'created_at', 'expires_at')
    search_fields = ('user__username', 'user__email', 'token')
    readonly_fields = ('token', 'created_at')
    
    def token_preview(self, obj):
        """Afficher une prévisualisation du token."""
        return f"{obj.token[:10]}...{obj.token[-10:]}"
    token_preview.short_description = 'Token'


admin.site.register(User, UserAdmin)
admin.site.register(UserPermission)
admin.site.register(AuthToken, AuthTokenAdmin)
