from .models import Course, Faculty, Room, TimeSlot, FacultyAvailability, Schedule
import time
import json
import random

class AnimatedTimetableScheduler:
    """
    A version of the timetable scheduler that provides step-by-step updates
    for animation and visualization.
    """
    def __init__(self):
        self.courses = Course.objects.all()
        self.rooms = Room.objects.all()
        self.time_slots = TimeSlot.objects.all()
        self.steps = []
        self.assignments_tried = 0
        self.backtracks = 0
        self.current_step = 0
        
    def get_step(self, step_number):
        """Get a specific step from the algorithm execution"""
        if step_number < len(self.steps):
            return self.steps[step_number]
        return None
    
    def get_next_step(self):
        """Get the next step and update the current step counter"""
        if self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            self.current_step += 1
            return step
        return {'type': 'complete', 'message': 'Algorithm completed'}
    
    def add_step(self, step_type, **kwargs):
        """Add a step to the algorithm execution history"""
        step = {'type': step_type, **kwargs}
        self.steps.append(step)
        return step
    
    def initialize(self):
        """Initialize the algorithm and return the first few steps"""
        # Clear any existing steps
        self.steps = []
        self.current_step = 0
        self.assignments_tried = 0
        self.backtracks = 0
        
        # Clear any existing schedules
        Schedule.objects.all().delete()
        
        self.add_step('init', message='Starting timetable generation algorithm...')
        self.add_step('info', message='Clearing existing schedules...')
        
        # Generate courses with sessions
        courses_with_sessions = []
        for course in self.courses:
            for i in range(course.weekly_sessions):
                courses_with_sessions.append((course, i+1))
                self.add_step('info', 
                             message=f"Added {course.code}: {course.name}, Session {i+1}/{course.weekly_sessions}")
        
        self.add_step('info', 
                     message=f"Found {len(self.courses)} courses with {len(courses_with_sessions)} total sessions")
        
        # Initialize the scheduling process
        self.schedule_courses_step_by_step(courses_with_sessions)
        
        # Return the initial steps
        return self.steps[:5]  # First 5 steps
    
    def schedule_courses_step_by_step(self, courses_to_schedule, index=0, depth=0):
        """
        Run the algorithm and generate all steps at once.
        In a real implementation, this would be done incrementally.
        """
        # For this mock version, we'll generate some synthetic steps
        if index >= len(courses_to_schedule):
            self.add_step('complete', message="All courses successfully scheduled!")
            return True
            
        course, session = courses_to_schedule[index]
        self.add_step('course', 
                     message=f"Scheduling {course.code} (Session {session}/{course.weekly_sessions})",
                     course_code=course.code,
                     course_name=course.name,
                     session=session,
                     total_sessions=course.weekly_sessions,
                     depth=depth)
        
        # Get available time slots for this faculty
        faculty = course.faculty
        faculty_availabilities = FacultyAvailability.objects.filter(
            faculty=faculty, is_available=True
        ).values_list('time_slot_id', flat=True)
        
        available_time_slots = list(TimeSlot.objects.filter(id__in=faculty_availabilities))
        
        self.add_step('info', 
                     message=f"Faculty {faculty.name} has {len(available_time_slots)} available time slots",
                     faculty_name=faculty.name,
                     available_slots=len(available_time_slots),
                     depth=depth)
        
        # Try room and time slot combinations
        success = False
        
        # Shuffle time slots and rooms to get different results each time
        random.shuffle(available_time_slots)
        rooms = list(self.rooms)
        random.shuffle(rooms)
        
        for time_slot in available_time_slots:
            # Check if faculty is already scheduled
            if Schedule.objects.filter(course__faculty=faculty, time_slot=time_slot).exists():
                self.add_step('conflict', 
                             message=f"Skip time slot {time_slot}: Faculty {faculty.name} already scheduled",
                             faculty_name=faculty.name,
                             time_slot=str(time_slot),
                             reason="faculty_conflict",
                             depth=depth)
                continue
                
            for room in rooms:
                self.assignments_tried += 1
                
                # Check if room is already booked
                if Schedule.objects.filter(room=room, time_slot=time_slot).exists():
                    self.add_step('conflict', 
                                 message=f"Skip room {room.name} at {time_slot}: Room already booked",
                                 room_name=room.name,
                                 time_slot=str(time_slot),
                                 reason="room_conflict",
                                 depth=depth)
                    continue
                
                # Try this assignment
                self.add_step('attempt', 
                             message=f"Try: {course.code} in {room.name} at {time_slot}",
                             course_code=course.code,
                             course_name=course.name,
                             room_name=room.name,
                             room_id=room.id,
                             time_slot=str(time_slot),
                             time_slot_id=time_slot.id,
                             result="trying",
                             depth=depth)
                
                # Add a schedule entry
                schedule = Schedule.objects.create(
                    course=course, 
                    room=room, 
                    time_slot=time_slot
                )
                
                # Recursively try to schedule next course
                if self.schedule_courses_step_by_step(courses_to_schedule, index + 1, depth + 1):
                    self.add_step('success', 
                                 message=f"Assigned {course.code} to {room.name} at {time_slot}",
                                 course_code=course.code,
                                 course_name=course.name,
                                 room_name=room.name,
                                 time_slot=str(time_slot),
                                 depth=depth)
                    success = True
                    break
                
                # If we get here, this assignment didn't work
                self.add_step('backtrack', 
                             message=f"Backtrack: Remove {course.code} from {room.name} at {time_slot}",
                             course_code=course.code,
                             course_name=course.name,
                             room_name=room.name,
                             time_slot=str(time_slot),
                             depth=depth)
                
                schedule.delete()
                self.backtracks += 1
            
            if success:
                break
        
        if not success:
            self.add_step('failure', 
                         message=f"Failed to find valid slot for {course.code}",
                         course_code=course.code,
                         course_name=course.name,
                         depth=depth)
                
        return success
