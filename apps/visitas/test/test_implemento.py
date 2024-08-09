from django.test import TestCase
from django.urls import reverse
from django.core.paginator import Page
from apps.funcionarios.models import Implemento

class GestionImplementoTests(TestCase):
    def setUp(self):
        """
        Configura el entorno de prueba creando objetos de Implemento.
        """
        # Crear 12 implementos de prueba
        for i in range(1, 13):
            Implemento.objects.create(
                nombre=f'Implemento {i}',
                estado=i % 2 == 0  # Habilitado si i es par, inhabilitado si es impar
            )

    def test_listar_implementos(self):
        """
        Prueba para listar los implementos.
        """
        url = reverse('reservas:gestion_implemento')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('resultados', response.context)

    def test_habilitar_deshabilitar_implemento(self):
        """
        Prueba para cambiar el estado de un implemento (habilitar/deshabilitar).
        """
        implemento = Implemento.objects.get(nombre='Implemento 1')
        self.assertFalse(implemento.estado)

        implemento.estado = True
        implemento.save()
        self.assertTrue(implemento.estado)

        implemento.estado = False
        implemento.save()
        self.assertFalse(implemento.estado)

    def test_paginacion_implementos(self):
        """
        Prueba para la paginación de implementos.
        """
        url = reverse('reservas:gestion_implemento')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('resultados', response.context)

        # Verificar si la página actual es una instancia de Page
        self.assertIsInstance(response.context['resultados'], Page)

        # Verificar si hay una página siguiente
        self.assertTrue(response.context['resultados'].has_next())

    def test_buscar_implemento(self):
        """
        Prueba para buscar un implemento por nombre.
        """
        url = reverse('reservas:buscar_implemento')
        response = self.client.get(url, {'buscar': 'Implemento 1'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('resultados', response.context)
        resultados = response.context['resultados']
        # Verificar que solo hay un resultado con nombre 'Implemento 1'
        self.assertEqual(len(resultados), 4)
        self.assertEqual(resultados[0].nombre, 'Implemento 1')

    def test_filtrar_implementos_habilitados(self):
        """
        Prueba para filtrar implementos habilitados.
        """
        url = reverse('reservas:buscar_implemento')
        response = self.client.get(url, {'estado': 'habilitados'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('resultados', response.context)
        for implemento in response.context['resultados']:
            self.assertTrue(implemento.estado)

    def test_filtrar_implementos_inhabilitados(self):
        """
        Prueba para filtrar implementos inhabilitados.
        """
        url = reverse('reservas:buscar_implemento')
        response = self.client.get(url, {'estado': 'inhabilitados'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('resultados', response.context)
        for implemento in response.context['resultados']:
            self.assertFalse(implemento.estado)

    def test_eliminar_implemento(self):
        """
        Prueba para eliminar un implemento.
        """
        implemento = Implemento.objects.get(nombre='Implemento 1')
        implemento_id = implemento.id
        url = reverse('reservas:eliminar_implemento', args=[implemento_id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Redirección tras eliminar

        with self.assertRaises(Implemento.DoesNotExist):
            Implemento.objects.get(id=implemento_id)
