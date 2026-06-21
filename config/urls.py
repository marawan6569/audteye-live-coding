from django.urls import path, include

from jobs.views import health

urlpatterns = [
    path('api/health/', health),
    path('api/', include('jobs.urls')),
]
