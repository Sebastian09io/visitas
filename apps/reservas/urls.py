from django.urls import path, include
from apps.reservas import views
from .views import CustomPasswordChangeView
from django.contrib.auth.views import PasswordChangeDoneView
from rest_framework.routers import DefaultRouter
from apps.reservas.views import ReservaViewSet

app_name = 'reservas'

router = DefaultRouter()
router.register(r'reservas', ReservaViewSet)

urlpatterns = [

    #rutas administracion
    path('gestion_reserva/', views.gestion_reserva, name='gestion_reserva'),
    path('administracion_reservas/', views.administracion_reservas, name='administracion_reservas'),
    path('gestion_funcionario/', views.gestion_funcionario, name='gestion_funcionario'),
    path('buscar_funcionario/', views.buscar_funcionario, name='buscar_funcionario'),

    path('gestion_perfil/', views.gestion_perfil, name='gestion_perfil'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    path('inhabilitar_cuenta/', views.inhabilitar_cuenta, name='inhabilitar_cuenta'),
    path('actualizar-imagen-perfil/', views.actualizar_imagen_perfil, name='actualizar_imagen_perfil'),
    path('eliminar_imagen_perfil/', views.eliminar_imagen_perfil, name='eliminar_imagen_perfil'),
    path('cambiar-contraseña/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('cambiar-contraseña/hecho/', PasswordChangeDoneView.as_view(
        template_name='password_change_done.html'
    ), name='password_change_done'),

    path('gestion_implemento/', views.gestion_implemento, name='gestion_implemento'),
    path('registrar_implemento/', views.registrar_implemento, name='registrar_implemento'),
    path('buscar_implemento/', views.buscar_implemento, name='buscar_implemento'),
    path('eliminar_implemento/<int:implemento_id>/', views.eliminar_implemento, name='eliminar_implemento'),

    path('gestion_espacio/', views.gestion_espacio, name='gestion_espacio'),
    path('registrar_espacio/', views.registrar_espacio, name='registrar_espacio'),
    path('buscar_espacio/', views.buscar_espacio, name='buscar_espacio'),
    path('eliminar_espacio/<int:espacio_id>/', views.eliminar_espacio, name='eliminar_espacio'),

    path('registro_temporal/', views.registro_temporal, name='registro_temporal'),
    path('api/', include(router.urls)), # api Reservas

    ] 
