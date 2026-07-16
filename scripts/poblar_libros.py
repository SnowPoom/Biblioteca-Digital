"""
Script para poblar la base de datos con libros de prueba para testear
el motor de recomendaciones.

Ejecutar con:
    python manage.py shell < scripts/poblar_libros.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from src.login.models import PerfilUsuario
from src.materiales.models import Libro, Categoria
from src.feed.models import Publicacion, Categoria as FeedCategoria
from src.recomendaciones.models import HistorialLectura

User = get_user_model()

# ---------------------------------------------------------------
# Categorias
# ---------------------------------------------------------------
nombres_categorias = [
    'Matematicas', 'Fisica', 'Quimica', 'Biologia',
    'Historia', 'Filosofia', 'Literatura', 'Programacion',
    'Ingenieria', 'Economia',
]

categorias = {}
for nombre in nombres_categorias:
    cat, _ = Categoria.objects.get_or_create(nombre=nombre)
    categorias[nombre] = cat

feed_categorias = {}
for nombre in nombres_categorias:
    fcat, _ = FeedCategoria.objects.get_or_create(nombre=nombre)
    feed_categorias[nombre] = fcat

# ---------------------------------------------------------------
# Autores
# ---------------------------------------------------------------
autores_data = [
    ('prof_garcia', 'garcia@ejemplo.com', 'Maria Garcia', PerfilUsuario.PROFESOR),
    ('prof_lopez', 'lopez@ejemplo.com', 'Carlos Lopez', PerfilUsuario.PROFESOR),
    ('est_martinez', 'martinez@ejemplo.com', 'Ana Martinez', PerfilUsuario.ESTUDIANTE),
    ('est_rodriguez', 'rodriguez@ejemplo.com', 'Luis Rodriguez', PerfilUsuario.ESTUDIANTE),
    ('prof_herrera', 'herrera@ejemplo.com', 'Sofia Herrera', PerfilUsuario.PROFESOR),
]

autores = []
for username, email, nombre, rol in autores_data:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'first_name': nombre,
        }
    )
    if created:
        user.set_password('password123')
        user.save()
        PerfilUsuario.objects.get_or_create(usuario=user, defaults={'rol': rol})
    autores.append(user)

# ---------------------------------------------------------------
# Libros (20 libros variados)
# ---------------------------------------------------------------
libros_data = [
    # (titulo, autor_idx, categorias, paginas, vistas, descargas, repubs)
    ('Calculo Diferencial Aplicado', 0, ['Matematicas'], 320, 450, 180, 45),
    ('Algebra Lineal para Ingenieros', 0, ['Matematicas', 'Ingenieria'], 280, 380, 150, 30),
    ('Mecanica Cuantica Introductoria', 1, ['Fisica'], 400, 520, 210, 60),
    ('Termodinamica y sus Aplicaciones', 1, ['Fisica', 'Quimica'], 350, 290, 120, 25),
    ('Quimica Organica Fundamental', 2, ['Quimica'], 420, 610, 300, 70),
    ('Biologia Molecular Moderna', 2, ['Biologia'], 380, 340, 140, 35),
    ('Genetica y Evolucion', 3, ['Biologia'], 300, 200, 80, 15),
    ('Historia de las Civilizaciones', 3, ['Historia'], 450, 700, 350, 90),
    ('La Revolucion Industrial', 4, ['Historia', 'Economia'], 250, 420, 170, 40),
    ('Introduccion a la Filosofia', 4, ['Filosofia'], 200, 550, 230, 55),
    ('Etica y Moral Contemporanea', 0, ['Filosofia'], 180, 310, 130, 28),
    ('Narrativa Latinoamericana', 1, ['Literatura'], 350, 480, 200, 50),
    ('Poesia del Siglo XX', 2, ['Literatura'], 150, 190, 70, 12),
    ('Python para Ciencia de Datos', 3, ['Programacion'], 400, 900, 450, 120),
    ('Estructuras de Datos en Java', 4, ['Programacion', 'Matematicas'], 380, 750, 380, 95),
    ('Diseno de Sistemas Distribuidos', 0, ['Programacion', 'Ingenieria'], 420, 650, 280, 75),
    ('Resistencia de Materiales', 1, ['Ingenieria', 'Fisica'], 360, 410, 160, 38),
    ('Microeconomia Avanzada', 2, ['Economia', 'Matematicas'], 300, 330, 140, 32),
    ('Macroeconomia Global', 3, ['Economia', 'Historia'], 280, 270, 110, 22),
    ('Inteligencia Artificial Practica', 4, ['Programacion', 'Matematicas'], 450, 850, 420, 110),
]

libros_creados = []
for titulo, autor_idx, cats, paginas, vistas, descargas, repubs in libros_data:
    autor = autores[autor_idx]

    libro, created = Libro.objects.get_or_create(
        titulo=titulo,
        autor=autor,
        defaults={
            'estado': Libro.PUBLICADO,
            'contenido_texto': f'Contenido completo del libro "{titulo}". '
                               f'Este material cubre los temas fundamentales '
                               f'de {", ".join(cats)} con ejercicios practicos.',
            'numero_paginas': paginas,
            'visualizaciones': vistas,
            'descargas': descargas,
            'republicaciones': repubs,
        }
    )

    if created:
        for cat_nombre in cats:
            libro.categorias.add(categorias[cat_nombre])

        # Crear Publicacion espejo en el feed
        pub, _ = Publicacion.objects.get_or_create(
            pk=libro.pk,
            defaults={
                'autor': autor,
                'titulo': titulo,
                'tipo': Publicacion.LIBRO,
            }
        )
        for cat_nombre in cats:
            pub.categorias.add(feed_categorias[cat_nombre])

    libros_creados.append(libro)

print(f'Se crearon/verificaron {len(libros_creados)} libros.')

# ---------------------------------------------------------------
# Historial de lectura para el usuario de prueba
# (para que el motor tenga datos con los que recomendar)
# ---------------------------------------------------------------
usuario_prueba, created = User.objects.get_or_create(
    username='usuario_prueba',
    defaults={
        'email': 'prueba@ejemplo.com',
        'first_name': 'Usuario de Prueba',
    }
)
if created:
    usuario_prueba.set_password('password123')
    usuario_prueba.save()
    PerfilUsuario.objects.get_or_create(
        usuario=usuario_prueba,
        defaults={'rol': PerfilUsuario.ESTUDIANTE}
    )

# Simular que el usuario leyo 4 libros (Programacion y Matematicas)
libros_leidos_titulos = [
    'Python para Ciencia de Datos',
    'Estructuras de Datos en Java',
    'Calculo Diferencial Aplicado',
    'Algebra Lineal para Ingenieros',
]

for titulo in libros_leidos_titulos:
    libro = Libro.objects.filter(titulo=titulo).first()
    if libro:
        pub = Publicacion.objects.filter(pk=libro.pk).first()
        if pub:
            HistorialLectura.objects.get_or_create(
                usuario=usuario_prueba,
                publicacion=pub,
            )

print(f'Historial de lectura creado para "{usuario_prueba.username}".')
print(f'Credenciales: usuario_prueba / password123')
print('Poblamiento completado.')
