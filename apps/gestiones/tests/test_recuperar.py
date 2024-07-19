# Importaciones de Django Test Framework para pruebas unitarias
import unittest
from django.test import Client, RequestFactory

# Importaciones para trabajar con modelos de usuario y tokens de autenticación en Django
from django.contrib.auth import get_user_model

# Importaciones para trabajar con el correo electrónico saliente en pruebas unitarias
from django.core import mail

# Importacions para el manejo de mensajes

from django.contrib import messages
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware

# Importación del formulario que se va a probar
from apps.gestiones.forms import CustomPasswordResetForm

# Obtener el modelo de usuario personalizado en Django, si se ha configurado
User = get_user_model()

class CustomPasswordResetFormTestCase(unittest.TestCase):
    def setUp(self):
        # Configuración inicial: Eliminar cualquier usuario existente con el correo 'test@example.com'
        User.objects.filter(correo='test@example.com').delete()

        # Crear un nuevo usuario de prueba
        self.user = User.objects.create_user(
            correo='test@example.com',
            password='testpassword123_'
        )

        self.factory = RequestFactory()

    def add_middleware(self, request):
        # Añadir middleware de sesión y mensajes a la solicitud
        session_middleware = SessionMiddleware(get_response=lambda req: None)
        session_middleware.process_request(request)
        request.session.save()

        message_middleware = MessageMiddleware(get_response=lambda req: None)
        message_middleware.process_request(request)
        request.session.save()

    def test_invalid_form_no_email(self):
        # Prueba: Formulario inválido sin correo electrónico
        form = CustomPasswordResetForm(data={'correo': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('correo', form.errors)

    def test_invalid_form_email_not_found(self):
        # Prueba: Formulario inválido con correo electrónico no encontrado en la base de datos
        form = CustomPasswordResetForm(data={'correo': 'nonexistent@example.com'})
        self.assertFalse(form.is_valid())
        self.assertIn('correo', form.errors)

    def test_message_sent_on_valid_form_submission(self):
        # Prueba: Mensaje enviado al enviar el formulario con éxito
        form_data = {'correo': 'test@example.com'}

        # Simular el envío del formulario
        client = Client()
        # response = client.post('/recuperar/', form_data)
        response = client.post('/recuperar/', form_data, follow=True)

        # Verificar la redirección y el mensaje de éxito
        self.assertEqual(response.status_code, 200)  # Se confirma que sigue en la misma vista

        # Verificar los mensajes en la respuesta
        messages_sent = [m.message for m in messages.get_messages(response.wsgi_request)]
        self.assertIn('Se ha enviado un correo electrónico para restablecer tu contraseña.', messages_sent)
