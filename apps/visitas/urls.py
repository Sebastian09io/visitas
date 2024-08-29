from django.urls import path
from apps.visitas import views

app_name = 'visitas'

urlpatterns = [
    path('home_visita/', views.home_visita, name='home_visita'),
    path('descargar_excel/', views.descargar_excel, name='descargar_excel'),
    path('administrador_visitas/', views.administrador_visitas, name='administrador_visitas'),
    path('buscar_visita/', views.buscar_visita, name='buscar_visita'),
    path('rechazar_visita/<int:visita_id>/', views.rechazar_visita, name='rechazar_visita'),
    path('aprobar_visita/<int:visita_id>/', views.aprobar_visita, name='aprobar_visita'),
    path('verificar_fecha/', views.verificar_fecha, name='verificar_fecha'),
    path('cargar_asistentes/<int:visita_id>/', views.cargar_asistentes, name='cargar_asistentes'),
    path('configuracion_visitas/', views.configuracion_visitas, name='configuracion_visitas'),
    path('eliminar_horario/<int:horario_id>/', views.eliminar_horario, name='eliminar_horario'),

]





