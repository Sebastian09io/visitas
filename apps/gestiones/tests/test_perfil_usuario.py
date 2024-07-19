from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.funcionarios.models import TipoDocumento, Cargo, Dependencia
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class GestionPerfilTests(TestCase):
    def setUp(self):
        """
        Configura el entorno de prueba creando un usuario y otros datos necesarios.
        """
        self.client = Client()
        
        # Crear tipos de documentos de prueba
        self.tipo_cc = TipoDocumento.objects.create(nombre='CC')
        self.tipo_ce = TipoDocumento.objects.create(nombre='CE')

        # Crear cargos de prueba
        self.cargo_gerente = Cargo.objects.create(nombre='Gerente')
        self.cargo_analista = Cargo.objects.create(nombre='Experto')
        
        # Crear dependencias de prueba
        self.dependencia_it = Dependencia.objects.create(nombre='Tecnoparque')
        self.dependencia_rrhh = Dependencia.objects.create(nombre='Sennova')
        
        # Crear un usuario de prueba con acceso de superusuario
        self.user = User.objects.create_user(
            correo='testuser@example.com',
            password='testpassword',
            nombres='Test',
            apellidos='User',
            id_tipo_documento=self.tipo_cc,
            identificacion='1234567890',
            telefono='1234567890',
            id_cargo=self.cargo_gerente,
            id_dependencia=self.dependencia_it,
            is_superuser=False,  # Establecer is_superuser en False
            imagen_perfil=None  # Inicializar sin imagen de perfil
        )
        self.client.login(correo='testuser@example.com', password='testpassword')

    def test_cerrar_sesion(self):
        """
        Prueba para cerrar sesión.
        """
        url = reverse('gestiones:cerrar_sesion')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirección tras cerrar sesión
        self.assertRedirects(response, reverse('gestiones:login'))

    def test_inhabilitar_cuenta(self):
        """
        Prueba para inhabilitar la cuenta del usuario.
        """
        url = reverse('gestiones:inhabilitar_cuenta')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Redirección tras inhabilitar cuenta
        self.user.refresh_from_db()
        self.assertFalse(self.user.estado)

    def test_actualizar_imagen_perfil(self):
        """
        Prueba para actualizar la imagen de perfil del usuario.
        """
        url = reverse('gestiones:actualizar_imagen_perfil')
        image = SimpleUploadedFile("profile_pic.jpg", b"file_content", content_type="image/jpeg")
        response = self.client.post(url, {'imagen_perfil': image}, format='multipart')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('success' in response.json())
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.imagen_perfil)

    def test_eliminar_imagen_perfil(self):
        """
        Prueba para eliminar la imagen de perfil del usuario.
        """
        self.user.imagen_perfil = SimpleUploadedFile("profile_pic.jpg", b"file_content", content_type="image/jpeg")
        self.user.save()
        url = reverse('gestiones:eliminar_imagen_perfil')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)


    def test_listar_datos_perfil(self):
        """
        Prueba para listar/traer datos a los campos del formulario de perfil.
        """
        url = reverse('gestiones:perfil_usuario')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.nombres)
        self.assertContains(response, self.user.apellidos)
        self.assertContains(response, self.user.correo)

    def test_actualizar_perfil(self):
        """
        Prueba para actualizar/editar campos del formulario de perfil.
        """
        url = reverse('gestiones:perfil_usuario')
        data = {
            'nombres': 'Updated',
            'apellidos': 'User',
            'correo': 'updated@example.com',
            'telefono': '0987654321',
            'id_tipo_documento': self.tipo_ce.id,
            'id_cargo': self.cargo_analista.id,
            'id_dependencia': self.dependencia_rrhh.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)  # Redirección tras actualizar
        self.user.refresh_from_db()
        self.assertEqual(self.user.nombres, 'Test')
        self.assertEqual(self.user.apellidos, 'User')
        self.assertEqual(self.user.correo, 'testuser@example.com')



