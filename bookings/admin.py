from django.contrib import admin
from .models import TeeTime, LessonSlot, Booking


class TeeTimeAdmin(admin.ModelAdmin):
    list_display = ('date', 'time', 'max_players', 'booked_players', 'is_available')
    list_filter = ('date', 'is_available')
    list_editable = ('is_available',)
    ordering = ('date', 'time')


class LessonSlotAdmin(admin.ModelAdmin):
    list_display = ('date', 'time', 'duration', 'is_available')
    list_filter = ('date', 'is_available')
    list_editable = ('is_available',)
    ordering = ('date', 'time')


class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'booking_type', 'date', 'num_players', 'is_paid', 'is_cancelled', 'total_price')
    list_filter = ('is_paid', 'is_cancelled', 'date')
    search_fields = ('user__username', 'user__email', 'player_names')
    ordering = ('-created_at',)

    def booking_type(self, obj):
        if obj.tee_time:
            return f"Tee Time ({obj.tee_time.time})"
        if obj.lesson_slot:
            return f"Lesson ({obj.lesson_slot.time})"
        return "Unknown"

    def date(self, obj):
        t = obj.tee_time or obj.lesson_slot
        return t.date if t else 'N/A'


admin.site.register(TeeTime, TeeTimeAdmin)
admin.site.register(LessonSlot, LessonSlotAdmin)
admin.site.register(Booking, BookingAdmin)
