import unittest  # Biblioteca de pruebas unitarias estándar de Python
from django.test import RequestFactory, TestCase  # Utilidades de prueba proporcionadas por Django
from django.contrib.auth import get_user_model  # Utilidad para obtener el modelo de usuario configurado en Django
from django.contrib.sessions.middleware import SessionMiddleware  # Middleware de sesiones de Django

# Importación del formulario personalizado de establecimiento de contraseña
from apps.gestiones.forms import CustomSetPasswordForm  # Ajustar la importación según la ubicación de tu formulario

# Obtener el modelo de usuario personalizado en Django.
User = get_user_model()

# Clase de prueba para el formulario CustomSetPasswordForm
class CustomSetPasswordFormTestCase(TestCase):

    # Configuración inicial antes de cada prueba
    def setUp(self):
        User.objects.filter(correo='testuser@example.com').delete()
        # Crea un nuevo usuario de prueba
        self.user = User.objects.create_user(
            correo='testuser@example.com',
            password='Testpassword123_'
        )
        # Inicializa RequestFactory para simular solicitudes HTTP
        self.factory = RequestFactory()

    # Método auxiliar para añadir middleware de sesión a una solicitud
    def add_middleware(self, request):
        # Añade middleware de sesión y mensajes al request.
        session_middleware = SessionMiddleware(get_response=lambda req: None)
        # Procesa el request a través del middleware
        session_middleware.process_request(request)
        # Guarda la sesión en la solicitud
        request.session.save()
    # Prueba para un formulario válido
    def test_valid_form(self):
        data = {
            'new_password1': 'ElCondor2028_',
            'new_password2': 'ElCondor2028_',
        }
        # Simula una solicitud POST
        request = self.factory.post('/set_password/', data)
        # Añade el middleware de sesión a la solicitud
        self.add_middleware(request)
        # Crea una instancia del formulario con los datos y la solicitud
        form = CustomSetPasswordForm(user=self.user, data=data, request=request)
        # Verifica que el formulario es válido
        self.assertTrue(form.is_valid())

    # Prueba para un formulario inválido con contraseñas que no coinciden
    def test_invalid_form_passwords_not_matching(self):
        # Datos para la solicitud POST con contraseñas que no coinciden
        data = {
            'new_password1': 'ElCondor2028_',
            'new_password2': 'ElElefante2029+',
        }
        # Crea una instancia del formulario con los datos
        form = CustomSetPasswordForm(user=self.user, data=data)
        # Verifica que el formulario no es válido
        self.assertFalse(form.is_valid())
        # Verifica que hay un error en el campo 'new_password2'
        self.assertIn('new_password2', form.errors)

    # Prueba para un formulario inválido con una contraseña faltante
    def test_invalid_form_missing_password(self):
        # Datos para la solicitud POST con una contraseña faltante
        data = {
            'new_password1': 'ElCondor2028_',
            'new_password2': '',
        }
        # Crea una instancia del formulario con los datos
        form = CustomSetPasswordForm(user=self.user, data=data)
        # Verifica que el formulario no es válido
        self.assertFalse(form.is_valid())
        # Verifica que hay un error en el campo 'new_password2'
        self.assertIn('new_password2', form.errors)

    # Limpieza después de cada prueba
    def tearDown(self):
        # Elimina el usuario de prueba
        User.objects.filter(correo='testuser@example.com').delete()

# Punto de entrada para ejecutar las pruebas
if __name__ == '__main__':
    unittest.main()
