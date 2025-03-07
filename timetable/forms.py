from django import forms
from .models import Faculty, Course, Room, TimeSlot, FacultyAvailability

class FacultyForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = ['name', 'department', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['code', 'name', 'faculty', 'weekly_sessions']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'faculty': forms.Select(attrs={'class': 'form-control'}),
            'weekly_sessions': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'capacity', 'has_projector']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'has_projector': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ['day', 'start_time', 'end_time']
        widgets = {
            'day': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

class FacultyAvailabilityForm(forms.ModelForm):
    class Meta:
        model = FacultyAvailability
        fields = ['faculty', 'time_slot', 'is_available']
