"""
URL configuration for breakdown app.
"""

from django.urls import path
from . import views

app_name = 'breakdown'

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_document, name='upload_document'),
    path('documents/', views.document_list, name='document_list'),
    path('breakdown/<int:breakdown_id>/', views.breakdown_detail, name='breakdown_detail'),
    path('breakdown/<int:breakdown_id>/regenerate/', views.regenerate_breakdown, name='regenerate_breakdown'),
    path('document/<int:document_id>/delete/', views.delete_document, name='delete_document'),
] 