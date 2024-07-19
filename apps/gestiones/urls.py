from django.urls import path
from apps.gestiones import views
from django.contrib.auth import views as auth_views
from .views import CustomPasswordResetView
from django.contrib.auth.views import  PasswordChangeDoneView
from .views import CustomPasswordChangeView
app_name = 'gestiones'

urlpatterns = [
    path('',views.Home, name='home'),
    
    path('calendario/',views.calendario, name='calendario'),
    
    path('perfil_usuario/',views.perfil_usuario, name='perfil_usuario'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    path('inhabilitar_cuenta/', views.inhabilitar_cuenta, name='inhabilitar_cuenta'),
    path('actualizar-imagen-perfil/', views.actualizar_imagen_perfil, name='actualizar_imagen_perfil'),
    path('eliminar_imagen_perfil/', views.eliminar_imagen_perfil, name='eliminar_imagen_perfil'),
    path('cambiar-contraseña/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('cambiar-contraseña/hecho/', PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
    
    path('registro/',views.registro, name='registro'),
    path("login/",views.login_view, name="login"),
    path('logout/', views.logout_view, name='logout'),
    
    path('recuperar/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('recuperar/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url='/login/'
    ), name='recuperar_contrasena_confirmado'),
]
