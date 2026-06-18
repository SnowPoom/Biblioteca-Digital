from behave import given, then

@given('que un usuario visita la página principal')
def paso_visitar_inicio(context):
    # Simulamos que un navegador entra a la URL raíz '/'
    context.response = context.test.client.get('/')

@then('la página debe mostrar el texto "{texto_esperado}"')
def paso_verificar_texto(context, texto_esperado):
    # Verificamos que la página responda y tenga el texto
    context.test.assertContains(context.response, texto_esperado)