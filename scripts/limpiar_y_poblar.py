"""
Script para limpiar la base de datos (excepto usuarios) y poblar con datos de prueba coherentes y actualizados.
Ejecutar con:
    python manage.py shell < scripts/limpiar_y_poblar.py
"""
import os
import sys
import django
from django.utils import timezone

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from src.login.models import PerfilUsuario
from src.materiales.models import (
    Libro, Coleccion, LibroColeccion, Categoria, Anotacion,
    ParticipacionColeccion, InvitacionColeccion, SolicitudAccesoColeccion,
    BitacoraColeccion, ComentarioRetroalimentacion, PropuestaCambioColeccion
)
from src.feed.models import Publicacion, Republicacion, Seguimiento, Notificacion
from src.recomendaciones.models import HistorialLectura, DescarteRecomendacion

User = get_user_model()

print("--- Iniciando limpieza de base de datos ---")

# 1. Limpiar todas las tablas secundarias (respetando dependencias de claves foráneas)
print("Eliminando Descartes...")
DescarteRecomendacion.objects.all().delete()

print("Eliminando Historial de Lectura...")
HistorialLectura.objects.all().delete()

print("Eliminando Notificaciones...")
Notificacion.objects.all().delete()

print("Eliminando Republicaciones...")
Republicacion.objects.all().delete()

print("Eliminando Publicaciones...")
Publicacion.objects.all().delete()

print("Eliminando Seguimientos...")
Seguimiento.objects.all().delete()

print("Eliminando Propuestas de cambio de colección...")
PropuestaCambioColeccion.objects.all().delete()

print("Eliminando Comentarios de retroalimentación...")
ComentarioRetroalimentacion.objects.all().delete()

print("Eliminando Bitácoras de colecciones...")
BitacoraColeccion.objects.all().delete()

print("Eliminando Solicitudes de acceso a colecciones...")
SolicitudAccesoColeccion.objects.all().delete()

print("Eliminando Invitaciones a colecciones...")
InvitacionColeccion.objects.all().delete()

print("Eliminando Participaciones en colecciones...")
ParticipacionColeccion.objects.all().delete()

print("Eliminando Libros en colecciones...")
LibroColeccion.objects.all().delete()

print("Eliminando Colecciones...")
Coleccion.objects.all().delete()

print("Eliminando Anotaciones...")
Anotacion.objects.all().delete()

print("Eliminando Libros...")
Libro.objects.all().delete()

print("Eliminando Categorías...")
Categoria.objects.all().delete()

print("¡Limpieza completada con éxito!")
print()
print("--- Creando nuevas Categorías de prueba ---")

nombres_categorias = [
    'Matematicas', 'Fisica', 'Quimica', 'Biologia',
    'Historia', 'Filosofia', 'Literatura', 'Programacion',
    'Ingenieria', 'Economia',
]
categorias_dict = {}
for nombre in nombres_categorias:
    cat = Categoria.objects.create(nombre=nombre)
    categorias_dict[nombre] = cat

print(f"Creadas {len(categorias_dict)} categorías.")
print()
print("--- Asegurando la existencia de Usuarios con sus Perfiles ---")

autores_data = [
    ('prof_garcia', 'garcia@ejemplo.com', 'Carlos Garcia', PerfilUsuario.PROFESOR),
    ('prof_lopez', 'lopez@ejemplo.com', 'Carlos Lopez', PerfilUsuario.PROFESOR),
    ('est_martinez', 'martinez@ejemplo.com', 'Ana Martinez', PerfilUsuario.ESTUDIANTE),
    ('est_rodriguez', 'rodriguez@ejemplo.com', 'Luis Rodriguez', PerfilUsuario.ESTUDIANTE),
    ('prof_herrera', 'herrera@ejemplo.com', 'Sofia Herrera', PerfilUsuario.PROFESOR),
    ('estudiante_lopez', 'autor2@biblioteca.com', 'Ana Lopez', PerfilUsuario.ESTUDIANTE),
    ('usuario_prueba', 'prueba@ejemplo.com', 'Usuario de Prueba', PerfilUsuario.ESTUDIANTE),
    ('SnowPoom', 'jonathan.pagual@hotmail.com', 'Jonathan Josue Pagual', PerfilUsuario.ESTUDIANTE),
]

usuarios_dict = {}
for username, email, nombre, rol in autores_data:
    user = User.objects.filter(username=username).first()
    if not user:
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=nombre.split(' ')[0],
            last_name=nombre.split(' ')[1] if len(nombre.split(' ')) > 1 else '',
        )
        user.set_password('password123')
        user.save()
        print(f"Creado usuario: {username}")
    else:
        print(f"Usuario existente conservado: {username}")
    
    PerfilUsuario.objects.get_or_create(usuario=user, defaults={'rol': rol})
    usuarios_dict[username] = user

print()
print("--- Poblando Libros y Publicaciones correspondientes ---")

libros_data = [
    # (titulo, autor_username, categorias_list, paginas, vistas, descargas, repubs)
    ('Calculo Diferencial Aplicado', 'prof_garcia', ['Matematicas'], 320, 450, 180, 45),
    ('Algebra Lineal para Ingenieros', 'prof_garcia', ['Matematicas', 'Ingenieria'], 280, 380, 150, 30),
    ('Mecanica Cuantica Introductoria', 'prof_lopez', ['Fisica'], 400, 520, 210, 60),
    ('Termodinamica y sus Aplicaciones', 'prof_lopez', ['Fisica', 'Quimica'], 350, 290, 120, 25),
    ('Quimica Organica Fundamental', 'est_martinez', ['Quimica'], 420, 610, 300, 70),
    ('Biologia Molecular Moderna', 'est_martinez', ['Biologia'], 380, 340, 140, 35),
    ('Genetica y Evolucion', 'est_rodriguez', ['Biologia'], 300, 200, 80, 15),
    ('Historia de las Civilizaciones', 'est_rodriguez', ['Historia'], 450, 700, 350, 90),
    ('La Revolucion Industrial', 'prof_herrera', ['Historia', 'Economia'], 250, 420, 170, 40),
    ('Introduccion a la Filosofia', 'prof_herrera', ['Filosofia'], 200, 550, 230, 55),
    ('Etica y Moral Contemporanea', 'prof_garcia', ['Filosofia'], 180, 310, 130, 28),
    ('Narrativa Latinoamericana', 'prof_lopez', ['Literatura'], 350, 480, 200, 50),
    ('Poesia del Siglo XX', 'est_martinez', ['Literatura'], 150, 190, 70, 12),
    ('Python para Ciencia de Datos', 'est_rodriguez', ['Programacion'], 400, 900, 450, 120),
    ('Estructuras de Datos en Java', 'prof_herrera', ['Programacion', 'Matematicas'], 380, 750, 380, 95),
    ('Diseno de Sistemas Distribuidos', 'prof_garcia', ['Programacion', 'Ingenieria'], 420, 650, 280, 75),
    ('Resistencia de Materiales', 'prof_lopez', ['Ingenieria', 'Fisica'], 360, 410, 160, 38),
    ('Microeconomia Avanzada', 'est_martinez', ['Economia', 'Matematicas'], 300, 330, 140, 32),
    ('Macroeconomia Global', 'est_rodriguez', ['Economia', 'Historia'], 280, 270, 110, 22),
    ('Inteligencia Artificial Practica', 'prof_herrera', ['Programacion', 'Matematicas'], 450, 850, 420, 110),
]

libros_creados = {}
for titulo, autor_name, cats, paginas, vistas, descargas, repubs in libros_data:
    autor_obj = usuarios_dict[autor_name]
    
    libro = Libro.objects.create(
        titulo=titulo,
        autor=autor_obj,
        estado=Libro.PUBLICADO,
        contenido_texto=f'Contenido completo del libro "{titulo}". Este material cubre los temas fundamentales con ejercicios practicos.',
        numero_paginas=paginas,
        visualizaciones=vistas,
        descargas=descargas,
        republicaciones=repubs,
    )
    
    # Asignar categorías
    libro.categorias.set([categorias_dict[cat_nombre] for cat_nombre in cats])
    
    # Crear publicación espejo para el feed (usando estructura actual)
    Publicacion.objects.create(
        libro=libro,
    )
    
    libros_creados[titulo] = libro

print(f"Creados {len(libros_creados)} libros con sus publicaciones espejo en el feed.")
print()
print("--- Creando Colecciones públicas y privadas ---")

colecciones_data = [
    # (nombre, creador_username, visibilidad, categorias, libros_titulos)
    ('Colección de Matemáticas Avanzadas', 'prof_garcia', Coleccion.PUBLICA, ['Matematicas', 'Ingenieria'], ['Calculo Diferencial Aplicado', 'Algebra Lineal para Ingenieros']),
    ('Fundamentos de la Ciencia', 'prof_lopez', Coleccion.PUBLICA, ['Fisica', 'Quimica', 'Biologia'], ['Mecanica Cuantica Introductoria', 'Termodinamica y sus Aplicaciones']),
    ('Desarrollo de Software Moderno', 'prof_herrera', Coleccion.PUBLICA, ['Programacion'], ['Python para Ciencia de Datos', 'Estructuras de Datos en Java']),
    ('Mi Álbum Privado de Lectura', 'SnowPoom', Coleccion.PRIVADA, ['Literatura'], ['Narrativa Latinoamericana', 'Poesia del Siglo XX']),
]

for nombre, creador_name, visibilidad, cats, libros_tits in colecciones_data:
    creador_obj = usuarios_dict[creador_name]
    
    col = Coleccion.objects.create(
        nombre=nombre,
        creador=creador_obj,
        visibilidad=visibilidad,
    )
    col.categorias.set([categorias_dict[cat_nombre] for cat_nombre in cats])
    
    # Agregar los libros a la colección
    for t in libros_tits:
        lib_obj = libros_creados[t]
        LibroColeccion.objects.create(
            coleccion=col,
            libro=lib_obj,
            agregado_por=creador_obj
        )
    
    # Si es pública, crear publicación espejo en el feed
    if visibilidad == Coleccion.PUBLICA:
        Publicacion.objects.create(
            coleccion=col,
        )

print("Creadas las colecciones y añadidas a publicaciones en el feed.")
print()
print("--- Creando relaciones de Seguimiento (Follows) ---")

seguimientos = [
    ('SnowPoom', 'prof_garcia'),
    ('SnowPoom', 'prof_lopez'),
    ('SnowPoom', 'estudiante_lopez'),
    ('SnowPoom', 'usuario_prueba'),
    ('usuario_prueba', 'prof_garcia'),
    ('usuario_prueba', 'prof_lopez'),
    ('usuario_prueba', 'estudiante_lopez'),
    ('usuario_prueba', 'SnowPoom'),
]

for seguidor_name, seguido_name in seguimientos:
    seguidor_obj = usuarios_dict[seguidor_name]
    seguido_obj = usuarios_dict[seguido_name]
    Seguimiento.objects.create(
        seguidor=seguidor_obj,
        seguido=seguido_obj,
    )

print(f"Creadas {len(seguimientos)} relaciones de seguimiento.")
print()
print("--- Simulando Historial de Lectura para probar recomendaciones ---")

lecturas_data = {
    'SnowPoom': [
        'Calculo Diferencial Aplicado',
        'Algebra Lineal para Ingenieros',
        'Python para Ciencia de Datos',
        'Estructuras de Datos en Java'
    ],
    'usuario_prueba': [
        'Python para Ciencia de Datos',
        'Estructuras de Datos en Java',
        'Calculo Diferencial Aplicado',
        'Historia de las Civilizaciones'
    ]
}

total_lecturas = 0
for username, libros_tits in lecturas_data.items():
    user_obj = usuarios_dict[username]
    for t in libros_tits:
        lib_obj = libros_creados[t]
        pub_obj = Publicacion.objects.get(libro=lib_obj)
        
        # Simular lectura
        HistorialLectura.objects.create(
            usuario=user_obj,
            publicacion=pub_obj,
        )
        total_lecturas += 1

print(f"Registradas {total_lecturas} lecturas de prueba.")
print()
print("==================================================================")
print(" PROCESO DE POBLAMIENTO Y LIMPIEZA FINALIZADO CON ÉXITO")
print("==================================================================")
print("Usuarios de prueba disponibles:")
print("  - SnowPoom / password123 (Administrador de su propia cuenta)")
print("  - usuario_prueba / password123")
print("  - prof_garcia / password123")
print("  - prof_lopez / password123")
print("  - est_rodriguez / password123")
print("==================================================================")
