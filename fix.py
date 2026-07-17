import sys
import os

try:
    with open('features/steps/publicacion_material_steps.py', 'rb') as f:
        data = f.read()

    idx = data.find(b'\x00')
    if idx != -1:
        # Since it's UTF-16, a null byte will appear in the first character of the appended string
        # Let's just find the last valid \n before the null byte
        valid_data = data[:idx]
        text = valid_data.decode('utf-8', errors='ignore')
        
        # let's just make sure we cut off any partial lines at the end
        last_newline = text.rfind('\n')
        if last_newline != -1:
            text = text[:last_newline+1]
    else:
        text = data.decode('utf-8', errors='ignore')
        
    # Append the new steps
    text += """
@given('que el usuario tiene una colección que contiene un libro')
def step_coleccion_contiene_libro(context):
    from src.materiales.models import Coleccion, Libro
    context.coleccion_eliminar = Coleccion.objects.create(
        nombre='Coleccion para eliminar libro',
        creador=context.usuario_principal
    )
    context.libro_a_eliminar = Libro.objects.create(
        titulo='Libro a Eliminar',
        autor=context.usuario_principal,
        estado=Libro.PUBLICADO
    )
    context.coleccion_eliminar.libros.add(context.libro_a_eliminar)

@when('el usuario elimina ese libro de la colección')
def step_elimina_libro_de_coleccion(context):
    try:
        context.coleccion_eliminar.eliminar_libro(context.usuario_principal, context.libro_a_eliminar)
        context.resultado = True
    except Exception as e:
        context.resultado = False
        context.error = e

@then('el libro desaparece de la colección')
def step_libro_desaparece_coleccion(context):
    context.test.assertNotIn(
        context.libro_a_eliminar,
        context.coleccion_eliminar.libros.all(),
        'El libro no debería estar en la colección'
    )

@then('el libro sigue disponible para cualquier usuario en la biblioteca general')
def step_libro_sigue_disponible(context):
    from src.materiales.models import Libro
    libro_en_bd = Libro.objects.filter(id=context.libro_a_eliminar.id).exists()
    context.test.assertTrue(
        libro_en_bd,
        'El libro debe seguir existiendo en la base de datos general'
    )
    context.libro_a_eliminar.refresh_from_db()
    context.test.assertEqual(
        context.libro_a_eliminar.estado,
        Libro.PUBLICADO,
        'El libro debe seguir publicado'
    )
"""

    with open('features/steps/publicacion_material_steps.py', 'wb') as f:
        f.write(text.encode('utf-8'))
    
    print('Fixed encoding and appended steps')

except Exception as e:
    print('Error:', e)
