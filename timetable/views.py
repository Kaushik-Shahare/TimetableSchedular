from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import IntegrityError
from django.http import JsonResponse
from datetime import time
import io
from contextlib import redirect_stdout
from django.core.management import call_command

from .models import Faculty, Course, Room, TimeSlot, FacultyAvailability, Schedule
from .scheduler import TimetableScheduler
from .forms import FacultyForm, CourseForm, RoomForm, TimeSlotForm, FacultyAvailabilityForm
from .algorithm_visualizer import AnimatedTimetableScheduler

# Create your views here.
def home(request):
    return render(request, 'timetable/home.html')

class FacultyListView(ListView):
    model = Faculty
    context_object_name = 'faculties'
    template_name = 'timetable/faculty/list.html'

class FacultyCreateView(CreateView):
    model = Faculty
    form_class = FacultyForm
    template_name = 'timetable/faculty/form.html'
    success_url = reverse_lazy('faculty-list')

class CourseListView(ListView):
    model = Course
    context_object_name = 'courses'
    template_name = 'timetable/course/list.html'

class CourseCreateView(CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'timetable/course/form.html'
    success_url = reverse_lazy('course-list')

class RoomListView(ListView):
    model = Room
    context_object_name = 'rooms'
    template_name = 'timetable/room/list.html'

class RoomCreateView(CreateView):
    model = Room
    form_class = RoomForm
    template_name = 'timetable/room/form.html'
    success_url = reverse_lazy('room-list')

class TimeSlotListView(ListView):
    model = TimeSlot
    context_object_name = 'timeslots'
    template_name = 'timetable/timeslot/list.html'

class TimeSlotCreateView(CreateView):
    model = TimeSlot
    form_class = TimeSlotForm
    template_name = 'timetable/timeslot/form.html'
    success_url = reverse_lazy('timeslot-list')

def faculty_availability(request, faculty_id):
    faculty = Faculty.objects.get(id=faculty_id)
    time_slots = TimeSlot.objects.all()
    
    if request.method == 'POST':
        for time_slot in time_slots:
            is_available = request.POST.get(f'timeslot_{time_slot.id}', False) == 'on'
            FacultyAvailability.objects.update_or_create(
                faculty=faculty,
                time_slot=time_slot,
                defaults={'is_available': is_available}
            )
        messages.success(request, f"Availability for {faculty.name} updated successfully.")
        return redirect('faculty-list')
    
    # Get existing availabilities or create defaults
    availabilities = {}
    for time_slot in time_slots:
        availability, created = FacultyAvailability.objects.get_or_create(
            faculty=faculty,
            time_slot=time_slot,
            defaults={'is_available': True}
        )
        availabilities[time_slot.id] = availability.is_available
        
    context = {
        'faculty': faculty,
        'time_slots': time_slots,
        'availabilities': availabilities,
    }
    return render(request, 'timetable/faculty_availability.html', context)

def generate_timetable(request):
    if request.method == 'POST':
        try:
            scheduler = TimetableScheduler()
            schedules = scheduler.generate_timetable()
            
            if schedules:
                messages.success(request, "Timetable generated successfully!")
            else:
                messages.error(request, "Couldn't generate a conflict-free timetable with current constraints.")
                
        except Exception as e:
            messages.error(request, f"Error generating timetable: {str(e)}")
            
        return redirect('view-timetable')
        
    return render(request, 'timetable/generate_timetable.html')

def view_timetable(request):
    days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
    day_names = dict(TimeSlot.DAY_CHOICES)
    
    # Get all schedules
    schedules = Schedule.objects.all().order_by('time_slot__day', 'time_slot__start_time')
    
    # Get all distinct time slots ordered by start time
    all_time_slots = TimeSlot.objects.values('start_time', 'end_time').distinct().order_by('start_time')
    
    # Create a nested dictionary to hold schedule data by time and day
    timetable = {}
    for ts in all_time_slots:
        start_time = ts['start_time']
        end_time = ts['end_time']
        time_key = f"{start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}"
        
        if time_key not in timetable:
            timetable[time_key] = {
                'start_time': start_time,
                'end_time': end_time,
                'days': {day: [] for day in days}  # Initialize empty list for each day
            }
    
    # Populate the timetable with schedules
    for schedule in schedules:
        start_time = schedule.time_slot.start_time
        end_time = schedule.time_slot.end_time
        day = schedule.time_slot.day
        time_key = f"{start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}"
        
        if time_key in timetable:
            timetable[time_key]['days'][day].append(schedule)
    
    # Convert dictionary to sorted list for template
    timetable_list = []
    for time_key, data in sorted(timetable.items()):
        timetable_list.append(data)
    
    context = {
        'schedules': schedules,
        'days': days,
        'day_names': day_names,
        'timetable': timetable_list,
    }
    return render(request, 'timetable/view_timetable.html', context)

def init_default_timeslots(request):
    if request.method == 'POST':
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
        
        if count > 0:
            messages.success(request, f'Successfully created {count} default time slots')
        else:
            messages.info(request, 'No new time slots created. They might already exist.')
        
        return redirect('timeslot-list')
    
    return render(request, 'timetable/init_timeslots.html')

def verbose_generate_timetable(request):
    if request.method == 'POST':
        try:
            # Capture output from algorithm
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                from timetable.management.commands.run_scheduler import VerboseTimetableScheduler
                scheduler = VerboseTimetableScheduler(buffer)
                schedules = scheduler.generate_timetable()
            
            algorithm_output = buffer.getvalue()
            
            if schedules:
                messages.success(request, "Timetable generated successfully!")
            else:
                messages.error(request, "Couldn't generate a conflict-free timetable with current constraints.")
                
            context = {
                'algorithm_output': algorithm_output,
                'schedules': schedules
            }
            return render(request, 'timetable/verbose_timetable_result.html', context)
                
        except Exception as e:
            messages.error(request, f"Error generating timetable: {str(e)}")
            return redirect('view-timetable')
        
    return render(request, 'timetable/generate_timetable.html', {'verbose': True})

def create_sample_data(request):
    if request.method == 'POST':
        try:
            # Capture output from command
            output = io.StringIO()
            call_command('create_sample_data', stdout=output)
            output_text = output.getvalue()
            
            messages.success(request, "Sample data created successfully!")
            return render(request, 'timetable/sample_data_result.html', {'output': output_text})
        except Exception as e:
            messages.error(request, f"Error creating sample data: {str(e)}")
            return redirect('home')
            
    return render(request, 'timetable/create_sample_data.html')

def animated_generate_timetable(request):
    """Generate timetable with animation steps"""
    # Reset any existing session data
    if 'algorithm_steps' in request.session:
        del request.session['algorithm_steps']
        
    return render(request, 'timetable/animated_timetable.html')

def timetable_step(request):
    """AJAX endpoint to get the next step in the timetable generation algorithm"""
    # Get step number from request
    step_number = request.GET.get('step', 0)
    try:
        step_number = int(step_number)
    except ValueError:
        step_number = 0
        
    # Initialize algorithm in session if needed
    if 'algorithm_steps' not in request.session:
        # Create scheduler and initialize steps
        scheduler = AnimatedTimetableScheduler()
        steps = scheduler.initialize()
        
        # Store all steps in session
        request.session['algorithm_steps'] = [step for step in scheduler.steps]
        request.session['stats'] = {
            'assignments_tried': scheduler.assignments_tried,
            'backtracks': scheduler.backtracks,
            'total_steps': len(scheduler.steps)
        }
        
    # Get the requested step
    steps = request.session.get('algorithm_steps', [])
    stats = request.session.get('stats', {})
    
    if step_number < len(steps):
        step = steps[step_number]
        is_complete = step_number >= len(steps) - 1
        next_step = step_number + 1
    else:
        step = {'type': 'complete', 'message': 'Algorithm completed'}
        is_complete = True
        next_step = step_number
        
    return JsonResponse({
        'step': step,
        'completed': is_complete,
        'next_step': next_step,
        'total_steps': len(steps),
        'progress': round((step_number / max(len(steps)-1, 1)) * 100) if len(steps) > 1 else 100,
        'stats': stats
    })
