from django.core.management.base import BaseCommand
from django.db import transaction
from timetable.models import Course, Faculty, Room, TimeSlot, FacultyAvailability, Schedule
import time as time_lib

class VerboseTimetableScheduler:
    def __init__(self, stdout):
        self.courses = Course.objects.all()
        self.rooms = Room.objects.all()
        self.time_slots = TimeSlot.objects.all()
        self.schedule = []
        self.stdout = stdout
        self.indent = 0
        self.assignments_tried = 0
        self.backtracks = 0
        
    def log(self, message):
        self.stdout.write(' ' * self.indent + message)
        
    def generate_timetable(self):
        """
        Generate a timetable using backtracking with graph coloring principles.
        Each course needs to be assigned a (room, time_slot) combination that satisfies all constraints.
        """
        start_time = time_lib.time()
        
        # Clear any existing schedules
        self.log("Clearing existing schedules...")
        Schedule.objects.all().delete()
        
        # Sort courses by constraints (courses with most constraints first)
        courses_with_sessions = []
        self.log("Expanding courses to individual sessions...")
        
        for course in self.courses:
            for i in range(course.weekly_sessions):
                courses_with_sessions.append((course, i+1))
                self.log(f"  Added {course.code}: {course.name}, Session {i+1}")
        
        # Start the backtracking algorithm
        self.log("\nStarting backtracking algorithm...")
        result = self._schedule_courses(courses_with_sessions)
        
        end_time = time_lib.time()
        duration = end_time - start_time
        
        self.log("")
        if result:
            self.log(self.stdout.style.SUCCESS(f"Successfully generated timetable in {duration:.2f} seconds"))
            self.log(f"Tried {self.assignments_tried} assignments with {self.backtracks} backtracks")
        else:
            self.log(self.stdout.style.ERROR("Failed to generate a conflict-free timetable with current constraints"))
        
        return Schedule.objects.all()
    
    def _schedule_courses(self, courses_to_schedule, index=0):
        """
        Backtracking algorithm to schedule courses
        """
        # Base case: all courses are scheduled
        if index >= len(courses_to_schedule):
            self.log(self.stdout.style.SUCCESS("All courses successfully scheduled!"))
            return True
            
        course, session = courses_to_schedule[index]
        self.indent += 2
        self.log(f"Scheduling {course.code} (Session {session}/{course.weekly_sessions})")
        
        faculty = course.faculty
        
        # Get available time slots for this faculty
        faculty_availabilities = FacultyAvailability.objects.filter(
            faculty=faculty, is_available=True
        ).values_list('time_slot_id', flat=True)
        
        available_time_slots = TimeSlot.objects.filter(id__in=faculty_availabilities)
        self.log(f"Faculty {faculty.name} has {available_time_slots.count()} available time slots")
        
        # Track assigned time slots for this course to avoid scheduling multiple sessions on same day
        course_days = set()
        for sched in Schedule.objects.filter(course=course):
            course_days.add(sched.time_slot.day)
            self.log(f"Course {course.code} already scheduled on {sched.time_slot.day}")
        
        for time_slot in available_time_slots:
            # Try to distribute course sessions across different days 
            if session > 1 and time_slot.day in course_days:
                self.log(f"  ❌ Skip time slot {time_slot}: Already have a session on {time_slot.day}")
                continue
                
            # Check if faculty is already scheduled for this time slot
            if Schedule.objects.filter(course__faculty=faculty, time_slot=time_slot).exists():
                self.log(f"  ❌ Skip time slot {time_slot}: Faculty {faculty.name} already scheduled")
                continue
                
            # Try each available room
            for room in self.rooms:
                self.assignments_tried += 1
                # Check if room is already booked for this time slot
                if Schedule.objects.filter(room=room, time_slot=time_slot).exists():
                    self.log(f"  ❌ Skip room {room.name} at {time_slot}: Room already booked")
                    continue
                
                self.log(f"  ✅ Try: {course.code} in {room.name} at {time_slot}")
                    
                # Create a tentative schedule
                schedule = Schedule(course=course, room=room, time_slot=time_slot)
                schedule.save()
                
                # Recursively try to schedule the next course
                self.indent += 2
                if self._schedule_courses(courses_to_schedule, index + 1):
                    self.indent -= 2
                    return True
                self.indent -= 2
                    
                # If we reach here, this assignment didn't work, so remove it and try another
                self.log(f"  ⏪ Backtrack: Removing {course.code} from {room.name} at {time_slot}")
                schedule.delete()
                self.backtracks += 1
        
        self.log(f"❗ Failed to find valid slot for {course.code}")
        self.indent -= 2
        # If no assignment worked, return False
        return False

class Command(BaseCommand):
    help = 'Run the timetable scheduling algorithm'

    def add_arguments(self, parser):
        parser.add_argument('--verbose', action='store_true', help='Display detailed algorithm steps')

    def handle(self, *args, **kwargs):
        try:
            with transaction.atomic():
                self.stdout.write("Running timetable scheduler...")
                
                if kwargs['verbose']:
                    scheduler = VerboseTimetableScheduler(self.stdout)
                    schedules = scheduler.generate_timetable()
                else:
                    # Use regular scheduler without verbose output
                    from timetable.scheduler import TimetableScheduler
                    scheduler = TimetableScheduler()
                    schedules = scheduler.generate_timetable()
                
                if schedules.exists():
                    # Print a summary of the generated schedule
                    self.stdout.write(self.style.SUCCESS(f"Successfully created {schedules.count()} scheduled classes"))
                    
                    # Print a simple text representation of the timetable
                    days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
                    day_names = {'MON': 'Monday', 'TUE': 'Tuesday', 'WED': 'Wednesday', 
                                'THU': 'Thursday', 'FRI': 'Friday', 'SAT': 'Saturday'}
                    
                    for day in days:
                        day_schedules = schedules.filter(time_slot__day=day).order_by('time_slot__start_time')
                        if day_schedules:
                            self.stdout.write(f"\n{day_names[day]}")
                            self.stdout.write("="*len(day_names[day]))
                            for schedule in day_schedules:
                                self.stdout.write(f"{schedule.time_slot.start_time} - {schedule.time_slot.end_time}: "
                                              f"{schedule.course.code} ({schedule.room.name}) - {schedule.course.faculty.name}")
                else:
                    self.stdout.write(self.style.ERROR("Failed to generate a valid timetable"))
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error running scheduler: {str(e)}"))
