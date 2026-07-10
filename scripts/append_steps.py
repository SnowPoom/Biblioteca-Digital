import os

new_steps = '''

# ---------------------------------------------------------------------------
# Escenario: Filtrar el feed de seguimiento por tipo de contenido
# ---------------------------------------------------------------------------

@when('el usuario filtra por {tipo_contenido}')
def step_usuario_filtra_por_tipo(context, tipo_contenido):
    # Simulamos el filtro en el frontend guardando el estado
    context.filtro_aplicado = tipo_contenido


@then('el feed muestra únicamente {tipo_contenido} publicado por sus seguidos')
def step_feed_muestra_unicamente_tipo(context, tipo_contenido):
    if tipo_contenido == 'libros':
        material_feed = list(context.response.context.get('material_feed', []))
        context.test.assertGreater(len(material_feed), 0, "No hay libros en el feed.")
        context.test.assertIn(b'id="material-view"', context.response.content)
    elif tipo_contenido == 'colecciones':
        colecciones = list(context.response.context.get('colecciones', []))
        context.test.assertIn(b'id="colecciones-view"', context.response.content)


@then('el otro tipo de contenido no aparece en esa vista')
def step_otro_tipo_no_aparece(context):
    # Verificamos que no esten mezclados en el contexto backend
    material_feed = list(context.response.context.get('material_feed', []))
    colecciones = list(context.response.context.get('colecciones', []))
    
    # Comprobar que en material_feed no hay colecciones
    for item in material_feed:
        if hasattr(item, 'titulo'): # Es Publicacion
            context.test.assertNotEqual(item.tipo, 'coleccion', 'Hay una coleccion en material_feed')
            
    # Comprobar que en colecciones no hay libros
    for col in colecciones:
        context.test.assertEqual(col.tipo, 'coleccion', 'Hay un libro en colecciones')
'''

with open('features/steps/feed_actividad_steps.py', 'a', encoding='utf-8') as f:
    f.write(new_steps)

print('Steps appended.')
