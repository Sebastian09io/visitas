from django.urls import path
from apps.visitas import views

app_name = 'visitas'

urlpatterns = [
    path('home_visita/', views.home_visita, name='home_visita'),
    path('guardar_visita/', views.guardar_visita, name='guardar_visita'),

]
