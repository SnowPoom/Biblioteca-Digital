"""Script para asignar categorias a las publicaciones del seed."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from src.feed.models import Categoria, Publicacion  # noqa: E402

cat_filosofia, _ = Categoria.objects.get_or_create(nombre='Filosofia')
cat_epistemologia, _ = Categoria.objects.get_or_create(nombre='Epistemologia')
cat_investigacion, _ = Categoria.objects.get_or_create(nombre='Investigacion')
cat_sociologia, _ = Categoria.objects.get_or_create(nombre='Sociologia')
cat_metodologia, _ = Categoria.objects.get_or_create(nombre='Metodologia')

for p in Publicacion.objects.all():
    titulo = p.titulo.lower()
    if 'epistemolog' in titulo:
        p.categorias.set([cat_filosofia, cat_epistemologia])
    elif 'metodos' in titulo or 'investigacion' in titulo:
        p.categorias.set([cat_investigacion, cat_metodologia])
    elif 'sociolog' in titulo:
        p.categorias.set([cat_sociologia])
    elif 'filosof' in titulo:
        p.categorias.set([cat_filosofia])

    nombres = list(p.categorias.values_list('nombre', flat=True))
    print(p.titulo, '->', nombres)

print('Categorias asignadas.')
