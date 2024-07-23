from django.urls import path
from apps.visitas import views

app_name = 'visitas'

urlpatterns = [
    path('home_visita/', views.home_visita, name='home_visita'),

]
