"""
URL configuration for comparison_ai app.
"""

from django.urls import path
from . import views

app_name = 'comparison_ai'

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_comparison, name='create_comparison'),
    path('comparison/<int:comparison_id>/', views.comparison_detail, name='comparison_detail'),
    path('comparison/<int:comparison_id>/viewer/', views.comparison_viewer, name='comparison_viewer'),
    path('comparison/<int:comparison_id>/run-analysis/', views.run_analysis, name='run_analysis'),
    path('comparison/<int:comparison_id>/add-comment/', views.add_comment, name='add_comment'),
    path('comparisons/', views.comparison_list, name='comparison_list'),
    path('comparison/<int:comparison_id>/delete/', views.delete_comparison, name='delete_comparison'),
] 