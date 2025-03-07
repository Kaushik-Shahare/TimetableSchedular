from django import template
from django.utils.safestring import mark_safe
import hashlib

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using key"""
    return dictionary.get(key)

@register.filter
def get_faculty_name(faculties, faculty_id):
    for faculty in faculties:
        if str(faculty.id) == str(faculty_id):
            return faculty.name
    return "Unknown"

@register.filter
def get_course_name(courses, course_id):
    for course in courses:
        if str(course.id) == str(course_id):
            return f"{course.code}: {course.name}"
    return "Unknown"

@register.filter
def get_room_name(rooms, room_id):
    for room in rooms:
        if str(room.id) == str(room_id):
            return room.name
    return "Unknown"

@register.filter
def get_day_name(day_code):
    day_dict = dict([
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
    ])
    return day_dict.get(day_code, day_code)

@register.filter
def generate_color(text):
    """Generate a consistent color based on text input"""
    hash_obj = hashlib.md5(text.encode())
    hash_int = int(hash_obj.hexdigest(), 16)
    hue = hash_int % 360
    return f"hsl({hue}, 70%, 60%)"
