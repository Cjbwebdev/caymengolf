from django.contrib import admin
from .models import GolferProfile, Score, WeeklyLeaderboard


@admin.register(GolferProfile)
class GolferProfileAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'user', 'handicap_index')
    search_fields = ('display_name', 'user__username')


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('golfer', 'date', 'total_score', 'par', 'to_par_str', 'handicap_at_time')
    list_filter = ('date',)


@admin.register(WeeklyLeaderboard)
class WeeklyLeaderboardAdmin(admin.ModelAdmin):
    list_display = ('golfer', 'score', 'week_start')
