from django.db import models

# Create your models here.
class Faculty(models.Model):
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.name

class TimeSlot(models.Model):
    DAY_CHOICES = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
    ]
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.get_day_display()} {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"

class FacultyAvailability(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ('faculty', 'time_slot')
        verbose_name_plural = 'Faculty Availabilities'

class Room(models.Model):
    name = models.CharField(max_length=50)
    capacity = models.IntegerField()
    has_projector = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Course(models.Model):
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    weekly_sessions = models.IntegerField(default=1)  # Number of sessions per week

    def __str__(self):
        return f"{self.code}: {self.name}"

class Schedule(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('room', 'time_slot')  # A room can only have one class at a time
        
    def __str__(self):
        return f"{self.course} in {self.room} at {self.time_slot}"
