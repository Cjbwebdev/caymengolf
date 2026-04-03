from django.utils import timezone
from datetime import timedelta

def run():
    from bookings.models import TeeTime
    import datetime
    
    today = datetime.date.today()
    TeeTime.objects.all().delete()
    
    for day_offset in range(7):
        date = today + timedelta(days=day_offset)
        for hour in range(8, 18):
            for minute in [0, 10, 20, 30, 40, 50]:
                t = datetime.time(hour, minute)
                TeeTime.objects.create(date=date, time=t)
    print(f"Created tee times for the next 7 days!")
