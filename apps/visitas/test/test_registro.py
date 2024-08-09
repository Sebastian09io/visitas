from django.test import TestCase
from django.urls import reverse
from django.core.paginator import Page
from apps.funcionarios.models import Espacio

class GestionEspacioTests(TestCase):
    def setUp(self):
        """
        Configura el entorno de prueba creando objetos de Espacio.
        """
        # Crear 12 espacios de prueba
        for i in range(1, 13):
            Espacio.objects.create(
                nombre=f'Espacio {i}',
                estado=i % 2 == 0  # Habilitado si i es par, inhabilitado si es impar
            )

    def test_listar_espacios(self):
        """
        Prueba para listar los espacios.
        """
        url = reverse('reservas:gestion_espacio')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('resultados', response.context)

    def test_habilitar_deshabilitar_espacio(self):
        """
        Prueba para cambiar el estado de un espacio (habilitar/deshabilitar).
        """
        espacio = Espacio.objects.get(nombre='Espacio 1')
        self.assertFalse(espacio.estado)

        espacio.estado = True
        espacio.save()
        self.assertTrue(espacio.estado)

        espacio.estado = False
        espacio.save()
        self.assertFalse(espacio.estado)

    def test_paginacion_espacios(self):
        """
        Prueba para la paginación de espacios.
        """
        url = reverse('reservas:gestion_espacio')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('resultados', response.context)

        # Verificar si la página actual es una instancia de Page
        self.assertIsInstance(response.context['resultados'], Page)

        # Verificar si hay una página siguiente
        self.assertTrue(response.context['resultados'].has_next())

    def test_buscar_espacio(self):
        """
        Prueba para buscar un espacio por nombre.
        """
        url = reverse('reservas:buscar_espacio')
        response = self.client.get(url, {'buscar': 'Espacio 1'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('resultados', response.context)
        resultados = response.context['resultados']
        # Verificar que solo hay un resultado con nombre 'Espacio 1'
        self.assertEqual(len(resultados), 4)
        self.assertEqual(resultados[0].nombre, 'Espacio 1')

    def test_filtrar_espacios_habilitados(self):
        """
        Prueba para filtrar espacios habilitados.
        """
        url = reverse('reservas:buscar_espacio')
        response = self.client.get(url, {'estado': 'habilitados'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('resultados', response.context)
        for espacio in response.context['resultados']:
            self.assertTrue(espacio.estado)

    def test_filtrar_espacios_inhabilitados(self):
        """
        Prueba para filtrar espacios inhabilitados.
        """
        url = reverse('reservas:buscar_espacio')
        response = self.client.get(url, {'estado': 'inhabilitados'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('resultados', response.context)
        for espacio in response.context['resultados']:
            self.assertFalse(espacio.estado)

    def test_eliminar_espacio(self):
        """
        Prueba para eliminar un espacio.
        """
        espacio = Espacio.objects.get(nombre='Espacio 1')
        espacio_id = espacio.id
        url = reverse('reservas:eliminar_espacio', args=[espacio_id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Redirección tras eliminar

        with self.assertRaises(Espacio.DoesNotExist):
            Espacio.objects.get(id=espacio_id)
