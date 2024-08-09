from django.test import TestCase
from django.urls import reverse
from apps.funcionarios.models import TipoDocumento, Cargo, Dependencia, Persona

from django.core.paginator import Page

class GestionFuncionarioTests(TestCase):
    def setUp(self):
        """
        crea un numero de usuario para hacer la prueba .
        """
        # Crear tipos de documentos de prueba
        tipo_cc = TipoDocumento.objects.create(nombre='CC')
        tipo_ce = TipoDocumento.objects.create(nombre='CE')

        # Crear cargos de prueba
        cargo_gerente = Cargo.objects.create(nombre='Gerente')
        cargo_analista = Cargo.objects.create(nombre='Analista')

        # Crear dependencias de prueba
        dependencia_it = Dependencia.objects.create(nombre='IT')
        dependencia_rrhh = Dependencia.objects.create(nombre='RRHH')

        # Crear 12 usuarios de prueba
        for i in range(1, 13):
            Persona.objects.create(
                nombres=f'Usuario {i}',
                apellidos=f'Apellido {i}',
                id_tipo_documento=tipo_cc if i % 2 == 0 else tipo_ce,
                identificacion=str(i),
                telefono='1234567890',
                correo=f'usuario{i}@example.com',
                id_cargo=cargo_gerente if i % 3 == 0 else cargo_analista,
                id_dependencia=dependencia_it if i % 4 == 0 else dependencia_rrhh,
                is_active=True,
                estado=True if i % 2 == 0 else False
            )
#paginador queda pendiente por que el test pide  organizar paginacion por orden de id
    def test_paginacion_personas(self):
        """
        prueba para la paginacion .
        """
        url = reverse('reservas:gestion_funcionario')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('resultados', response.context)
    
        # Verificar si la página actual es una instancia de Page
        self.assertIsInstance(response.context['resultados'], Page)
    
        # Verificar si hay una página siguiente
        self.assertTrue(response.context['resultados'].has_next())

    def test_habilitar_deshabilitar_persona(self):
        """
        prueba para el cambio de estados .
        """
        persona = Persona.objects.get(correo='usuario1@example.com')
        self.assertTrue(persona.is_active)

        persona.is_active = False
        persona.save()
        self.assertFalse(persona.is_active)
        
        persona.is_active = True
        persona.save()
        self.assertTrue(persona.is_active)
        
    def test_buscar_funcionario_identificacion(self):
        """
        prueba para listar o buscar un usuario mediante la identificacion, se busca mediante el numero 1.
        """
        url = reverse('reservas:buscar_funcionario')
        response = self.client.get(url, {'buscar': '1'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('resultados', response.context)
        resultados = response.context['resultados']
        # Verificar que solo hay un resultado con identificación '1'
        self.assertEqual(len(resultados), 4)
        self.assertEqual(resultados[0].identificacion, '1')
        
    def test_filtrar_funcionarios_habilitados(self):
        """
        prueba para ver que liste los usuarios habilitados mediante el filtro desplegable .
        """
        url = reverse('reservas:buscar_funcionario')
        response = self.client.get(url, {'estado': 'habilitados'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('resultados', response.context)
        for persona in response.context['resultados']:
            self.assertTrue(persona.estado)

    def test_filtrar_funcionarios_inhabilitados(self):
        """
        prueba para ver que liste los usuarios inhabilitados mediante el filtro desplegable .
        """
        url = reverse('reservas:buscar_funcionario')
        response = self.client.get(url, {'estado': 'inhabilitados'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('resultados', response.context)
        for persona in response.context['resultados']:
            self.assertFalse(persona.estado)

    def test_buscar_funcionario_y_filtrar(self):
        """
        prueba de el filtro buscar, testea usuarios por identificacion 2 y que esten habilitados .
        """
        url = reverse('reservas:buscar_funcionario')
        response = self.client.get(url, {'buscar': '2', 'estado': 'habilitados'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('resultados', response.context)
        resultados = response.context['resultados']
        # Verificar que solo hay un resultado con identificación '2' y estado habilitado
        self.assertEqual(len(resultados), 2)
        self.assertEqual(resultados[0].identificacion, '2')
        self.assertTrue(resultados[0].estado)