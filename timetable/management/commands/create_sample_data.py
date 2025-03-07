from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import time
from timetable.models import Faculty, Course, Room, TimeSlot, FacultyAvailability, Schedule

class Command(BaseCommand):
    help = 'Create sample data for timetable application'

    def handle(self, *args, **kwargs):
        try:
            with transaction.atomic():
                self.stdout.write("Creating sample data...")
                
                # Create faculties
                self.stdout.write("Creating faculty members...")
                faculties = [
                    Faculty.objects.create(name="Dr. John Smith", department="Computer Science", email="john.smith@example.com"),
                    Faculty.objects.create(name="Dr. Emily Johnson", department="Mathematics", email="emily.johnson@example.com"),
                    Faculty.objects.create(name="Dr. Michael Davis", department="Physics", email="michael.davis@example.com"),
                    Faculty.objects.create(name="Dr. Sarah Wilson", department="Chemistry", email="sarah.wilson@example.com"),
                    Faculty.objects.create(name="Dr. Robert Brown", department="Computer Science", email="robert.brown@example.com"),
                ]
                self.stdout.write(self.style.SUCCESS(f"Created {len(faculties)} faculty members"))

                # Create rooms
                self.stdout.write("Creating rooms...")
                rooms = [
                    Room.objects.create(name="Room 101", capacity=30, has_projector=True),
                    Room.objects.create(name="Room 102", capacity=45, has_projector=True),
                    Room.objects.create(name="Lab 201", capacity=25, has_projector=True),
                    Room.objects.create(name="Lecture Hall A", capacity=100, has_projector=True),
                    Room.objects.create(name="Seminar Room B", capacity=20, has_projector=False),
                ]
                self.stdout.write(self.style.SUCCESS(f"Created {len(rooms)} rooms"))

                # Create time slots (check if they exist first)
                self.stdout.write("Creating time slots if needed...")
                days = [
                    ('MON', 'Monday'),
                    ('TUE', 'Tuesday'),
                    ('WED', 'Wednesday'),
                    ('THU', 'Thursday'),
                    ('FRI', 'Friday'),
                ]
                
                lecture_times = [
                    (time(9, 0), time(9, 50)),
                    (time(10, 0), time(10, 50)),
                    (time(11, 0), time(11, 50)),
                    (time(12, 0), time(12, 50)),
                    (time(14, 0), time(14, 50)),
                    (time(15, 0), time(15, 50)),
                ]
                
                time_slots = []
                for day_code, day_name in days:
                    for start_time, end_time in lecture_times:
                        time_slot, created = TimeSlot.objects.get_or_create(
                            day=day_code,
                            start_time=start_time,
                            end_time=end_time
                        )
                        time_slots.append(time_slot)
                        if created:
                            self.stdout.write(f"Created time slot: {day_name} {start_time} - {end_time}")
                
                self.stdout.write(self.style.SUCCESS(f"Ensured {len(time_slots)} time slots exist"))

                # Create courses
                self.stdout.write("Creating courses...")
                courses = [
                    Course.objects.create(code="CS101", name="Introduction to Programming", faculty=faculties[0], weekly_sessions=3),
                    Course.objects.create(code="CS201", name="Data Structures", faculty=faculties[0], weekly_sessions=2),
                    Course.objects.create(code="CS301", name="Database Systems", faculty=faculties[4], weekly_sessions=2),
                    Course.objects.create(code="MATH101", name="Calculus I", faculty=faculties[1], weekly_sessions=3),
                    Course.objects.create(code="MATH201", name="Linear Algebra", faculty=faculties[1], weekly_sessions=2),
                    Course.objects.create(code="PHY101", name="Physics I", faculty=faculties[2], weekly_sessions=3),
                    Course.objects.create(code="PHY201", name="Quantum Mechanics", faculty=faculties[2], weekly_sessions=2),
                    Course.objects.create(code="CHEM101", name="Chemistry I", faculty=faculties[3], weekly_sessions=2),
                    Course.objects.create(code="CS401", name="Artificial Intelligence", faculty=faculties[4], weekly_sessions=2),
                ]
                self.stdout.write(self.style.SUCCESS(f"Created {len(courses)} courses"))

                # Set faculty availability (make most time slots available)
                self.stdout.write("Setting faculty availability...")
                availability_count = 0
                
                for faculty in faculties:
                    for time_slot in time_slots:
                        # Make most slots available, but create some constraints
                        is_available = True
                        
                        # Dr. John Smith is not available Monday mornings
                        if faculty.name == "Dr. John Smith" and time_slot.day == "MON" and time_slot.start_time.hour < 12:
                            is_available = False
                            
                        # Dr. Emily Johnson is not available Friday afternoons
                        if faculty.name == "Dr. Emily Johnson" and time_slot.day == "FRI" and time_slot.start_time.hour >= 12:
                            is_available = False
                            
                        # Dr. Michael Davis is not available after 3 PM any day
                        if faculty.name == "Dr. Michael Davis" and time_slot.start_time.hour >= 15:
                            is_available = False
                        
                        FacultyAvailability.objects.create(
                            faculty=faculty,
                            time_slot=time_slot,
                            is_available=is_available
                        )
                        availability_count += 1
                
                self.stdout.write(self.style.SUCCESS(f"Set {availability_count} faculty availability records"))
                
                self.stdout.write(self.style.SUCCESS("Sample data creation completed successfully!"))
                
                self.stdout.write("\nYou can now run the timetable generator to create a schedule.")
                self.stdout.write("Use the web interface or run 'python manage.py run_scheduler --verbose'")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating sample data: {str(e)}"))
