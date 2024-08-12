from django.utils import timezone
from django.test import TestCase
from django.urls import reverse
import json
from django.contrib.auth.models import User
from django.core import mail
from django.contrib.messages import get_messages
from apps.funcionarios.models import Persona, Visita, Asistente, TipoDocumento
from apps.visitas.views import actualizar_estado_visitas

class HomeVisitaTests(TestCase):
    def setUp(self):
    # Crear el usuario de prueba
        self.user = Persona.objects.create(
            nombres='Juan',
            apellidos='Pérez',
            telefono='123456789',
            correo='juan@example.com'
        )
        

        self.user.set_password('testpass')
        self.user.save()
    

        self.client.login(correo='juan@example.com', password='testpass')
    
        # Crear un asistente de prueba
        self.asistente = Asistente.objects.create(
            nombre_asistente='Ana',
            apellidos_asistente='López',
            telefono_asistente='987654321',
            correo_asistente='ana@example.com',
            id_tipo_documento_asistente=TipoDocumento.objects.create(nombre='Cédula'),
            identificacion_asistente='12345'
        )
    
        # Crear una visita de prueba
        self.visita = Visita.objects.create(
            id_persona=self.user, 
            fecha_inicio=timezone.now() - timezone.timedelta(days=2),
            fecha_finalizacion=timezone.now() - timezone.timedelta(days=1),
            discapacidad='Ninguna',
            procedencia='Local',
            grabacion=False,
            estado_finalizado=False
        )


    def test_registro_visita(self):
        """
        Prueba para registrar una visita.
        """
        self.client.login(username='juan@example.com', password='testpass')  
        url = reverse('visitas:home_visita')
        data = {
            'nombres': 'Juan',
            'apellidos': 'Pérez',
            'telefono': '123456789',
            'correo': 'juan@example.com',
            'grabacion': 'True',
            'asistentes': json.dumps([
                {
                    'identificacion': '12345',
                    'nombres': 'Ana',
                    'apellidos': 'López',
                    'telefono': '987654321',
                    'correo': 'ana@example.com',
                    'idTipoDocumento': 1,
                    'discapacidad_a': 'Ninguna',
                    'procedencia_a': 'Local',
                    'genero_a': 1
                }
            ])
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        

        # Verificar que la visita y el asistente se hayan creado
        self.assertTrue(Visita.objects.filter(id_persona=self.user).exists())
        self.assertTrue(Asistente.objects.filter(identificacion_asistente='12345').exists())

    def test_formulario_invalido(self):
        """
        Prueba que un formulario inválido no cree una visita.
        """
        self.client.login(username='juan@example.com', password='testpass') 
        url = reverse('visitas:home_visita')
        data = {}  # vacio
        
        response = self.client.post(url, data)
        
        
        self.assertEqual(response.status_code, 200)

        # Verificar que se muestre un mensaje de error
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Formulario inválido. Por favor revise los datos ingresados.')

class DescargarExcelTests(TestCase):
    def test_descargar_excel(self):
        """
        Prueba para descargar el archivo Excel de registro de asistentes.
        """
        url = reverse('visitas:descargar_excel')
        response = self.client.get(url)
        
        # Verificar que el estado de respuesta sea 200
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="Registro Asistentes.xlsx"')

class ActualizarEstadoVisitasTests(TestCase):
    def setUp(self):
        # Crear una persona de prueba
        self.persona = Persona.objects.create(
            nombres='Juan',
            apellidos='Pérez',
            telefono='123456789',
            correo='juan@example.com'
        )
        
        # Crear una visita 
        self.visita = Visita.objects.create(
            id_persona=self.persona,
            fecha_inicio=timezone.now() - timezone.timedelta(days=2),
            fecha_finalizacion=timezone.now() - timezone.timedelta(days=1),
            discapacidad='Ninguna',
            procedencia='Local',
            grabacion=False,
            estado_finalizado=False
        )

    def test_actualizar_estado_visitas(self):
        """
        Prueba para actualizar el estado de las visitas.
        """
        # Llama la función 
        actualizar_estado_visitas()

        
        self.visita.refresh_from_db()
        self.assertTrue(self.visita.estado_finalizado)

class VerificarFechaTests(TestCase):
    def test_verificar_fecha_reservada(self):
        """
        Prueba para verificar si una fecha está reservada.
        """
        fecha = timezone.now() + timezone.timedelta(days=1)
        Visita.objects.create(
            fecha_inicio=fecha,
            fecha_finalizacion=fecha + timezone.timedelta(hours=1),
            estado_finalizado=False
        )

        url = reverse('visitas:verificar_fecha')
        response = self.client.get(url, {'fecha': fecha.isoformat()})

        # Verificar que la respuesta sea 200 y la fecha esté reservada
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'reservada': True})

    def test_verificar_fecha_no_reservada(self):
        """
        Prueba para verificar si una fecha no está reservada.
        """
        fecha = timezone.now() + timezone.timedelta(days=1)
        
        url = reverse('visitas:verificar_fecha')
        response = self.client.get(url, {'fecha': fecha.isoformat()})

        # Verificar que la respuesta sea 200 y la fecha no esté reservada
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'reservada': False})
