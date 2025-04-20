from django.contrib import admin

from .models import DailyChallenge

@admin.register(DailyChallenge)
class DailyChallengeAdmin(admin.ModelAdmin):
    list_display = ('id', 'daily_date', 'difficulty', 'theme', 'created_at')
    list_display_links = ('id', 'daily_date')
    list_filter = ('daily_date', 'difficulty', 'created_at')
    search_fields = ('id', 'theme', 'encrypted_message')
    fieldsets = (
        ('Basic Information', {
            'fields': ('daily_date', 'difficulty', 'theme')
        }),
        ('Puzzle Content', {
            'fields': ('encrypted_message', 'nonce', 'salt')
        }),
        ('Puzzle Settings', {
            'fields': ('one_time_view', 'is_solved', 'self_destruct_at')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'daily_date'