import os
import json
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Optional, Tuple
import PyPDF2
from tabulate import tabulate
from tqdm import tqdm
import requests

# Configurar logger para que solo muestre errores
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

from .gemini_processor import GeminiProcessor
from .job_profiles import is_candidate_suitable, JOB_PROFILES
from .contact_generator import generate_whatsapp_link

class CVProcessor:
    def __init__(self, base_dir: str):
        from system.config import CURRICULUMS_FOLDER, RESULT_FOLDER, CV_PROCESSOR_FOLDER, CV_PROCESSOR_TOP3_FOLDER
        
        self.base_dir = os.path.abspath(base_dir)
        self.curriculums_dir = CURRICULUMS_FOLDER
        self.results_dir = CV_PROCESSOR_FOLDER
        self.top3_dir = CV_PROCESSOR_TOP3_FOLDER
        self.gemini_processor = GeminiProcessor()
        
        # Crear directorios si no existen
        os.makedirs(self.curriculums_dir, exist_ok=True)
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.top3_dir, exist_ok=True)

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            logger.error(f"Error al procesar {pdf_path}: {str(e)}")
            return ""

    def process_cv(self, pdf_path: str, puesto: str) -> Tuple[dict, float]:
        """
        Procesa un CV y retorna la información estructurada y su puntaje
        """
        try:
            # Extraer texto del PDF
            cv_text = self.extract_text_from_pdf(pdf_path)
            if not cv_text:
                logger.error(f"No se pudo extraer texto del archivo {os.path.basename(pdf_path)}")
                return None, 0
            
            # Analizar CV con Gemini
            cv_data = self.gemini_processor.analyze_cv(cv_text)
            if not cv_data or not isinstance(cv_data, dict):
                logger.error(f"Gemini no pudo analizar el CV {os.path.basename(pdf_path)}")
                return None, 0
            
            # Asegurar que los campos existan y tengan valores válidos
            required_fields = ['nombre', 'habilidades']
            if not all(field in cv_data for field in required_fields):
                logger.error(f"CV incompleto: faltan campos requeridos en {os.path.basename(pdf_path)}")
                return None, 0

            # Normalizar campos que podrían ser None
            cv_data['ubicacion'] = cv_data.get('ubicacion') or 'No especificada'
            cv_data['telefono'] = cv_data.get('telefono') or 'No especificado'
            cv_data['correo'] = cv_data.get('correo') or 'No especificado'
            cv_data['idiomas'] = cv_data.get('idiomas') or []
            cv_data['educacion'] = cv_data.get('educacion') or ['No especificada']
            cv_data['experiencia'] = cv_data.get('experiencia') or []
            
            # Evaluar si el candidato es apto
            is_suitable, score = is_candidate_suitable(cv_data, puesto)
            
            # Guardar score en los datos del CV
            cv_data['score'] = score
            
            return cv_data, score
            
        except Exception as e:
            logger.error(f"Error procesando {os.path.basename(pdf_path)}: {str(e)}")
            return None, 0
            
    def process_all_cvs(self, puesto: str, recruiter_name: str = "Recursos Humanos") -> List[Tuple[dict, float]]:
        """
        Procesa todos los CVs en el directorio de currículums
        """
        # Verificar que el puesto sea válido
        if not puesto or puesto.lower() not in JOB_PROFILES:
            raise ValueError(f"Puesto no válido. Opciones disponibles: {', '.join(JOB_PROFILES.keys())}")
            
        # Verificar API key silenciosamente
        if not self.gemini_processor.verify_api_key():
            raise ValueError("Error: API key de Gemini no válida o no configurada")
            
        # Buscar archivos PDF
        pdf_files = [f for f in os.listdir(self.curriculums_dir) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            print("\nNo se encontraron archivos PDF en el directorio.")
            return []
        
        print("\nIniciando procesamiento de CVs...")
        
        # Lista para almacenar resultados
        results = []
        cache_dir = os.path.join(self.results_dir, "cache")
        os.makedirs(cache_dir, exist_ok=True)
        
        # Limpiar caché anterior del puesto actual
        for cache_file in os.listdir(cache_dir):
            if f"_{puesto.lower()}_cache.json" in cache_file.lower():
                try:
                    os.remove(os.path.join(cache_dir, cache_file))
                except Exception as e:
                    logger.warning(f"No se pudo eliminar archivo de caché {cache_file}: {str(e)}")
        
        # Configurar barra de progreso ASCII
        total_files = len(pdf_files)
        progress_width = 40
        
        def process_cv_file(pdf_file):
            try:
                pdf_path = os.path.join(self.curriculums_dir, pdf_file)
                # Incluir el puesto en el nombre del archivo de caché
                cache_file = os.path.join(cache_dir, f"{os.path.splitext(pdf_file)[0]}_{puesto.lower()}_cache.json")
                
                # Intentar cargar del caché primero
                if os.path.exists(cache_file):
                    try:
                        with open(cache_file, 'r', encoding='utf-8') as f:
                            cv_data = json.load(f)
                            if cv_data and isinstance(cv_data, dict):
                                score = cv_data.get("score", 0)
                                return cv_data, score
                    except Exception as e:
                        logger.warning(f"Error al cargar caché para {pdf_file}: {str(e)}")
                
                # Procesar CV
                cv_data, score = self.process_cv(pdf_path, puesto)
                if cv_data and isinstance(cv_data, dict) and score > 0:
                    # Guardar en caché
                    try:
                        with open(cache_file, 'w', encoding='utf-8') as f:
                            json.dump(cv_data, f, indent=4, ensure_ascii=False)
                    except Exception as e:
                        logger.warning(f"Error al guardar caché para {pdf_file}: {str(e)}")
                    return cv_data, score
                
                return None, 0
                
            except Exception as e:
                logger.error(f"Error procesando {pdf_file}: {str(e)}")
                return None, 0
        
        # Procesar CVs en paralelo con ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for pdf_file in pdf_files:
                future = executor.submit(process_cv_file, pdf_file)
                futures.append(future)
            
            # Mostrar barra de progreso mientras se procesan los CVs
            completed = 0
            while completed < total_files:
                completed = sum(1 for f in futures if f.done())
                progress = int((completed / total_files) * progress_width)
                bar = "█" * progress + "░" * (progress_width - progress)
                percentage = (completed / total_files) * 100
                print(f"\rProcesando: [{bar}] {percentage:0.1f}%", end="", flush=True)
                time.sleep(0.1)
            
            # Recolectar resultados
            for future in futures:
                cv_data, score = future.result()
                if cv_data and isinstance(cv_data, dict) and score >= 50:  # Solo incluir candidatos con puntaje >= 50%
                    results.append((cv_data, score))
        
        print("\n\nProcesamiento completado.")
        
        if not results:
            print("\nNo se encontraron candidatos aptos para el puesto.")
            return []
        
        # Ordenar por score descendente
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Tomar los 3 mejores resultados
        top_results = results[:3]
        
        # Guardar top 3 en archivos separados
        for i, (cv_data, score) in enumerate(top_results, 1):
            filename = f"top{i}_{puesto.lower()}_{cv_data.get('nombre', 'candidato').replace(' ', '_')}.json"
            filepath = os.path.join(self.top3_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(cv_data, f, indent=4, ensure_ascii=False)
        
        return top_results

    def _generate_short_url(self, long_url: str) -> str:
        """
        Genera una URL corta usando TinyURL
        """
        try:
            response = requests.get(f'http://tinyurl.com/api-create.php?url={long_url}')
            if response.status_code == 200:
                return response.text
            return long_url
        except:
            return long_url

    def _format_candidate_info(self, cv_data: dict, score: float, recruiter_name: str = "Recursos Humanos") -> str:
        """
        Formatea la información del candidato en una tabla ASCII
        """
        # Generar estrellas basadas en el score
        stars = "★" * int(score/20) + "☆" * (5 - int(score/20))
        
        # Calcular años de experiencia
        años_experiencia = 0
        experiencia = cv_data.get('experiencia', [])
        if isinstance(experiencia, list):
            for exp in experiencia:
                if isinstance(exp, dict):
                    periodo = exp.get('periodo', '').lower()
                    if 'presente' in periodo or 'actual' in periodo:
                        try:
                            año_inicio = int(''.join(filter(str.isdigit, periodo.split('-')[0])))
                            años_experiencia += 2024 - año_inicio
                        except:
                            pass
        
        # Formatear idiomas
        idiomas = cv_data.get("idiomas", [])
        if not idiomas:
            idiomas = ["No especificados"]
        
        # Formatear experiencia
        experiencia = cv_data.get("experiencia", [])
        experiencia_str = []
        
        if experiencia:
            for exp in experiencia:
                if isinstance(exp, dict):
                    puesto = exp.get("puesto", "No especificado")
                    empresa = exp.get("empresa", "No especificada")
                    periodo = exp.get("periodo", "No especificado")
                    responsabilidades = exp.get("responsabilidades", [])
                    
                    exp_str = [f"• {puesto} en {empresa} ({periodo})"]
                    for resp in responsabilidades:
                        exp_str.append(f"   - {resp}")
                    experiencia_str.extend(exp_str)
                else:
                    experiencia_str.append(f"• {exp}")
        else:
            experiencia_str = ["No especificada"]
        
        # Formatear habilidades en columnas
        habilidades = cv_data.get("habilidades", [])
        if not habilidades:
            habilidades = ["No especificadas"]
        
        # Dividir habilidades en dos columnas
        habilidades_formatted = []
        for i in range(0, len(habilidades), 2):
            if i + 1 < len(habilidades):
                habilidades_formatted.append(f"• {habilidades[i]:<20} • {habilidades[i+1]}")
            else:
                habilidades_formatted.append(f"• {habilidades[i]}")
        
        # Generar enlace de WhatsApp
        whatsapp_link = generate_whatsapp_link(
            telefono=cv_data.get("telefono", ""),
            recruiter_name=recruiter_name,
            nombre=cv_data.get("nombre", "Candidato")
        )
        
        # Construir tabla
        table = f"""
╔═══════════════════════════════════════════════════════════════════════════════════════════════╗
║ {cv_data.get('nombre', 'No especificado'):<77} ║
║ {stars} {score}% - {años_experiencia} años de experiencia{' ':<50} ║
╠═══════════════════════════════╦═══════════════════════════════════════════════════════════════╣
║ Contacto                      ║ Teléfono: {cv_data.get('telefono', 'No especificado'):<43} ║
║                               ║ Email: {cv_data.get('correo', 'No especificado'):<46} ║
║                               ║ Ubicación: {cv_data.get('ubicacion') or 'No especificada':<42} ║
║                               ║ WhatsApp: {whatsapp_link:<44} ║
╠═══════════════════════════════╬═══════════════════════════════════════════════════════════════╣
║ Educación                     ║ {('• ' + cv_data.get('educacion', ['No especificada'])[0]):<55} ║"""
        
        # Agregar educación adicional si existe
        for edu in cv_data.get('educacion', [])[1:]:
            table += f"""
║                               ║ • {edu:<53} ║"""
        
        # Agregar experiencia
        table += f"""
╠═══════════════════════════════╬═══════════════════════════════════════════════════════════════╣
║ Experiencia                   ║ {experiencia_str[0]:<55} ║"""
        
        for exp in experiencia_str[1:]:
            table += f"""
║                               ║ {exp:<55} ║"""
        
        # Agregar habilidades
        table += f"""
╠═══════════════════════════════╬═══════════════════════════════════════════════════════════════╣
║ Habilidades                   ║ {habilidades_formatted[0]:<55} ║"""
        
        for hab in habilidades_formatted[1:]:
            table += f"""
║                               ║ {hab:<55} ║"""
        
        # Agregar idiomas
        table += f"""
╠═══════════════════════════════╬═══════════════════════════════════════════════════════════════╣
║ Idiomas                       ║ {idiomas[0]:<55} ║"""
        
        for idioma in idiomas[1:]:
            table += f"""
║                               ║ {idioma:<55} ║"""
        
        # Cerrar tabla
        table += """
╚═══════════════════════════════╩═══════════════════════════════════════════════════════════════╝"""
        
        return table

    def display_results(self, suitable_candidates: List[Tuple[dict, float]], recruiter_name: str = "Recursos Humanos") -> None:
        """
        Muestra los resultados del procesamiento
        """
        if not suitable_candidates:
            print("\nNo se encontraron candidatos aptos para el puesto.")
            return
        
        print("\n=== TOP 3 CANDIDATOS ===\n")
        
        for i, (cv_data, score) in enumerate(suitable_candidates, 1):
            print(f"\nCandidato #{i}")
            print(self._format_candidate_info(cv_data, score, recruiter_name))
        
        print("\nResultados guardados en la carpeta 'Results/CV Processor'")
