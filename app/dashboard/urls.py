"""Dashboard URL Configuration"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.executive_dashboard, name='executive'),
    path('portfolio/', views.portfolio_report, name='portfolio_report'),
    path('bog/', views.bog_report, name='bog_report'),
    path('api/data/', views.api_dashboard_data, name='api_data'),
]
