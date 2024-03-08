# urls.py
from django.urls import path
from .views import upload_file,success_view

urlpatterns = [
    path('upload/', upload_file, name='upload_file'),
     path('success/<str:file_name>/', success_view, name='success_view'),
]
