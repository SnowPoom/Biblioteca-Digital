from django.test import SimpleTestCase
from django.urls import reverse


class MaterialesViewsTests(SimpleTestCase):
    def test_vista_previa_material_disponible(self):
        response = self.client.get(reverse('materiales:vista_previa_material'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Vista previa del material')

    def test_lectura_material_disponible(self):
        response = self.client.get(reverse('materiales:lectura_material'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lectura del material')

    def test_creacion_material_disponible(self):
        response = self.client.get(reverse('materiales:creacion_material'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Creación del material')
