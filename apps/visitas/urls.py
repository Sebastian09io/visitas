from django.urls import path
from apps.visitas import views

app_name = 'visitas'

urlpatterns = [
    path('home_visita/', views.home_visita, name='home_visita'),
    path('descargar-excel/', views.descargar_excel, name='descargar_excel'),
        path('administrador_visitas/', views.administrador_visitas, name='administrador_visitas'),


]
