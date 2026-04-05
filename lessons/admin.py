from django.contrib import admin
from .models import LessonType


class LessonTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration_minutes', 'price', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('is_active',)


admin.site.register(LessonType, LessonTypeAdmin)
