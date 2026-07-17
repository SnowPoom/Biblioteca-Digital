"""
Servicio de validacion automatizada de contenido para material educativo.

Implementa RN-PUB-02: todo material publicado debe pasar por una validacion
automatizada de contenido apropiado y relevancia academica antes de quedar
visible para la comunidad.

El proceso simula una revision academica evaluando tres criterios:
1. Calidad del contenido textual (coherencia y riqueza linguistica).
2. Relacion tematica entre titulo, contenido y categoria.
3. Relevancia de las imagenes respecto al contenido del libro.
"""

import os
import re
import unicodedata
import base64
import requests
from bs4 import BeautifulSoup
from .vision_service import validar_contenido_multimodal


# -----------------------------------------------------------------------
# Umbrales de validacion
# -----------------------------------------------------------------------

# Un texto coherente en espanol contiene al menos un 10% de palabras
# funcionales (articulos, preposiciones, conjunciones). Textos con menos
# de este porcentaje carecen de estructura linguistica natural.
UMBRAL_MINIMO_PALABRAS_FUNCIONALES = 0.10

# Si mas del 40% de las palabras del texto son basura (relleno, letras
# repetidas, secuencias aleatorias), el contenido se considera invalido.
UMBRAL_MAXIMO_PALABRAS_BASURA = 0.40


# -----------------------------------------------------------------------
# Vocabulario de referencia
# -----------------------------------------------------------------------

# Palabras funcionales del espanol (articulos, preposiciones, conjunciones
# y pronombres). Su presencia es indicador de texto con estructura real.
PALABRAS_FUNCIONALES = {
    'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
    'de', 'del', 'al', 'a', 'en', 'con', 'por', 'para', 'sin',
    'sobre', 'entre', 'y', 'o', 'u', 'e', 'ni', 'que', 'es',
    'son', 'se', 'su', 'sus', 'como', 'mas', 'pero', 'sino',
    'no', 'si', 'ya', 'este', 'esta', 'estos', 'estas',
    'ante', 'bajo', 'hacia', 'hasta', 'segun', 'tras',
    'lo', 'le', 'les', 'me', 'te', 'nos', 'mi', 'tu',
    'ser', 'ha', 'hay', 'fue', 'era', 'tiene', 'hace',
    'todo', 'cada', 'otro', 'otra', 'muy', 'tan',
    'cuando', 'donde', 'porque', 'aunque', 'mientras',
    'tambien', 'asi', 'aqui', 'ahi', 'alli',
}

# Palabras de relleno comunmente usadas en textos generados o sin sentido
PALABRAS_RELLENO = {
    'lorem', 'ipsum', 'dolor', 'sit', 'amet', 'consectetur',
    'adipiscing', 'elit', 'sed', 'eiusmod', 'tempor',
    'incididunt', 'labore', 'dolore', 'magna', 'aliqua',
    'bla', 'blah', 'foo', 'bar', 'baz', 'qux',
    'asdf', 'qwerty', 'zxcv', 'wasd',
}

VOCALES = set('aeiou')


# Diccionario basico de palabras inapropiadas o censuradas
PALABRAS_INAPROPIADAS = {
    'puta', 'puto', 'mierda', 'pendejo', 'pendeja', 'idiota', 'estupido',
    'estupida', 'imbecil', 'cabron', 'maricon', 'zorra', 'perra', 'coño',
    'joder', 'carajo', 'verga', 'pene', 'vagina', 'culo', 'mierdas'
}


class ValidadorContenido:
    """Servicio que evalua si un libro cumple los criterios de calidad
    academica necesarios para ser publicado en la plataforma.

    Aplica tres criterios de revision en orden:
    1. Calidad del contenido textual (coherencia y riqueza del texto).
    2. Relacion tematica entre titulo, contenido y categoria.
    3. Relevancia de las imagenes respecto al contenido.
    """

    def validar(self, libro):
        """Ejecuta la validacion completa del libro.

        Retorna un diccionario con:
        - 'aprobado': True si supera todos los criterios, False en caso contrario.
        - 'mensaje': Descripcion del resultado dirigida al autor.
        """
        resultado_calidad = self._validar_calidad_contenido(libro)
        if not resultado_calidad['aprobado']:
            return resultado_calidad

        # Llamada unica a la IA (valida texto e imagenes a la vez para ahorrar cuota)
        resultado_ia = self._validar_tematica_e_imagenes_ia(libro)
        if not resultado_ia['aprobado']:
            return resultado_ia

        resultado_plagio = self._validar_plagio(libro)
        if not resultado_plagio['aprobado']:
            return resultado_plagio

        resultado_inapropiado = self._validar_palabras_inapropiadas(libro)
        if not resultado_inapropiado['aprobado']:
            return resultado_inapropiado

        return {
            'aprobado': True,
            'mensaje': 'El contenido ha superado la validacion automatica.',
        }

    # -------------------------------------------------------------------
    # Criterio 1: Calidad del contenido textual
    # -------------------------------------------------------------------

    def _validar_calidad_contenido(self, libro):
        """Verifica que el texto sea coherente, enriquecido y con sentido.

        Analiza la proporcion de palabras funcionales del idioma y la
        cantidad de palabras basura para determinar si el texto tiene
        estructura linguistica real o es relleno sin sentido.
        """
        texto_normalizado = self._normalizar_texto(libro.contenido_texto)
        palabras = re.findall(r'[a-z]+', texto_normalizado)

        total_palabras = len(palabras)
        if total_palabras < 10:
            return {
                'aprobado': False,
                'mensaje': (
                    'Validacion rechazada: el contenido del libro es '
                    'insuficiente para una publicacion academica.'
                ),
            }

        # RN-PUB-02: Un texto coherente en espanol presenta al menos un
        # porcentaje minimo de palabras funcionales (articulos, preposiciones).
        # Su ausencia indica texto generado o aleatorio.
        cantidad_funcionales = sum(
            1 for p in palabras if p in PALABRAS_FUNCIONALES
        )
        proporcion_funcionales = cantidad_funcionales / total_palabras

        cantidad_basura = sum(
            1 for p in palabras if self._es_palabra_basura(p)
        )
        proporcion_basura = cantidad_basura / total_palabras

        if proporcion_basura > UMBRAL_MAXIMO_PALABRAS_BASURA:
            return {
                'aprobado': False,
                'mensaje': (
                    'Validacion rechazada: el contenido del libro carece de '
                    'sentido o esta compuesto por texto de relleno no valido '
                    'para una publicacion academica.'
                ),
            }

        if proporcion_funcionales < UMBRAL_MINIMO_PALABRAS_FUNCIONALES:
            return {
                'aprobado': False,
                'mensaje': (
                    'Validacion rechazada: el contenido del libro no presenta '
                    'estructura linguistica coherente para una publicacion '
                    'academica.'
                ),
            }

        return {'aprobado': True, 'mensaje': ''}

    # -------------------------------------------------------------------
    # Criterio 2 y 3: Validacion tematica y de imagenes por IA
    # -------------------------------------------------------------------

    def _validar_tematica_e_imagenes_ia(self, libro):
        """
        Extrae las imagenes y el texto, y delega a la IA la evaluacion de:
        - Relacion semantica del texto con categorias y titulo.
        - Idoneidad y relevancia de las imagenes aportadas.
        Se hace en una sola llamada para minimizar el consumo de API (RN-PUB-02).
        """
        categorias = libro.categorias.all()
        if not categorias.exists():
            return {
                'aprobado': False,
                'mensaje': 'No se puede validar tematicamente sin una categoria asignada.'
            }

        categorias_nombres = [c.nombre for c in categorias]
        texto_resumen = self._normalizar_texto(libro.contenido_texto)[:2000]

        imagenes_a_analizar = []

        # 1. Extraer portada si existe
        if libro.portada and libro.portada.name:
            try:
                libro.portada.seek(0)
                imagenes_a_analizar.append(libro.portada.read())
            except Exception:
                pass

        # 2. Extraer imagenes base64 o HTTP del contenido HTML
        if libro.contenido_texto:
            try:
                soup = BeautifulSoup(libro.contenido_texto, 'html.parser')
                for img in soup.find_all('img'):
                    src = img.get('src', '')
                    if src.startswith('data:image'):
                        try:
                            base64_str = src.split(',')[1]
                            img_bytes = base64.b64decode(base64_str)
                            imagenes_a_analizar.append(img_bytes)
                        except Exception:
                            pass
                    elif src.startswith('http'):
                        try:
                            resp = requests.get(src, timeout=3)
                            if resp.status_code == 200:
                                imagenes_a_analizar.append(resp.content)
                        except Exception:
                            pass
            except Exception:
                pass

        # Llamar al servicio de IA Multimodal
        return validar_contenido_multimodal(
            imagenes_bytes=imagenes_a_analizar,
            categorias=categorias_nombres,
            titulo=libro.titulo,
            texto_resumen=texto_resumen
        )

    # -------------------------------------------------------------------
    # Criterio 4: Detección de plagio
    # -------------------------------------------------------------------

    def _validar_plagio(self, libro):
        """Verifica si el contenido textual del libro ya existe en la plataforma."""
        if not libro.contenido_texto:
            return {'aprobado': True, 'mensaje': ''}

        texto_limpio = self._normalizar_texto(libro.contenido_texto).strip()
        if not texto_limpio:
            return {'aprobado': True, 'mensaje': ''}

        # Comparamos con otros libros publicados (excluyendo el actual)
        libros_publicados = type(libro).objects.filter(estado='publicado').exclude(pk=libro.pk)
        
        for otro_libro in libros_publicados:
            otro_texto_limpio = self._normalizar_texto(otro_libro.contenido_texto).strip()
            if texto_limpio == otro_texto_limpio:
                return {
                    'aprobado': False,
                    'mensaje': (
                        'Validacion rechazada: se ha detectado que el contenido del libro '
                        'es idéntico a otra publicación existente en la plataforma. '
                        'No se permite contenido copiado (plagio).'
                    ),
                }

        return {'aprobado': True, 'mensaje': ''}

    # -------------------------------------------------------------------
    # Criterio 5: Detección de lenguaje inapropiado
    # -------------------------------------------------------------------

    def _validar_palabras_inapropiadas(self, libro):
        """Verifica que el contenido no contenga lenguaje ofensivo o inapropiado."""
        texto_normalizado = self._normalizar_texto(libro.contenido_texto)
        titulo_normalizado = self._normalizar_texto(libro.titulo)
        
        texto_completo = f"{titulo_normalizado} {texto_normalizado}"
        palabras_texto = set(re.findall(r'[a-z]{3,}', texto_completo))
        
        coincidencias = palabras_texto.intersection(PALABRAS_INAPROPIADAS)
        
        if coincidencias:
            return {
                'aprobado': False,
                'mensaje': (
                    'Validacion rechazada: se ha detectado el uso de lenguaje '
                    'inapropiado u ofensivo en el titulo o contenido del libro. '
                    'La plataforma mantiene un entorno academico.'
                ),
            }
            
        return {'aprobado': True, 'mensaje': ''}

    # -------------------------------------------------------------------
    # Metodos auxiliares
    # -------------------------------------------------------------------

    def _es_palabra_basura(self, palabra):
        """Determina si una palabra es basura (relleno, repetitiva o aleatoria)."""
        if palabra in PALABRAS_RELLENO:
            return True

        # Palabras compuestas por un solo caracter repetido (xxx, aaa)
        if len(palabra) >= 2 and len(set(palabra)) == 1:
            return True

        # Secuencias alfabeticas consecutivas (mnop, qrst, stuv)
        if self._es_secuencia_alfabetica(palabra):
            return True

        # Palabras sin ninguna vocal no son propias del idioma
        if len(palabra) >= 2 and not any(c in VOCALES for c in palabra):
            return True

        return False

    def _es_secuencia_alfabetica(self, palabra):
        """Detecta secuencias de letras consecutivas en el alfabeto."""
        if len(palabra) < 3:
            return False
        for i in range(1, len(palabra)):
            if ord(palabra[i]) != ord(palabra[i - 1]) + 1:
                return False
        return True

    def _normalizar_texto(self, texto):
        """Elimina acentos y convierte a minusculas para comparacion uniforme."""
        if not texto:
            return ''
        texto = texto.lower()
        texto = unicodedata.normalize('NFD', texto)
        texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
        # Reemplazar guiones y guiones bajos por espacios para no juntar palabras
        texto = re.sub(r'[-_]', ' ', texto)
        # Eliminar cualquier cosa que no sea alfanumérica o espacio
        return re.sub(r'[^a-z0-9\s]', '', texto)
