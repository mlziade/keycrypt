from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Profile, ResetPasswordLink
from django.utils.timezone import now

@admin.register(Profile)
class ProfileAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined', 'last_login', 'personal_url')
    list_display_links = ('id', 'username')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'date_joined', 'last_login')
    search_fields = ('id', 'username', 'email', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')

    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('personal_url',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('personal_url',)}),
    )

@admin.register(ResetPasswordLink)
class ResetPasswordLinkAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'expires_at', 'is_used', 'is_expired')
    list_display_links = ('id', 'user')
    search_fields = ('id', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'expires_at', 'is_used', 'is_expired')

    def is_expired(self, obj):
        return obj.is_used or obj.expires_at < now()
    is_expired.boolean = True
    is_expired.short_description = 'Expired'

    def has_add_permission(self, request):
        return False