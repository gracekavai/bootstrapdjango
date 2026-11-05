from django.urls import path

from myapp import views

urlpatterns = [
    path('', views.index, name='index'),
    path('properties/', views.properties, name='properties'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
]