from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("billing/", include("billing.urls")),
    path("", include("pages.urls")),
    path("bookings/", include("bookings.urls")),
    path("golfers/", include("golfers.urls")),
    path("lessons/", include("lessons.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
]
