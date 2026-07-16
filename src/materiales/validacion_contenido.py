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

# Cantidad minima de palabras clave de la categoria que deben aparecer
# en el contenido para considerar que existe relacion tematica.
MINIMO_COINCIDENCIAS_TEMATICAS = 1


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

# Palabras clave asociadas a categorias academicas comunes. Se utilizan
# para determinar si el contenido de un libro guarda relacion con la
# categoria tematica que el autor le asigno al publicarlo.
PALABRAS_CLAVE_CATEGORIAS = {
    'matematicas': [
        'matematica', 'algebra', 'calculo', 'ecuacion', 'funcion',
        'numero', 'vector', 'matriz', 'geometria', 'estadistica',
        'teorema', 'formula', 'integral', 'derivada', 'variable',
        'lineal', 'trigonometria', 'logaritmo', 'probabilidad',
        'conjunto', 'demostracion', 'axioma', 'polinomio',
    ],
    'ciencias': [
        'ciencia', 'biologia', 'quimica', 'fisica', 'celula',
        'atomo', 'molecula', 'energia', 'experimento', 'laboratorio',
        'organismo', 'ecosistema', 'natural', 'materia', 'fuerza',
        'reaccion', 'elemento', 'compuesto', 'genetica', 'evolucion',
    ],
    'programacion': [
        'programacion', 'codigo', 'software', 'algoritmo', 'python',
        'java', 'desarrollo', 'web', 'variable', 'funcion',
        'clase', 'objeto', 'compilador', 'lenguaje', 'datos',
        'estructura', 'tipado', 'interprete', 'automatizacion',
        'framework', 'servidor', 'cliente', 'api', 'programa',
    ],
    'historia': [
        'historia', 'historico', 'siglo', 'epoca', 'civilizacion',
        'guerra', 'imperio', 'revolucion', 'cultura', 'sociedad',
        'antiguo', 'medieval', 'moderno', 'contemporaneo', 'colonia',
    ],
    'literatura': [
        'literatura', 'novela', 'poesia', 'cuento', 'narrativa',
        'escritor', 'autor', 'genero', 'literario', 'prosa',
        'verso', 'obra', 'personaje', 'trama', 'ficcion',
    ],
    'arte': [
        'arte', 'pintura', 'escultura', 'dibujo', 'color',
        'composicion', 'artista', 'museo', 'galeria', 'estetica',
        'visual', 'creativo', 'diseno', 'fotografia', 'ilustracion',
    ],
    'ingenieria': [
        'ingenieria', 'ingeniero', 'diseno', 'sistema', 'proceso',
        'material', 'construccion', 'mecanica', 'electronica',
        'circuito', 'estructura', 'proyecto', 'plano', 'prototipo',
    ],
    'medicina': [
        'medicina', 'medico', 'salud', 'enfermedad', 'diagnostico',
        'tratamiento', 'paciente', 'hospital', 'clinica', 'cirugia',
        'farmaco', 'sintoma', 'anatomia', 'fisiologia', 'patologia',
    ],
    'economia': [
        'economia', 'mercado', 'oferta', 'demanda', 'precio',
        'produccion', 'consumo', 'capital', 'inversion', 'comercio',
        'finanzas', 'banco', 'moneda', 'inflacion', 'fiscal',
    ],
    'derecho': [
        'derecho', 'ley', 'norma', 'juridico', 'constitucion',
        'tribunal', 'juez', 'sentencia', 'codigo', 'penal',
        'civil', 'proceso', 'demanda', 'abogado', 'legislacion',
    ],
}

# Palabras genericas en nombres de archivo de portadas que no aportan
# informacion tematica y deben excluirse del analisis
PALABRAS_GENERICAS_ARCHIVO = {
    'portada', 'cover', 'imagen', 'image', 'images', 'img', 'foto', 'photo',
    'descarga', 'download', 'whatsapp', 'screenshot', 'captura', 'pantalla',
    'default', 'hqdefault', 'maxresdefault',
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

        resultado_tematica = self._validar_relacion_tematica(libro)
        if not resultado_tematica['aprobado']:
            return resultado_tematica

        resultado_imagenes = self._validar_relevancia_imagenes(libro)
        if not resultado_imagenes['aprobado']:
            return resultado_imagenes

        resultado_plagio = self._validar_plagio(libro)
        if not resultado_plagio['aprobado']:
            return resultado_plagio

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
    # Criterio 2: Relacion tematica titulo-contenido-categoria
    # -------------------------------------------------------------------

    def _validar_relacion_tematica(self, libro):
        """Verifica que el contenido este apegado a la categoria y que
        el titulo guarde relacion con el contenido.

        Compara las palabras del contenido contra un diccionario de
        palabras clave por categoria academica. Si no se encuentra
        coincidencia suficiente, el libro se rechaza por falta de
        relacion tematica.
        """
        categorias = libro.categorias.all()
        if not categorias.exists():
            return {
                'aprobado': False,
                'mensaje': (
                    'Validacion rechazada: no existe relación temática '
                    'verificable sin una categoria asignada al libro.'
                ),
            }

        texto_normalizado = self._normalizar_texto(libro.contenido_texto)
        palabras_contenido = set(re.findall(r'[a-z]{3,}', texto_normalizado))

        titulo_normalizado = self._normalizar_texto(libro.titulo)
        palabras_titulo = set(re.findall(r'[a-z]{3,}', titulo_normalizado))
        # Removemos palabras genéricas del título si es necesario o simplemente cruzamos
        if palabras_titulo and not palabras_titulo.intersection(palabras_contenido):
            return {
                'aprobado': False,
                'mensaje': (
                    'Validacion rechazada: no existe relación temática '
                    'entre el título del libro y su contenido textual.'
                ),
            }

        contenido_coincide_categoria = False
        for categoria in categorias:
            categoria_normalizada = self._normalizar_texto(categoria.nombre)

            # Verificar si el nombre de la categoria aparece en el contenido
            if categoria_normalizada in texto_normalizado:
                contenido_coincide_categoria = True
                break

            # Verificar contra el diccionario de palabras clave academicas
            palabras_clave = self._obtener_palabras_clave_categoria(
                categoria_normalizada,
            )
            coincidencias = palabras_contenido.intersection(palabras_clave)
            if len(coincidencias) >= MINIMO_COINCIDENCIAS_TEMATICAS:
                contenido_coincide_categoria = True
                break

        if not contenido_coincide_categoria:
            return {
                'aprobado': False,
                'mensaje': (
                    'Validacion rechazada: no se encontro relación temática '
                    'entre el titulo, el contenido y la categoria del libro.'
                ),
            }

        return {'aprobado': True, 'mensaje': ''}

    # -------------------------------------------------------------------
    # Criterio 3: Relevancia de imagenes respecto al contenido
    # -------------------------------------------------------------------

    def _validar_relevancia_imagenes(self, libro):
        """Verifica que las imagenes del libro (incluida la portada) guarden
        relacion con el contenido textual.

        Extrae palabras descriptivas del nombre del archivo de portada y
        las compara con las palabras clave del contenido, titulo y
        categoria del libro. Si no existe coincidencia, se considera
        que las imagenes no son representativas del tema.
        """
        if not libro.portada or not libro.portada.name:
            return {'aprobado': True, 'mensaje': ''}

        nombre_archivo = os.path.basename(libro.portada.name)
        nombre_sin_extension = os.path.splitext(nombre_archivo)[0]
        
        # Normalizamos el nombre del archivo y extraemos palabras que contengan letras y/o números
        nombre_normalizado = self._normalizar_texto(nombre_sin_extension)
        palabras_archivo = re.findall(r'[a-z0-9]+', nombre_normalizado)

        # Filtramos palabras genéricas, muy cortas, y posibles hashes de Django (7 caracteres alfanuméricos)
        palabras_imagen = {
            p for p in palabras_archivo
            if p not in PALABRAS_GENERICAS_ARCHIVO and len(p) >= 3 and not (len(p) == 7 and any(c.isdigit() for c in p))
        }

        # Si el nombre del archivo no contiene palabras descriptivas,
        # no es posible realizar la validacion y se aprueba por defecto
        if not palabras_imagen:
            return {'aprobado': True, 'mensaje': ''}

        texto_normalizado = self._normalizar_texto(libro.contenido_texto)
        titulo_normalizado = self._normalizar_texto(libro.titulo)
        texto_completo = f'{titulo_normalizado} {texto_normalizado}'
        palabras_texto = set(re.findall(r'[a-z]{3,}', texto_completo))

        # Incluir las palabras clave de la categoria en la comparacion
        for categoria in libro.categorias.all():
            cat_normalizada = self._normalizar_texto(categoria.nombre)
            palabras_clave = self._obtener_palabras_clave_categoria(
                cat_normalizada,
            )
            palabras_texto.update(palabras_clave)
            palabras_texto.add(cat_normalizada)

        coincidencias = palabras_imagen.intersection(palabras_texto)

        # Para reducir la severidad y no rechazar imágenes descargadas con nombres aleatorios
        # (ej. hashes de amazon, whatsapp, etc), solo rechazamos si el nombre tiene al menos 
        # 2 palabras descriptivas claras y ninguna coincide con el texto.
        if not coincidencias and len(palabras_imagen) >= 2:
            return {
                'aprobado': False,
                'mensaje': (
                    'Validacion rechazada: las imagenes del libro no guardan '
                    'coherencia con el contenido textual. La portada y demas '
                    'imagenes deben ser representativas del tema del libro.'
                ),
            }

        return {'aprobado': True, 'mensaje': ''}

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

    def _obtener_palabras_clave_categoria(self, categoria_normalizada):
        """Retorna el conjunto de palabras clave asociadas a una categoria.

        Busca coincidencia parcial entre el nombre de la categoria y las
        claves del diccionario, permitiendo variaciones como 'programacion'
        para la clave 'programacion'.
        """
        palabras_clave = set()
        for clave, lista in PALABRAS_CLAVE_CATEGORIAS.items():
            if clave in categoria_normalizada or categoria_normalizada in clave:
                palabras_clave.update(lista)
        palabras_clave.add(categoria_normalizada)
        return palabras_clave
