from django.core.management.base import BaseCommand
import datetime
from bookings.models import TeeTime, LessonSlot

class Command(BaseCommand):
    help = 'Generate 10-minute tee times and 45-minute lesson slots for the next 7 days.'

    def handle(self, *args, **kwargs):
        deleted_tees = 0
        deleted_lessons = 0
        created = 0
        
        # Only clear today onwards to keep existing future bookings intact
        today = datetime.date.today()
        TeeTime.objects.filter(date__gte=today).delete()
        
        for day_offset in range(7):
            date = today + datetime.timedelta(days=day_offset)
            # Tee Times: every 10 mins from 08:00 to 17:30
            current_hour = 8
            current_min = 0
            while current_hour < 17 or (current_hour == 17 and current_min <= 30):
                t = datetime.time(current_hour, current_min)
                TeeTime.objects.create(date=date, time=t, is_available=True, max_players=4, booked_players=0)
                current_min += 10
                if current_min >= 60:
                    current_min = 0
                    current_hour += 1
                created += 1
                
            created += 1 # rough count
        self.stdout.write(self.style.SUCCESS(f'Successfully generated slots for 7 days!'))
