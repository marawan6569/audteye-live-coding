from django.urls import path

from jobs.views import create_job, get_job

urlpatterns = [
    path('jobs/', create_job),
    path('jobs/<str:job_id>/', get_job),
]
