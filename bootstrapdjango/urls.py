"""URL configuration for bootstrapdjango project."""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from myapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='myapp/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('', views.index, name='index'),
    path('properties/', views.properties, name='properties'),
    path('property-details/', views.about, name='property_details'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
]
