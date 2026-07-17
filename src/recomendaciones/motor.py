from django.db.models import Sum, F, Value, FloatField, ExpressionWrapper, Q
from django.db.models.functions import Coalesce
from django.utils import timezone

from src.feed.models import Publicacion
from src.materiales.models import Libro, Coleccion
from .models import HistorialLectura, DescarteRecomendacion


# Umbral minimo de registros en el historial para considerar
# que el usuario tiene actividad suficiente y no cae en arranque en frio.
UMBRAL_ACTIVIDAD_MINIMA = 1

# Peso relativo de cada metrica colectiva (RN-REC-02)
PESO_VISUALIZACIONES = 1.0
PESO_DESCARGAS = 3.0
PESO_REPUBLICACIONES = 5.0

# Factor de decaimiento temporal por dia de antiguedad (RN-REC-08).
# Cuanto mayor sea, mas rapido pierden peso las lecturas antiguas.
DECAIMIENTO_TEMPORAL_POR_DIA = 0.02


class MotorRecomendaciones:
    """Servicio que genera recomendaciones personalizadas para un usuario.

    Reglas de negocio aplicadas:
    - RN-REC-01: Historial de lectura y areas tematicas como senales primarias.
    - RN-REC-02: Metricas colectivas (vistas, descargas, republicaciones) como
      senal de relevancia.
    - RN-REC-03: Exclusion de contenido ya consumido.
    - RN-REC-04: Exclusion de contenido descartado.
    - RN-REC-06: Actualizacion dinamica conforme el usuario interactua.
    - RN-REC-07: Diferenciacion entre libros y colecciones con filtrado.
    - RN-REC-08: Actividad reciente con mayor peso que la antigua.
    """

    def __init__(self, usuario):
        self.usuario = usuario

    # ------------------------------------------------------------------
    # API publica
    # ------------------------------------------------------------------

    def obtener_recomendaciones(self, tipo=None):
        """Genera la lista ordenada de recomendaciones para el usuario.

        Args:
            tipo: Filtro opcional — 'libros' o 'colecciones' (RN-REC-07).

        Returns:
            QuerySet de Publicacion ordenado por puntuacion descendente.
        """
        if not self._tiene_actividad_suficiente():
            return self._recomendaciones_arranque_frio(tipo)

        return self._recomendaciones_personalizadas(tipo)

    # ------------------------------------------------------------------
    # Metodos internos
    # ------------------------------------------------------------------

    def _tiene_actividad_suficiente(self):
        """Determina si el usuario supera el umbral de actividad minima."""
        return (
            HistorialLectura.objects.filter(usuario=self.usuario).count()
            >= UMBRAL_ACTIVIDAD_MINIMA
        )

    def _ids_excluidos(self):
        """Devuelve los PKs de publicaciones que deben excluirse (RN-REC-03, RN-REC-04).

        Se excluyen:
        - Contenido ya consumido por el usuario (historial de lectura).
        - Contenido descartado explicitamente por el usuario.
        - Contenido propio del usuario.
        """
        ids_leidos = set(
            HistorialLectura.objects.filter(
                usuario=self.usuario
            ).values_list('publicacion_id', flat=True)
        )
        ids_descartados = set(
            DescarteRecomendacion.objects.filter(
                usuario=self.usuario
            ).values_list('publicacion_id', flat=True)
        )
        ids_propios = set(
            Publicacion.objects.filter(
                Q(libro__autor=self.usuario) | Q(coleccion__creador=self.usuario)
            ).values_list('pk', flat=True)
        )
        return ids_leidos | ids_descartados | ids_propios

    def _categorias_ponderadas(self):
        """Calcula el peso de cada categoria segun el historial del usuario.

        RN-REC-01: Las categorias mas exploradas tienen mayor relevancia.
        RN-REC-08: La actividad reciente pondera mas que la antigua.
        El peso de cada lectura decae con el tiempo usando un factor lineal.

        Returns:
            dict {nombre_categoria: peso_acumulado}
        """
        ahora = timezone.now()
        lecturas = HistorialLectura.objects.filter(
            usuario=self.usuario
        ).select_related('publicacion').prefetch_related('publicacion__libro__categorias', 'publicacion__coleccion__categorias')

        pesos_categorias = {}

        for lectura in lecturas:
            dias_antiguedad = max(
                (ahora - lectura.fecha).days, 0
            )
            # Peso temporal: decae linealmente, minimo 0.1
            peso_temporal = max(
                1.0 - (DECAIMIENTO_TEMPORAL_POR_DIA * dias_antiguedad),
                0.1,
            )

            for categoria in lectura.publicacion.categorias.all() if lectura.publicacion.categorias else []:
                nombre = categoria.nombre
                pesos_categorias[nombre] = (
                    pesos_categorias.get(nombre, 0.0) + peso_temporal
                )

        # Restar peso a las categorias basandose en las publicaciones descartadas
        descartes = DescarteRecomendacion.objects.filter(
            usuario=self.usuario
        ).select_related('publicacion').prefetch_related('publicacion__libro__categorias', 'publicacion__coleccion__categorias')

        for descarte in descartes:
            dias_antiguedad = max(
                (ahora - descarte.fecha).days, 0
            )
            # El peso negativo tiene el mismo decaimiento
            peso_temporal = max(
                1.0 - (DECAIMIENTO_TEMPORAL_POR_DIA * dias_antiguedad),
                0.1,
            )

            for categoria in descarte.publicacion.categorias.all() if descarte.publicacion.categorias else []:
                nombre = categoria.nombre
                pesos_categorias[nombre] = (
                    pesos_categorias.get(nombre, 0.0) - peso_temporal
                )

        return pesos_categorias

    def _construir_queryset_anotado(self, candidatas, pesos_categorias=None):
        """Construye las consultas a la base de datos para libros y colecciones
        anotando su relevancia y popularidad.
        """
        from django.db.models import Subquery, OuterRef, FloatField, Value, F, Case, When, Sum
        from django.db.models.functions import Coalesce
        from src.materiales.models import Libro, Coleccion

        # Expresion para calcular popularidad de un libro
        pop_expr = (
            F('visualizaciones') * Value(PESO_VISUALIZACIONES) +
            F('descargas') * Value(PESO_DESCARGAS) +
            F('republicaciones') * Value(PESO_REPUBLICACIONES)
        )

        # 1. Subconsulta para popularidad de Libros
        libro_qs = Libro.objects.filter(pk=OuterRef('libro_id')).annotate(
            pop_calc=ExpressionWrapper(pop_expr, output_field=FloatField())
        )
        subq_libro_pop = Subquery(libro_qs.values('pop_calc')[:1], output_field=FloatField())

        # 2. Subconsulta para popularidad de Colecciones (suma de los libros que contiene)
        coleccion_qs = Coleccion.objects.filter(pk=OuterRef('coleccion_id')).annotate(
            pop_total=Sum(
                F('libros__visualizaciones') * Value(PESO_VISUALIZACIONES) +
                F('libros__descargas') * Value(PESO_DESCARGAS) +
                F('libros__republicaciones') * Value(PESO_REPUBLICACIONES),
                output_field=FloatField()
            )
        )
        subq_coleccion_pop = Subquery(coleccion_qs.values('pop_total')[:1], output_field=FloatField())

        # 3. Expresion para afinidad tematica (solo si hay pesos)
        if pesos_categorias:
            whens_libro = [When(libro__categorias__nombre=nombre, then=Value(peso)) for nombre, peso in pesos_categorias.items()]
            whens_coleccion = [When(coleccion__categorias__nombre=nombre, then=Value(peso)) for nombre, peso in pesos_categorias.items()]
            if whens_libro:
                afinidad_expr_libro = Coalesce(Sum(Case(*whens_libro, default=Value(0.0), output_field=FloatField())), Value(0.0))
                afinidad_expr_coleccion = Coalesce(Sum(Case(*whens_coleccion, default=Value(0.0), output_field=FloatField())), Value(0.0))
            else:
                afinidad_expr_libro = Value(0.0)
                afinidad_expr_coleccion = Value(0.0)
        else:
            afinidad_expr_libro = Value(0.0)
            afinidad_expr_coleccion = Value(0.0)

        # 4. Separar querysets y anotar
        qs_libros = candidatas.filter(libro__isnull=False).annotate(
            popularidad_bruta=Coalesce(subq_libro_pop, Value(0.0)),
            afinidad=afinidad_expr_libro
        ).annotate(
            puntuacion=F('afinidad') + (F('popularidad_bruta') / 100.0)
        ).order_by('-puntuacion')[:10]

        qs_colecciones = candidatas.filter(coleccion__isnull=False).annotate(
            popularidad_bruta=Coalesce(subq_coleccion_pop, Value(0.0)),
            afinidad=afinidad_expr_coleccion
        ).annotate(
            puntuacion=F('afinidad') + (F('popularidad_bruta') / 100.0)
        ).order_by('-puntuacion')[:10]

        return qs_libros, qs_colecciones

    def _recomendaciones_personalizadas(self, tipo=None):
        """Genera recomendaciones basadas en el perfil del usuario."""
        ids_excluidos = self._ids_excluidos()
        pesos_categorias = self._categorias_ponderadas()

        candidatas = Publicacion.objects.exclude(
            pk__in=ids_excluidos
        ).prefetch_related('libro__categorias', 'coleccion__categorias')

        qs_libros, qs_colecciones = self._construir_queryset_anotado(candidatas, pesos_categorias)

        # Ejecutar las consultas limitadas a 10 cada una
        libros = list(qs_libros) if tipo in (None, 'libros') else []
        colecciones = list(qs_colecciones) if tipo in (None, 'colecciones') else []

        # Mezclar y ordenar en Python (maximo 20 elementos)
        resultado_final = libros + colecciones
        resultado_final.sort(key=lambda pub: pub.puntuacion, reverse=True)

        return resultado_final

    def _recomendaciones_arranque_frio(self, tipo=None):
        """Contenido de mayor consumo general para usuarios sin historial (RN-REC-05).
        Se ordena por las metricas colectivas de los libros asociados.
        """
        ids_excluidos = self._ids_excluidos()

        candidatas = Publicacion.objects.exclude(
            pk__in=ids_excluidos
        ).prefetch_related('libro__categorias', 'coleccion__categorias')

        # Para arranque en frio, no hay afinidad tematica (pesos_categorias=None)
        qs_libros, qs_colecciones = self._construir_queryset_anotado(candidatas, None)

        libros = list(qs_libros) if tipo in (None, 'libros') else []
        colecciones = list(qs_colecciones) if tipo in (None, 'colecciones') else []

        resultado_final = libros + colecciones
        resultado_final.sort(key=lambda pub: pub.puntuacion, reverse=True)

        return resultado_final
