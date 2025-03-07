from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    # Faculty URLs
    path('faculty/', views.FacultyListView.as_view(), name='faculty-list'),
    path('faculty/add/', views.FacultyCreateView.as_view(), name='faculty-add'),
    path('faculty/<int:faculty_id>/availability/', views.faculty_availability, name='faculty-availability'),
    
    # Course URLs
    path('course/', views.CourseListView.as_view(), name='course-list'),
    path('course/add/', views.CourseCreateView.as_view(), name='course-add'),
    
    # Room URLs
    path('room/', views.RoomListView.as_view(), name='room-list'),
    path('room/add/', views.RoomCreateView.as_view(), name='room-add'),
    
    # TimeSlot URLs
    path('timeslot/', views.TimeSlotListView.as_view(), name='timeslot-list'),
    path('timeslot/add/', views.TimeSlotCreateView.as_view(), name='timeslot-add'),
    path('timeslot/init-default/', views.init_default_timeslots, name='init-default-timeslots'),
    
    # Timetable generation and viewing
    path('generate/', views.generate_timetable, name='generate-timetable'),
    path('generate/verbose/', views.verbose_generate_timetable, name='generate-timetable-verbose'),
    path('timetable/', views.view_timetable, name='view-timetable'),

    # Add these URL patterns
    path('sample-data/', views.create_sample_data, name='create-sample-data'),
    path('generate/animated/', views.animated_generate_timetable, name='generate-timetable-animated'),
    path('generate/step/', views.timetable_step, name='timetable-step'),
]
