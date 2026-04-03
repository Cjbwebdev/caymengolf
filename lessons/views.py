from bookings.views import lesson_page
from django.shortcuts import render

def lessons_view(request):
    return lesson_page(request)
