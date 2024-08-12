from django.utils import timezone
from django.test import TestCase
from django.core.paginator import Page
from django.urls import reverse
from django.core import mail
from apps.funcionarios.models import Persona, Visita, Asistente, TipoDocumento


class AdministradorVisitasTests(TestCase):
    def setUp(self):
        # Crear un usuario de prueba
        self.user = Persona.objects.create(
            nombres='Juan',
            apellidos='Pérez',
            telefono='123456789',
            correo='juan@example.com',
            identificacion='1234567890'  
        )
        self.user.set_password('testpass')
        self.user.save()

        self.client.login(correo='juan@example.com', password='testpass')

        # Crear varias visitas de prueba
        for i in range(3):
            Visita.objects.create(
                id_persona=self.user, 
                fecha_inicio=timezone.now() - timezone.timedelta(days=i + 1),
                fecha_finalizacion=timezone.now() - timezone.timedelta(days=i),
                discapacidad='Ninguna',
                procedencia='Local',
                grabacion=False,
                estado_finalizado=False,
                estado_revision=False,
                estado_rechazado=False
            )

    def test_listar_visitas(self):
        """Prueba para listar visitas con información de la persona."""
        url = reverse('visitas:administrador_visitas')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Juan')  

    def test_buscar_visita(self):
        """Prueba para buscar visitas."""
        url = reverse('visitas:buscar_visita')
        response = self.client.get(url, {'buscar': 'Juan'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Juan')  

    def test_paginacion(self):
        """Prueba la paginación de visitas."""
        url = reverse('visitas:administrador_visitas')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('resultados', response.context)

        # Verificar si la página actual es una instancia de Page
        self.assertIsInstance(response.context['resultados'], Page)

        # Verificar si hay una página siguiente
        self.assertFalse(response.context['resultados'].has_next())

    def test_rechazar_visita(self):
        """Prueba para rechazar una visita y enviar correo."""
        visita = Visita.objects.first()  # Obtener la primera visita creada
        url = reverse('visitas:rechazar_visita', args=[visita.id])

        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        visita.refresh_from_db()  # Refrescar desde la base de datos
        self.assertTrue(visita.estado_rechazado)

        # Verificar que se envió un correo
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Estado de solicitud de reserva', mail.outbox[0].subject)

    def test_aprobar_visita(self):
        """Prueba para aprobar una visita y enviar correo."""
        visita = Visita.objects.first()  # Obtener la primera visita creada
        url = reverse('visitas:aprobar_visita', args=[visita.id])

        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        visita.refresh_from_db()  # Refrescar desde la base de datos
        self.assertTrue(visita.estado_revision)

        # Verificar que se envió un correo
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Estado de solicitud de reserva', mail.outbox[0].subject)


    
