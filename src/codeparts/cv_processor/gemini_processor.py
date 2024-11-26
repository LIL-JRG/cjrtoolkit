import time
import logging
import google.generativeai as genai
from google.api_core import retry
from typing import Dict, Any
import json
import os
from dotenv import load_dotenv

# Configurar logger para que solo muestre errores
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

class GeminiProcessor:
    def __init__(self):
        load_dotenv()
        
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    @retry.Retry(
        predicate=lambda exc: isinstance(exc, Exception) and '429' in str(exc),
        initial=1.0,  # Espera inicial de 1 segundo
        maximum=10.0,  # Espera máxima de 10 segundos
        multiplier=2.0,  # Duplica el tiempo de espera en cada intento
        deadline=300.0  # Tiempo límite total de 5 minutos
    )
    def _generate_with_retry(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error al generar contenido con Gemini: {str(e)}")
            raise

    def verify_api_key(self) -> bool:
        """
        Verifica si la API key de Gemini está configurada y es válida
        """
        try:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                return False
            
            # Configurar Gemini con la API key
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            
            # Hacer una prueba simple para verificar que la API key funciona
            test_prompt = "Test API key"
            response = self.model.generate_content(test_prompt)
            return True
            
        except Exception as e:
            logger.error(f"Error al verificar API key: {str(e)}")
            return False

    def analyze_cv(self, cv_text: str) -> dict:
        """
        Analiza un CV usando Gemini y retorna la información estructurada
        """
        try:
            if not cv_text or not cv_text.strip():
                logger.error("El texto del CV está vacío")
                return {}

            prompt = f"""
            Analiza el siguiente CV y extrae la información en formato JSON.
            
            INSTRUCCIONES:
            1. Extrae todas las habilidades mencionadas
            2. Infiere habilidades adicionales de la experiencia
            3. Identifica habilidades específicas del sector
            4. Evalúa nivel de experiencia
            
            HABILIDADES A IDENTIFICAR:
            - Habilidades técnicas (software, herramientas)
            - Habilidades profesionales (gestión, análisis)
            - Habilidades blandas (comunicación, trabajo en equipo)
            - Microsoft Office (Excel, Word)
            - Atención al cliente
            - Organización y planificación
            
            FORMATO JSON:
            {{
                "nombre": "nombre del candidato",
                "correo": "email",
                "telefono": "teléfono",
                "ubicacion": "ciudad",
                "habilidades": ["habilidad1", "habilidad2"],
                "idiomas": ["idioma1 (nivel)", "idioma2 (nivel)"],
                "educacion": ["educación1", "educación2"],
                "experiencia": [
                    {{
                        "puesto": "cargo",
                        "empresa": "empresa",
                        "periodo": "fechas",
                        "responsabilidades": ["responsabilidad1", "responsabilidad2"]
                    }}
                ]
            }}

            CV:
            {cv_text}

            IMPORTANTE: Responde SOLO con el JSON.
            """
            
            response_text = self._generate_with_retry(prompt)

            # Intentar extraer el JSON de la respuesta
            try:
                # Encontrar el primer '{' y el último '}'
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                
                if start >= 0 and end > start:
                    json_str = response_text[start:end]
                    return json.loads(json_str)
                else:
                    logger.error("No se encontró JSON en la respuesta")
                    return {}
                    
            except json.JSONDecodeError as e:
                logger.error(f"Error al decodificar JSON: {str(e)}")
                return {}
                
        except Exception as e:
            logger.error(f"Error al analizar CV: {str(e)}")
            return {}
