from django.contrib import admin
from .models import Puzzle, PuzzleQuestion, PuzzleSolved, PuzzleReport, PuzzleQuestionHint


@admin.register(Puzzle)
class PuzzleAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_by', 'one_time_view', 'is_solved', 'self_destruct_at', 'created_at', 'updated_at')
    list_display_links = ('id', 'created_by')
    list_filter = ('one_time_view', 'is_solved', 'created_by', 'created_at', 'self_destruct_at')
    search_fields = ('id', 'created_by__username', 'encrypted_message')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(PuzzleQuestion)
class PuzzleQuestionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'puzzle', 'question', 'created_at')
    list_display_links = ('id', 'puzzle', 'question')
    list_filter = ('puzzle', 'created_at')
    search_fields = ('id', 'puzzle__id', 'question', 'answer')
    readonly_fields = ('created_at',)

@admin.register(PuzzleSolved)
class PuzzleSolvedAdmin(admin.ModelAdmin):
    list_display = ('id', 'puzzle', 'solved_by', 'solved_at')
    list_display_links = ('id', 'puzzle', 'solved_by')
    list_filter = ('puzzle', 'solved_by', 'solved_at')
    search_fields = ('id', 'puzzle__id', 'solved_by__username')
    readonly_fields = ('solved_at',)

@admin.register(PuzzleReport)
class PuzzleReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'puzzle', 'reported_by', 'created_at')
    list_display_links = ('id', 'puzzle', 'reported_by')
    list_filter = ('puzzle', 'reported_by', 'created_at')
    search_fields = ('id', 'puzzle__id', 'reported_by__username')
    readonly_fields = ('created_at',)

@admin.register(PuzzleQuestionHint)
class PuzzleQuestionHintAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'hint', 'created_at')
    list_display_links = ('id', 'question')
    list_filter = ('question', 'created_at')
    search_fields = ('id', 'question__id', 'question__question', 'hint')
    readonly_fields = ('created_at',)