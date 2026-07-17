from behave import given, when, then
from django.contrib.auth import get_user_model
from django.urls import reverse
from src.login.models import PerfilUsuario
from src.materiales.models import Categoria, Libro, Coleccion

User = get_user_model()


@given('que existen materiales publicados en la plataforma')
def step_existen_materiales_publicados(context):
    autor = User.objects.create_user(
        username='autor_busqueda',
        email='autor_busqueda@ejemplo.com',
        password='password123',
        first_name='Autor Busqueda',
    )
    PerfilUsuario.objects.create(usuario=autor, rol=PerfilUsuario.ESTUDIANTE)

    categoria = Categoria.objects.create(nombre='Matematicas')

    libro = Libro.objects.create(
        titulo='Algebra Lineal Avanzada',
        contenido_texto='Contenido de algebra lineal para pruebas de busqueda.',
        numero_paginas=50,
        autor=autor,
        estado=Libro.PUBLICADO,
    )
    libro.categorias.add(categoria)

    context.libro_busqueda = libro
    context.autor_busqueda = autor
    context.categoria_busqueda = categoria


@when('el usuario realiza una busqueda por el nombre de un material')
def step_busqueda_por_nombre_material(context):
    url = reverse('busqueda:busqueda')
    context.response = context.test.client.get(url, {'q': 'Algebra'})


@then('el sistema muestra los materiales cuyo titulo coincide con el termino buscado')
def step_muestra_materiales_coincidentes(context):
    context.test.assertEqual(context.response.status_code, 200)
    context.test.assertContains(context.response, 'Algebra Lineal Avanzada')


@given('que existen colecciones publicadas en la plataforma')
def step_existen_colecciones_publicadas(context):
    creador = User.objects.create_user(
        username='creador_col_busqueda',
        email='creador_col_busqueda@ejemplo.com',
        password='password123',
        first_name='Creador Coleccion',
    )
    PerfilUsuario.objects.create(usuario=creador, rol=PerfilUsuario.PROFESOR)

    categoria = Categoria.objects.create(nombre='Fisica')

    coleccion = Coleccion.objects.create(
        nombre='Recursos de Mecanica Clasica',
        descripcion='Coleccion de libros sobre mecanica.',
        visibilidad=Coleccion.PUBLICA,
        creador=creador,
    )
    coleccion.categorias.add(categoria)

    context.coleccion_busqueda = coleccion


@when('el usuario realiza una busqueda por el nombre de una coleccion')
def step_busqueda_por_nombre_coleccion(context):
    url = reverse('busqueda:busqueda')
    context.response = context.test.client.get(url, {'q': 'Mecanica'})


@then('el sistema muestra las colecciones cuyo nombre coincide con el termino buscado')
def step_muestra_colecciones_coincidentes(context):
    context.test.assertEqual(context.response.status_code, 200)
    context.test.assertContains(context.response, 'Recursos de Mecanica Clasica')


@given('que existen materiales y colecciones asociados a categorias')
def step_existen_recursos_con_categorias(context):
    autor = User.objects.create_user(
        username='autor_cat_busqueda',
        email='autor_cat_busqueda@ejemplo.com',
        password='password123',
        first_name='Autor Categoria',
    )
    PerfilUsuario.objects.create(usuario=autor, rol=PerfilUsuario.ESTUDIANTE)

    categoria = Categoria.objects.create(nombre='Programacion')

    libro = Libro.objects.create(
        titulo='Introduccion a Python',
        contenido_texto='Contenido sobre programacion en Python.',
        numero_paginas=80,
        autor=autor,
        estado=Libro.PUBLICADO,
    )
    libro.categorias.add(categoria)

    coleccion = Coleccion.objects.create(
        nombre='Guias de Desarrollo',
        descripcion='Material de programacion.',
        visibilidad=Coleccion.PUBLICA,
        creador=autor,
    )
    coleccion.categorias.add(categoria)

    context.categoria_programacion = categoria


@when('el usuario realiza una busqueda por el nombre de una categoria')
def step_busqueda_por_categoria(context):
    url = reverse('busqueda:busqueda')
    context.response = context.test.client.get(url, {'q': 'Programacion'})


@then('el sistema muestra los materiales y colecciones que pertenecen a esa categoria')
def step_muestra_recursos_de_categoria(context):
    context.test.assertEqual(context.response.status_code, 200)
    context.test.assertContains(context.response, 'Introduccion a Python')
    context.test.assertContains(context.response, 'Guias de Desarrollo')


@given('que existen materiales publicados por estudiantes y por profesores')
def step_existen_materiales_por_roles(context):
    estudiante = User.objects.create_user(
        username='estudiante_busqueda',
        email='estudiante_busqueda@ejemplo.com',
        password='password123',
        first_name='Estudiante Busqueda',
    )
    PerfilUsuario.objects.create(usuario=estudiante, rol=PerfilUsuario.ESTUDIANTE)

    profesor = User.objects.create_user(
        username='profesor_busqueda',
        email='profesor_busqueda@ejemplo.com',
        password='password123',
        first_name='Profesor Busqueda',
    )
    PerfilUsuario.objects.create(usuario=profesor, rol=PerfilUsuario.PROFESOR)

    Libro.objects.create(
        titulo='Libro del Estudiante',
        contenido_texto='Contenido del estudiante.',
        numero_paginas=30,
        autor=estudiante,
        estado=Libro.PUBLICADO,
    )
    Libro.objects.create(
        titulo='Libro del Profesor',
        contenido_texto='Contenido del profesor.',
        numero_paginas=40,
        autor=profesor,
        estado=Libro.PUBLICADO,
    )


@when('el usuario filtra la busqueda por rol de autor')
def step_filtro_por_rol(context):
    url = reverse('busqueda:busqueda')
    context.response = context.test.client.get(url, {'q': 'Libro', 'rol': 'profesor'})


@then('el sistema muestra unicamente los materiales publicados por usuarios con ese rol')
def step_muestra_solo_materiales_del_rol(context):
    context.test.assertEqual(context.response.status_code, 200)
    context.test.assertContains(context.response, 'Libro del Profesor')
    context.test.assertNotContains(context.response, 'Libro del Estudiante')


@when('el usuario realiza una busqueda con un termino que no coincide con ningun recurso')
def step_busqueda_sin_coincidencias(context):
    url = reverse('busqueda:busqueda')
    context.response = context.test.client.get(url, {'q': 'TerminoInexistente12345'})


@then('el sistema informa que no se encontraron resultados')
def step_informa_sin_resultados(context):
    context.test.assertEqual(context.response.status_code, 200)
    context.test.assertContains(context.response, 'No se encontraron resultados')
