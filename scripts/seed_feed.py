"""
Script de datos de prueba para el feed de seguimiento.
Ejecutar con: python manage.py shell < scripts/seed_feed.py
"""
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from src.login.models import PerfilUsuario
from src.feed.models import Seguimiento, Publicacion, Republicacion

User = get_user_model()

# Limpia datos previos del seed para poder re-ejecutarlo
emails_seed = [
    'tester@biblioteca.com',
    'autor1@biblioteca.com',
    'autor2@biblioteca.com',
    'externo@biblioteca.com',
]
User.objects.filter(email__in=emails_seed).delete()

# Crea el usuario principal (el que va a "iniciar sesión")
tester = User.objects.create_user(
    username='tester',
    email='tester@biblioteca.com',
    password='test1234',
    first_name='Usuario',
    last_name='Tester',
)
PerfilUsuario.objects.create(usuario=tester, rol=PerfilUsuario.ESTUDIANTE)

# Crea dos usuarios a los que el tester sigue
autor1 = User.objects.create_user(
    username='prof_garcia',
    email='autor1@biblioteca.com',
    password='test1234',
    first_name='Carlos',
    last_name='García',
)
PerfilUsuario.objects.create(usuario=autor1, rol=PerfilUsuario.PROFESOR)

autor2 = User.objects.create_user(
    username='estudiante_lopez',
    email='autor2@biblioteca.com',
    password='test1234',
    first_name='Ana',
    last_name='López',
)
PerfilUsuario.objects.create(usuario=autor2, rol=PerfilUsuario.ESTUDIANTE)

# Crea un usuario que NO es seguido (su contenido no debe aparecer)
externo = User.objects.create_user(
    username='externo',
    email='externo@biblioteca.com',
    password='test1234',
    first_name='Usuario',
    last_name='Externo',
)
PerfilUsuario.objects.create(usuario=externo, rol=PerfilUsuario.ESTUDIANTE)

# El tester sigue a autor1 y autor2 (pero NO a externo)
Seguimiento.objects.create(seguidor=tester, seguido=autor1)
Seguimiento.objects.create(seguidor=tester, seguido=autor2)

# Publicaciones de los seguidos
pub1 = Publicacion.objects.create(
    autor=autor1,
    titulo='Introducción a la Epistemología',
    descripcion='Una guía completa sobre los fundamentos del conocimiento y la teoría del saber. '
                'Ideal para estudiantes de filosofía y ciencias sociales.',
    tipo=Publicacion.LIBRO,
)

pub2 = Publicacion.objects.create(
    autor=autor2,
    titulo='Métodos de Investigación Cualitativa',
    descripcion='Herramientas prácticas para diseñar y ejecutar investigaciones de campo. '
                'Incluye estudios de caso y análisis de datos cualitativos.',
    tipo=Publicacion.LIBRO,
)

pub3 = Publicacion.objects.create(
    autor=autor1,
    titulo='Colección: Filosofía Contemporánea',
    descripcion='Selección de textos clave del pensamiento filosófico del siglo XX.',
    tipo=Publicacion.COLECCION,
)

# Publicacion del externo (NO debe aparecer en el feed del tester)
Publicacion.objects.create(
    autor=externo,
    titulo='Este libro NO debe verse en el feed',
    descripcion='Publicado por alguien que el tester no sigue.',
    tipo=Publicacion.LIBRO,
)

# Republicación: autor2 republica un libro del externo
pub_externa = Publicacion.objects.create(
    autor=externo,
    titulo='Sociología del Conocimiento — Texto Clásico',
    descripcion='Obra fundamental de la sociología moderna, republicada por uno de tus seguidos.',
    tipo=Publicacion.LIBRO,
)
Republicacion.objects.create(
    publicacion=pub_externa,
    republicado_por=autor2,
)

print()
print('Datos de prueba creados correctamente.')
print()
print('Usuarios creados:')
print('  tester@biblioteca.com       / test1234  (usuario principal)')
print('  autor1@biblioteca.com       / test1234  (seguido por tester)')
print('  autor2@biblioteca.com       / test1234  (seguido por tester)')
print('  externo@biblioteca.com      / test1234  (NO seguido)')
print()
print('Accede al feed en: http://127.0.0.1:8000/feed/')
print('Inicia sesion en:  http://127.0.0.1:8000/auth/')
