from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from apps.funcionarios.models import Persona, TipoDocumento, Cargo, Dependencia

class LoginViewTests(TestCase):

    def setUp(self):
        self.url = reverse('gestiones:login')  # Asegúrate de que el nombre de la URL sea correcto
        self.password = 'password123'
        tipo_documento = TipoDocumento.objects.create(nombre='Cédula')
        cargo = Cargo.objects.create(nombre='Cargo Test')
        dependencia = Dependencia.objects.create(nombre='Dependencia Test')
        
        self.user = Persona.objects.create_user(
            correo='test@example.com',
            password=self.password,
            nombres='Test',
            apellidos='User',
            id_tipo_documento=tipo_documento,
            identificacion='1234567890',
            telefono='9876543210',
            id_cargo=cargo,
            id_dependencia=dependencia,
            is_active=True,
            is_staff=False,
            is_superuser=False,
            is_admin=False
        )
    
    def test_usuario_no_existe(self):
        response = self.client.post(self.url, {'username': 'nonexistent@example.com', 'password': 'password123'})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Por favor, introduzca un correo y clave correctos. Observe que ambos campos pueden ser sensibles a mayúsculas.")

    def test_contraseña_incorrecta(self):
        response = self.client.post(self.url, {'username': 'test@example.com', 'password': 'wrongpassword'})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Por favor, introduzca un correo y clave correctos. Observe que ambos campos pueden ser sensibles a mayúsculas.")

    def test_login_exitoso(self):
        response = self.client.post(self.url, {'username': 'test@example.com', 'password': self.password})
        self.assertRedirects(response, reverse('gestiones:calendario'))
