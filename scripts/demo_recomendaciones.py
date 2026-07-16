"""
Script de demostracion interactiva del Motor de Recomendaciones.
Muestra de forma transparente como se calculan las puntuaciones y
como reacciona el sistema ante una nueva lectura.

Ejecutar con:
    python manage.py shell < scripts/demo_recomendaciones.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from src.feed.models import Publicacion, Categoria as FeedCategoria
from src.recomendaciones.motor import MotorRecomendaciones
from src.recomendaciones.models import HistorialLectura
from src.materiales.models import Libro
from django.utils import timezone

User = get_user_model()

# ---------------------------------------------------------
# 1. Asegurar que existan Colecciones en la base de datos
# ---------------------------------------------------------
autor_demo = User.objects.filter(username='prof_garcia').first()
usuario = User.objects.filter(username='usuario_prueba').first()
if not autor_demo or not usuario:
    print("Por favor, ejecuta primero 'python manage.py shell < scripts/poblar_libros.py'")
    exit()

colecciones_data = [
    ('Coleccion de Matematicas Avanzadas', ['Matematicas', 'Ingenieria']),
    ('Fundamentos de la Ciencia', ['Fisica', 'Quimica', 'Biologia']),
    ('Biblioteca de Letras e Historia', ['Literatura', 'Historia']),
    ('Desarrollo de Software Moderno', ['Programacion']),
]

for titulo, categorias in colecciones_data:
    pub, created = Publicacion.objects.get_or_create(
        titulo=titulo,
        tipo=Publicacion.COLECCION,
        defaults={
            'autor': autor_demo,
        }
    )
    
    # Sincronizar categorías siempre (idempotencia)
    feed_cats = []
    for cat_nombre in categorias:
        fcat = FeedCategoria.objects.filter(nombre=cat_nombre).first()
        if fcat:
            feed_cats.append(fcat)
    pub.categorias.set(feed_cats)

# ---------------------------------------------------------
# 2. Obtener el usuario de prueba y su motor
# ---------------------------------------------------------
motor = MotorRecomendaciones(usuario)

def imprimir_estado_actual(titulo_bloque):
    print(f"\n{'='*60}")
    print(f" {titulo_bloque.upper()}")
    print(f"{'='*60}")
    
    # 2.1 Historial actual
    print("\n[ HISTORIAL DE LECTURA ]")
    historial = HistorialLectura.objects.filter(usuario=usuario).order_by('-fecha')
    for h in historial:
        dias = (timezone.now() - h.fecha).days
        print(f" - {h.publicacion.titulo} (hace {dias} dias)")
        
    # 2.2 Perfil de Intereses Ponderado (Senal 1)
    print("\n[ PERFIL DE INTERESES CALCULADO (Por afinidad tematica) ]")
    pesos = motor._categorias_ponderadas()
    for cat, peso in sorted(pesos.items(), key=lambda x: x[1], reverse=True):
        print(f" - {cat}: {peso:.2f} pts")
        
    # 2.3 Mejores Recomendaciones Explicadas
    print("\n[ TOP 5 RECOMENDACIONES - LIBROS ]")
    # Hack para obtener las puntuaciones (el motor devuelve solo las publicaciones ordenadas,
    # asi que recalculamos la puntuacion aqui para mostrartela)
    recs_libros = motor.obtener_recomendaciones(tipo='libros')[:5]
    for r in recs_libros:
        afinidad = sum(pesos.get(c.nombre, 0.0) for c in r.categorias.all())
        libro_orig = Libro.objects.filter(pk=r.pk).first()
        pop = (libro_orig.visualizaciones * 1.0 + libro_orig.descargas * 3.0 + libro_orig.republicaciones * 5.0) / 100.0 if libro_orig else 0.0
        total = afinidad + pop
        cats = [c.nombre for c in r.categorias.all()]
        print(f" ★ {total:.2f} pts | {r.titulo[:30]:<30} | {cats}")
        print(f"      L-> (Afinidad: {afinidad:.2f} + Popularidad: {pop:.2f})")

    print("\n[ TOP 3 RECOMENDACIONES - COLECCIONES ]")
    recs_cols = motor.obtener_recomendaciones(tipo='colecciones')[:3]
    for r in recs_cols:
        afinidad = sum(pesos.get(c.nombre, 0.0) for c in r.categorias.all())
        # Las colecciones puras (sin logica extra aqui) solo tienen afinidad
        print(f" ★ {afinidad:.2f} pts | {r.titulo[:30]:<30} | {[c.nombre for c in r.categorias.all()]}")

# ---------------------------------------------------------
# 3. Flujo de la demostracion
# ---------------------------------------------------------
imprimir_estado_actual("ESTADO INICIAL")

# Simulamos que el usuario lee un libro NUEVO
libro_nuevo = Publicacion.objects.filter(tipo=Publicacion.LIBRO).exclude(
    pk__in=HistorialLectura.objects.filter(usuario=usuario).values_list('publicacion_id')
).first()

if libro_nuevo:
    print("\n" + "*"*60)
    print(f" ACCION: El usuario entra a leer '{libro_nuevo.titulo}'")
    print(f" Categorias: {[c.nombre for c in libro_nuevo.categorias.all()]}")
    print("*"*60)
    
    HistorialLectura.objects.create(
        usuario=usuario,
        publicacion=libro_nuevo
    )
else:
    print("No hay libros nuevos para leer.")

# Volvemos a imprimir el estado para ver como cambian los puntajes
imprimir_estado_actual("ESTADO DESPUES DE LEER EL NUEVO LIBRO")

print("\nNota: Revisa tu frontend web en la pestaña 'Colecciones' para ver las nuevas colecciones creadas.")
