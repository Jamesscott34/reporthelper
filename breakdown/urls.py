"""
URL configuration for breakdown app.
"""

from django.urls import path
from . import views

app_name = 'breakdown'

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_document, name='upload'),
    path('upload/<int:document_id>/progress/', views.upload_progress, name='upload_progress'),
    path('breakdown/<int:breakdown_id>/', views.breakdown_detail, name='breakdown_detail'),
    path('breakdown/<int:breakdown_id>/viewer/', views.breakdown_viewer, name='breakdown_viewer'),
    path('breakdown/<int:breakdown_id>/status/', views.breakdown_status, name='breakdown_status'),
    path('breakdown/<int:breakdown_id>/regenerate/', views.regenerate_breakdown, name='regenerate_breakdown'),
    path('breakdown/<int:breakdown_id>/custom-prompt/', views.custom_prompt, name='custom_prompt'),
    path('breakdown/<int:breakdown_id>/regenerate-with-comments/', views.regenerate_with_comments, name='regenerate_with_comments'),
    path('documents/', views.document_list, name='document_list'),
    path('documents/<int:document_id>/delete/', views.delete_document, name='delete_document'),
] 