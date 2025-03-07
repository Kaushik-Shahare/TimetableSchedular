from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import time
from timetable.models import TimeSlot

class Command(BaseCommand):
    help = 'Initialize default time slots for timetable'

    def handle(self, *args, **kwargs):
        # Define days
        days = [
            ('MON', 'Monday'),
            ('TUE', 'Tuesday'),
            ('WED', 'Wednesday'),
            ('THU', 'Thursday'),
            ('FRI', 'Friday'),
            ('SAT', 'Saturday'),
        ]

        # Define lecture times (6 lectures per day)
        lecture_times = [
            (time(9, 0), time(9, 50)),   # 9:00 - 9:50 AM
            (time(10, 0), time(10, 50)), # 10:00 - 10:50 AM
            (time(11, 0), time(11, 50)), # 11:00 - 11:50 AM
            (time(12, 0), time(12, 50)), # 12:00 - 12:50 PM
            (time(14, 0), time(14, 50)), # 2:00 - 2:50 PM (after lunch break)
            (time(15, 0), time(15, 50)), # 3:00 - 3:50 PM
        ]

        # Create time slots for each day and lecture time
        count = 0
        for day_code, day_name in days:
            for start_time, end_time in lecture_times:
                # Check if this time slot already exists
                time_slot, created = TimeSlot.objects.get_or_create(
                    day=day_code,
                    start_time=start_time,
                    end_time=end_time
                )
                
                if created:
                    count += 1
                    self.stdout.write(f"Created time slot: {day_name} {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")

        if count > 0:
            self.stdout.write(self.style.SUCCESS(f'Successfully created {count} time slots'))
        else:
            self.stdout.write(self.style.WARNING('No new time slots created. They might already exist.'))
