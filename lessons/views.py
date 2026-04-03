from bookings.views import lessons_page
from django.shortcuts import render

def lessons_view(request):
    return lessons_page(request)
