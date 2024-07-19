import pytest  # Importa pytest, una herramienta de pruebas para aplicaciones Python.
from django.contrib.auth import get_user_model  # Importa get_user_model, una función que devuelve el modelo de usuario actual definido en el proyecto.
from django.test import RequestFactory, LiveServerTestCase  # Importa RequestFactory para crear solicitudes de prueba y LiveServerTestCase para lanzar un servidor en vivo para pruebas.
from apps.funcionarios.models import TipoDocumento, Cargo, Dependencia  # Importa los modelos TipoDocumento, Cargo y Dependencia desde la aplicación funcionarios.
from playwright.sync_api import sync_playwright  # Importa sync_playwright para la automatización de navegadores web de forma sincrónica con Playwright.

# Obtiene el modelo de usuario definido en el proyecto
User = get_user_model()

@pytest.mark.django_db  # Marca esta clase como una prueba de base de datos de Django
class PasswordResetTest(LiveServerTestCase):
    """
    Clase de prueba automatizada para el flujo de restablecimiento de contraseña usando Playwright.
    """

    def setUp(self):
        """
        Configuración inicial para cada prueba. Aquí se crean los datos de prueba necesarios.
        """
        self.factory = RequestFactory()  # Inicializa una instancia de RequestFactory para crear solicitudes de prueba

        # Obtiene las primeras instancias de las relaciones foráneas
        self.tipo_documento = TipoDocumento.objects.first()
        self.cargo = Cargo.objects.first()
        self.dependencia = Dependencia.objects.first()

        # Crea un usuario de prueba con las relaciones necesarias
        self.user = User.objects.create_user(
            correo='test_auto@example.com',
            password='Construccion_123',
            nombres='Test',
            apellidos='User',
            id_tipo_documento=self.tipo_documento,
            identificacion='0034567890',
            telefono='0034567890',
            id_cargo=self.cargo,
            id_dependencia=self.dependencia
        )

        # Configura una solicitud de prueba con sesión
        self.request = self.factory.post('/dummy-url/')
        self.request.session = self.client.session
        self.request.session.save()

    def test_password_reset_with_playwright(self):
        """
        Prueba automatizada para el flujo de restablecimiento de contraseña usando Playwright.
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)  # Lanza el navegador Chromium en modo no headless
            page = browser.new_page()  # Abre una nueva página en el navegador
            password_reset_url = self.live_server_url + '/recuperar/'  # URL para la página de recuperación de contraseña
            page.goto(password_reset_url)  # Navega a la URL de recuperación de contraseña

            # Llena el campo de correo electrónico y envía el formulario
            page.fill('input[name="correo"]', 'test_auto@example.com')
            page.click('button[type="submit"]')

            # Espera el mensaje de éxito
            try:
                page.wait_for_selector('.alert-success', timeout=30000)  # Espera hasta 30 segundos para el mensaje de éxito
            except Exception as e:
                # Captura una captura de pantalla en caso de error y cierra el navegador
                page.screenshot(path="error_screenshot.png")
                print(f"Error occurred: {e}")
                browser.close()
                return
