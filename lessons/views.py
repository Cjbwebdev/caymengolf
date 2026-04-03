from django.shortcuts import render

def lessons_page(request):
    from lessons.models import LessonType
    types = LessonType.objects.filter(is_active=True)
    return render(request, "pages/lessons.html", {"lesson_types": types})
