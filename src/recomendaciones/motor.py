from django.db.models import Sum, F, Value, FloatField, ExpressionWrapper
from django.db.models.functions import Coalesce
from django.utils import timezone

from src.feed.models import Publicacion
from src.materiales.models import Libro
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
                autor=self.usuario
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
        ).select_related('publicacion').prefetch_related('publicacion__categorias')

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

            for categoria in lectura.publicacion.categorias.all():
                nombre = categoria.nombre
                pesos_categorias[nombre] = (
                    pesos_categorias.get(nombre, 0.0) + peso_temporal
                )

        return pesos_categorias

    def _puntuacion_publicacion(self, publicacion, pesos_categorias):
        """Calcula la puntuacion de relevancia de una publicacion candidata.

        Combina dos senales:
        1. Afinidad tematica: suma de pesos de las categorias que coinciden
           con las exploradas por el usuario (RN-REC-01, RN-REC-08).
        2. Popularidad colectiva: combinacion ponderada de visualizaciones,
           descargas y republicaciones del material original (RN-REC-02).
        """
        # Senal 1: afinidad tematica
        afinidad = 0.0
        for categoria in publicacion.categorias.all():
            afinidad += pesos_categorias.get(categoria.nombre, 0.0)

        # Senal 2: popularidad colectiva obtenida desde el Libro original
        popularidad = 0.0
        if publicacion.tipo == Publicacion.LIBRO:
            libro = Libro.objects.filter(pk=publicacion.pk).first()
            if libro:
                popularidad = (
                    libro.visualizaciones * PESO_VISUALIZACIONES
                    + libro.descargas * PESO_DESCARGAS
                    + libro.republicaciones * PESO_REPUBLICACIONES
                )

        # Se normaliza la popularidad para no dominar la afinidad
        popularidad_normalizada = popularidad / 100.0 if popularidad else 0.0

        return afinidad + popularidad_normalizada

    def _recomendaciones_personalizadas(self, tipo=None):
        """Genera recomendaciones basadas en el perfil del usuario."""
        ids_excluidos = self._ids_excluidos()
        pesos_categorias = self._categorias_ponderadas()

        candidatas = Publicacion.objects.exclude(
            pk__in=ids_excluidos
        ).prefetch_related('categorias')

        if tipo == 'libros':
            candidatas = candidatas.filter(tipo=Publicacion.LIBRO)
        elif tipo == 'colecciones':
            candidatas = candidatas.filter(tipo=Publicacion.COLECCION)

        # Calcular puntuacion y ordenar
        puntuadas = []
        for pub in candidatas:
            puntuacion = self._puntuacion_publicacion(pub, pesos_categorias)
            puntuadas.append((puntuacion, pub))

        # Orden descendente por puntuacion
        puntuadas.sort(key=lambda par: par[0], reverse=True)

        # Aplicar el limite de 10 libros y 10 colecciones
        libros_agregados = 0
        colecciones_agregadas = 0
        resultado_final = []

        for _, pub in puntuadas:
            if pub.tipo == Publicacion.LIBRO and libros_agregados < 10:
                resultado_final.append(pub)
                libros_agregados += 1
            elif pub.tipo == Publicacion.COLECCION and colecciones_agregadas < 10:
                resultado_final.append(pub)
                colecciones_agregadas += 1

        return resultado_final

    def _recomendaciones_arranque_frio(self, tipo=None):
        """Contenido de mayor consumo general para usuarios sin historial (RN-REC-05).

        Se ordena por las metricas colectivas de los libros asociados.
        """
        ids_excluidos = self._ids_excluidos()

        candidatas = Publicacion.objects.exclude(
            pk__in=ids_excluidos
        ).prefetch_related('categorias')

        if tipo == 'libros':
            candidatas = candidatas.filter(tipo=Publicacion.LIBRO)
        elif tipo == 'colecciones':
            candidatas = candidatas.filter(tipo=Publicacion.COLECCION)

        # Para arranque en frio, se ordenan por popularidad pura
        resultados = []
        for pub in candidatas:
            popularidad = 0.0
            if pub.tipo == Publicacion.LIBRO:
                libro = Libro.objects.filter(pk=pub.pk).first()
                if libro:
                    popularidad = (
                        libro.visualizaciones * PESO_VISUALIZACIONES
                        + libro.descargas * PESO_DESCARGAS
                        + libro.republicaciones * PESO_REPUBLICACIONES
                    )
            resultados.append((popularidad, pub))

        resultados.sort(key=lambda par: par[0], reverse=True)

        # Aplicar el limite de 10 libros y 10 colecciones
        libros_agregados = 0
        colecciones_agregadas = 0
        resultado_final = []

        for _, pub in resultados:
            if pub.tipo == Publicacion.LIBRO and libros_agregados < 10:
                resultado_final.append(pub)
                libros_agregados += 1
            elif pub.tipo == Publicacion.COLECCION and colecciones_agregadas < 10:
                resultado_final.append(pub)
                colecciones_agregadas += 1

        return resultado_final
