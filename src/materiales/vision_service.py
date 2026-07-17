import os
import json
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Try to import google genai
try:
    from google import genai
    from google.genai import types
    from pydantic import BaseModel
    class EvaluacionMultimodal(BaseModel):
        es_texto_relacionado: bool
        motivo_texto: str
        son_imagenes_apropiadas: bool
        son_imagenes_relacionadas: bool
        motivo_imagenes: str
        
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("google-genai no esta instalado. La validacion por IA no funcionara.")

def validar_contenido_multimodal(imagenes_bytes: List[bytes], categorias: List[str], titulo: str, texto_resumen: str) -> Dict[str, Any]:
    """
    Analiza tanto el texto (titulo, categorias, contenido) como las imagenes del libro 
    en una unica peticion a Gemini para ahorrar llamadas a la API.
    """
    if not GENAI_AVAILABLE:
        return {'aprobado': True, 'mensaje': ''}

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {'aprobado': True, 'mensaje': ''}

    try:
        client = genai.Client(api_key=api_key)
        
        contents = []
        from PIL import Image
        import io
        
        # Procesar y comprimir imagenes
        for img_bytes in imagenes_bytes[:5]:
            try:
                img = Image.open(io.BytesIO(img_bytes))
                if img.mode in ('RGBA', 'P', 'LA'):
                    img = img.convert('RGB')
                img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=85)
                compressed_bytes = output.getvalue()
                
                contents.append(
                    types.Part.from_bytes(data=compressed_bytes, mime_type='image/jpeg')
                )
            except Exception as e_img:
                logger.error(f"Error comprimiendo imagen: {e_img}")
                contents.append(
                    types.Part.from_bytes(data=img_bytes, mime_type='image/jpeg')
                )

        cats_str = ", ".join(categorias)
        
        prompt = f"""
        Eres un revisor académico de una biblioteca digital. 
        Evalúa el siguiente libro, que cuenta con el título "{titulo}", pertenece a las categorías [{cats_str}], 
        y trata sobre: "{texto_resumen[:2000]}...".

        Debes evaluar dos cosas en un solo formato JSON estructurado:

        1. Análisis del TEXTO:
           - ¿El contenido del texto guarda una relación lógica y semántica con el título y las categorías?
           
        2. Análisis de las IMÁGENES (si se adjuntaron):
           - Seguridad: ¿Las imágenes contienen material inapropiado, ofensivo, violencia o desnudez?
           - Relevancia: ¿Las imágenes tienen alguna relación visual o de apoyo con el tema del libro? (Sé flexible, acepta imágenes genéricas que encajen). Si no hay imágenes, marca esto como verdadero.

        Responde exactamente con el esquema JSON requerido.
        - "es_texto_relacionado": true/false
        - "motivo_texto": Explicación si el texto se rechaza (vacío si se aprueba).
        - "son_imagenes_apropiadas": true/false (false si son ofensivas).
        - "son_imagenes_relacionadas": true/false (false si las imágenes son totalmente desconectadas del texto, ej. un gato en un libro de matemáticas).
        - "motivo_imagenes": Explicación si las imágenes se rechazan (vacío si se aprueban).
        """
        
        contents.append(prompt)

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=EvaluacionMultimodal,
            temperature=0.1,
        )

        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=contents,
            config=config,
        )

        if not response.parsed:
            return {'aprobado': True, 'mensaje': ''}
            
        resultado = response.parsed
        
        # Validar el resultado del texto
        if not resultado.es_texto_relacionado:
            motivo = resultado.motivo_texto or 'El titulo y contenido del libro no guardan relacion con la categoria.'
            return {'aprobado': False, 'mensaje': motivo}
            
        # Validar el resultado de las imagenes
        if not resultado.son_imagenes_apropiadas:
            return {'aprobado': False, 'mensaje': 'Las imagenes contienen material inapropiado.'}
            
        if not resultado.son_imagenes_relacionadas:
            motivo = resultado.motivo_imagenes or 'Las imagenes no tienen relacion con el tema del libro.'
            return {'aprobado': False, 'mensaje': motivo}

        return {'aprobado': True, 'mensaje': ''}

    except Exception as e:
        logger.error(f"Error en validacion multimodal IA: {str(e)}")
        # Falla abierta: en caso de error técnico, dejamos pasar la validacion
        return {'aprobado': True, 'mensaje': ''}
