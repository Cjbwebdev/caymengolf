from django.contrib import admin
from .models import GolferProfile, Score, WeeklyLeaderboard


@admin.register(GolferProfile)
class GolferProfileAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'user', 'handicap_index', 'home_course', 'is_public')
    search_fields = ('display_name', 'user__username', 'user__email')
    list_filter = ('is_public', 'home_course')


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('golfer', 'date', 'total_score', 'par', 'to_par_display', 'handicap_at_time', 'is_verified')
    list_filter = ('is_verified', 'date', 'course')
    search_fields = ('golfer__display_name', 'golfer__user__username')
    date_hierarchy = 'date'


@admin.register(WeeklyLeaderboard)
class WeeklyLeaderboardAdmin(admin.ModelAdmin):
    list_display = ('golfer', 'score', 'week_start', 'week_end')
    list_filter = ('week_start',)
    search_fields = ('golfer__display_name',)
