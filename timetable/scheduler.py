from .models import Course, Faculty, Room, TimeSlot, FacultyAvailability, Schedule
import random

class TimetableScheduler:
    def __init__(self):
        self.courses = Course.objects.all()
        self.rooms = Room.objects.all()
        self.time_slots = TimeSlot.objects.all()
        self.schedule = []
        
    def generate_timetable(self):
        """
        Generate a timetable using backtracking with graph coloring principles.
        Each course needs to be assigned a (room, time_slot) combination that satisfies all constraints.
        """
        # Clear any existing schedules
        Schedule.objects.all().delete()
        
        # Sort courses by constraints (courses with most constraints first)
        courses_with_sessions = []
        
        # 1. First add courses with higher weekly sessions as they have more constraints
        for course in sorted(self.courses, key=lambda x: x.weekly_sessions, reverse=True):
            for i in range(course.weekly_sessions):
                courses_with_sessions.append((course, i+1))
        
        # 2. Track faculty assignments to ensure even distribution across days
        faculty_day_assignments = {}
        for faculty in Faculty.objects.all():
            faculty_day_assignments[faculty.id] = {'MON': 0, 'TUE': 0, 'WED': 0, 'THU': 0, 'FRI': 0, 'SAT': 0}
            
        # Start the backtracking algorithm
        success = self._schedule_courses(courses_with_sessions, faculty_day_assignments)
        
        if not success:
            print("Failed to generate a complete schedule with the given constraints.")
        
        return Schedule.objects.all()
    
    def _schedule_courses(self, courses_to_schedule, faculty_day_assignments, index=0):
        """
        Backtracking algorithm to schedule courses
        """
        # Base case: all courses are scheduled
        if index >= len(courses_to_schedule):
            return True
            
        course, session = courses_to_schedule[index]
        faculty = course.faculty
        
        # Get available time slots for this faculty
        faculty_availabilities = FacultyAvailability.objects.filter(
            faculty=faculty, is_available=True
        ).values_list('time_slot_id', flat=True)
        
        available_time_slots = list(TimeSlot.objects.filter(id__in=faculty_availabilities))
        
        # 3. Sort time slots to prioritize days with fewer assignments for this faculty
        available_time_slots.sort(
            key=lambda ts: (faculty_day_assignments[faculty.id][ts.day], random.random())
        )
        
        # Track assigned time slots for this course to avoid scheduling multiple sessions on same day
        course_days = set()
        for sched in Schedule.objects.filter(course=course):
            course_days.add(sched.time_slot.day)
        
        for time_slot in available_time_slots:
            # 4. Try to distribute course sessions across different days 
            if session > 1 and time_slot.day in course_days and len(course_days) < faculty.course_set.count():
                continue
                
            # Check if faculty is already scheduled for this time slot
            if Schedule.objects.filter(course__faculty=faculty, time_slot=time_slot).exists():
                continue
                
            # Try each available room
            rooms_to_try = list(self.rooms)
            
            # 5. Prioritize rooms with appropriate capacity for the course
            random.shuffle(rooms_to_try)  # Add some randomness to avoid same room assignments
            
            for room in rooms_to_try:
                # Check if room is already booked for this time slot
                if Schedule.objects.filter(room=room, time_slot=time_slot).exists():
                    continue
                    
                # Create a tentative schedule
                schedule = Schedule(course=course, room=room, time_slot=time_slot)
                schedule.save()
                
                # Update faculty day assignments count
                faculty_day_assignments[faculty.id][time_slot.day] += 1
                if time_slot.day not in course_days:
                    course_days.add(time_slot.day)
                
                # Recursively try to schedule the next course
                if self._schedule_courses(courses_to_schedule, faculty_day_assignments, index + 1):
                    return True
                    
                # If we reach here, this assignment didn't work, so remove it and try another
                faculty_day_assignments[faculty.id][time_slot.day] -= 1
                if schedule.time_slot.day in course_days and not Schedule.objects.filter(
                    course=course, time_slot__day=schedule.time_slot.day
                ).exclude(id=schedule.id).exists():
                    course_days.remove(schedule.time_slot.day)
                
                schedule.delete()
        
        # If no assignment worked, return False
        return False
