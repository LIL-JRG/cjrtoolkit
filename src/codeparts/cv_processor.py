import os
import re
import logging
import shutil
import asyncio
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional, Dict, Tuple
from pdf2image import convert_from_path
import pytesseract
from system.config import RESULT_FOLDER, KEYWORDS_CAMPO, KEYWORDS_OFICINA
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_method(func):
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            logging.info(f"{func.__name__} completado")
            return result
        except Exception as e:
            logging.error(f"Error en {func.__name__}: {str(e)}")
            raise
    return wrapper

class CVProcessor:

    @staticmethod
    def extract_name(text: str) -> str:
        name_pattern = r"\b([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){1,3})\b"
        invalid_names = ["Calle Cualquiera", "Institución Increible", "Cualquier Lugar", "Universidad Ensigna"]
        
        matches = re.finditer(name_pattern, text)
        for match in matches:
            name = match.group()
            if name not in invalid_names and len(name.split()) >= 2:
                return name
        return "Nombre no encontrado"
    
    @staticmethod
    def sanitize_filename(name: str) -> str:
        sanitized = re.sub(r'[<>:"/\\|?*\n\r\t]', '', name)
        sanitized = sanitized.replace(' ', '_')
        return sanitized[:255]
    
    @staticmethod
    def extract_phone(text: str) -> str:
        phone_pattern = r'\b(?:\+52|52)?[ -]?(?:1|01)?[ -]?(?:\d{3}[ -]?\d{3}[ -]?\d{4}|\d{2}[ -]?\d{4}[ -]?\d{4})\b'
        match = re.search(phone_pattern, text)
        if match:
            phone = re.sub(r'\D', '', match.group())
            if len(phone) == 10:
                return f"+52{phone}"
            elif len(phone) == 12 and phone.startswith("52"):
                return f"+{phone}"
        return "Teléfono no encontrado"
    
    @staticmethod
    def extract_email(text: str) -> str:
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group() if match else "Correo no encontrado"
    
    @staticmethod
    async def extract_text_from_pdf(filepath: str) -> str:
        try:
            pages = await asyncio.to_thread(convert_from_path, filepath)
            with ThreadPoolExecutor() as executor:
                texts = await asyncio.gather(*[
                    asyncio.to_thread(pytesseract.image_to_string, page)
                    for page in pages
                ])
            return "\n".join(f"\n--- Página {page_num} ---\n{page_text}" for page_num, page_text in enumerate(texts, start=1))
        except Exception as e:
            logging.error(f"Error al procesar PDF {filepath}: {str(e)}")
            return ""

    @classmethod
    @log_method
    async def process_cv(cls, folder: str, tipo_personal: str, puesto: str) -> Dict:
        now = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        resultado_folder = os.path.join(RESULT_FOLDER, f"{now}-CV-Sorter")
        os.makedirs(resultado_folder, exist_ok=True)
    
        tasks = [
            cls.process_file(os.path.join(folder, filename), resultado_folder, tipo_personal, puesto)
            for filename in os.listdir(folder)
            if filename.endswith('.pdf')
        ]
    
        candidates = await asyncio.gather(*tasks)
        candidates = [c for c in candidates if c]  # Remove None values
        
        if candidates:
            top_candidates = cls.select_top_candidates(candidates, tipo_personal, puesto)
            cls.save_top_candidates(top_candidates, resultado_folder)
            return {"top_candidatos": top_candidates}
        else:
            return {"top_candidatos": []}
    
    @classmethod
    async def process_file(cls, filepath: str, resultado_folder: str, tipo_personal: str, puesto: str) -> Optional[Dict]:
        text = await cls.extract_text_from_pdf(filepath)
        
        keywords = cls.get_keywords_for_position(tipo_personal, puesto)
        if cls.filter_keywords(text, keywords):
            return await cls.process_candidate(text, resultado_folder, os.path.basename(filepath), tipo_personal, puesto)
        return None
    
    @staticmethod
    def filter_keywords(text: str, keywords: List[str]) -> bool:
        return any(keyword.lower() in text.lower() for keyword in keywords)
    
    @classmethod
    @log_method
    async def process_candidate(cls, text: str, resultado_folder: str, filename: str, tipo_personal: str, puesto: str) -> Dict:
        candidate_info = {
            "nombre": cls.extract_name(text),
            "telefono": cls.extract_phone(text),
            "correo": cls.extract_email(text),
            "texto_completo": text,
            "tipo_personal": tipo_personal,
            "puesto": puesto,
            "filename": filename
        }
    
        sanitized_name = cls.sanitize_filename(candidate_info["nombre"])
        candidate_folder = os.path.join(resultado_folder, sanitized_name)
        os.makedirs(candidate_folder, exist_ok=True)
    
        new_filepath = os.path.join(candidate_folder, filename)
        await asyncio.to_thread(shutil.copy2, os.path.join('../curriculums', filename), new_filepath)
    
        whatsapp_link = (f"https://api.whatsapp.com/send/?phone={candidate_info['telefono']}&"
                         f"text=Hola_{candidate_info['nombre']},_hemos recibido tu CV&type=phone_number&app_absent=0"
                         if candidate_info['telefono'] != "Teléfono no encontrado" else "No disponible")
    
        txt_filename = f"{tipo_personal}_{puesto}_Candidato_{sanitized_name}.txt"
        with open(os.path.join(candidate_folder, txt_filename), 'w', encoding='utf-8') as f:
            f.write(f"Nombre completo: {candidate_info['nombre']}\n")
            f.write(f"Número de teléfono: {candidate_info['telefono']}\n")
            f.write(f"Correo electrónico: {candidate_info['correo']}\n")
            f.write(f"WhatsApp: {whatsapp_link}\n")
    
        logging.info(f"Procesado candidato: {candidate_info['nombre']}")
        return candidate_info

    @staticmethod
    def get_keywords_for_position(tipo_personal: str, puesto: str) -> List[str]:
        keywords = {
            "oficina": {
                "recepcionista": ["recepción", "atención al cliente", "agenda", "llamadas", "organización"],
                "administrador": ["administración", "gestión", "finanzas", "recursos", "planificación"],
                "gerente": ["liderazgo", "estrategia", "gestión de equipos", "toma de decisiones", "objetivos"],
                "supervisor": ["supervisión", "control de calidad", "coordinación", "reportes", "mejora continua"],
                "contador": ["contabilidad", "finanzas", "impuestos", "auditoría", "estados financieros"],
                "auxiliar_recepcionista": ["apoyo", "atención", "organización", "comunicación", "multitarea"],
                "auxiliar_administrador": ["apoyo administrativo", "archivo", "datos", "reportes", "correspondencia"],
                "auxiliar_gerente": ["apoyo gerencial", "agenda", "reuniones", "presentaciones", "informes"],
                "auxiliar_supervisor": ["apoyo en supervisión", "seguimiento", "reportes", "control", "asistencia"],
                "auxiliar_contador": ["apoyo contable", "registros", "conciliaciones", "facturas", "pagos"]
            },
            "campo": {
                "ingeniero_energia_renovable": ["energía renovable", "diseño", "proyectos", "eficiencia energética", "sostenibilidad"],
                "tecnico_instalacion": ["instalación", "montaje", "equipos", "mantenimiento", "seguridad"],
                "tecnico_mantenimiento": ["mantenimiento", "reparación", "diagnóstico", "preventivo", "correctivo"],
                "gerente_proyectos": ["gestión de proyectos", "planificación", "presupuestos", "equipos",   "energía renovable"],
                "gerente_desarrollo_negocios": ["desarrollo de negocios", "ventas", "estrategia", "mercado energético", "clientes"],
                "gerente_operaciones": ["operaciones", "logística", "optimización", "procesos", "KPIs"],
                "investigador_energia_solar": ["investigación", "energía solar", "innovación", "análisis", "desarrollo"],
                "ingeniero_biomasa": ["biomasa", "procesos térmicos", "conversión energética", "sostenibilidad", "diseño"],
                "ingeniero_almacenamiento_energia": ["almacenamiento de energía", "baterías", "sistemas", "eficiencia", "grid"]
            }
        }
        return keywords[tipo_personal][puesto]

    @staticmethod
    def select_top_candidates(candidates: List[Dict], tipo_personal: str, puesto: str) -> List[Dict]:
        keywords = CVProcessor.get_keywords_for_position(tipo_personal, puesto)
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([c['texto_completo'] for c in candidates])
        keyword_vector = vectorizer.transform([' '.join(keywords)])
        
        similarities = cosine_similarity(keyword_vector, tfidf_matrix)
        
        for i, candidate in enumerate(candidates):
            candidate['puntuacion'] = similarities[0][i]
        
        sorted_candidates = sorted(candidates, key=lambda x: x['puntuacion'], reverse=True)
        
        # Definir un umbral mínimo de puntuación (ajustado a 0.3 para que sea más intuitivo)
        umbral_minimo = 0.1
        
        top_candidates = [c for c in sorted_candidates if c['puntuacion'] >= umbral_minimo][:3]
        
        return top_candidates

    @staticmethod
    def save_top_candidates(top_candidates: List[Dict], resultado_folder: str) -> None:
        top_candidates_folder = os.path.join(resultado_folder, "Top_Candidatos")
        os.makedirs(top_candidates_folder, exist_ok=True)
        
        for i, candidate in enumerate(top_candidates, 1):
            sanitized_name = CVProcessor.sanitize_filename(candidate['nombre'])
            candidate_folder = os.path.join(top_candidates_folder, f"{i}_{sanitized_name}")
            os.makedirs(candidate_folder, exist_ok=True)
            
            # Copiar el archivo PDF del candidato
            shutil.copy2(
                os.path.join(resultado_folder, sanitized_name, candidate['filename']),
                os.path.join(candidate_folder, candidate['filename'])
            )
            
            # Crear un archivo de texto con la información del candidato
            with open(os.path.join(candidate_folder, "info_candidato.txt"), 'w', encoding='utf-8') as f:
                f.write(f"Nombre: {candidate['nombre']}\n")
                f.write(f"Teléfono: {candidate['telefono']}\n")
                f.write(f"Correo: {candidate['correo']}\n")
                f.write(f"Tipo de personal: {candidate['tipo_personal']}\n")
                f.write(f"Puesto: {candidate['puesto']}\n")
                f.write(f"Puntuación: {candidate['puntuacion']*100:.2f}/10\n")