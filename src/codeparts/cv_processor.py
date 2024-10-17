import os
import re
import logging
import shutil
import asyncio
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional, Dict
from pdf2image import convert_from_path
import pytesseract
from system.config import RESULT_FOLDER, KEYWORDS_CAMPO, KEYWORDS_OFICINA

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
        name_pattern = r"\b([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?: [A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)?)(?: [A-ZÁÉÍÓÚÑ][a-záéíóúñ]+\b| [A-ZÁÉÍÓÚÑ]\.| [A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?: [A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)?)\b"
        match = re.search(name_pattern, text)
        return match.group() if match else "Nombre no encontrado"
    
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
    async def process_cv(cls, folder: str, tipo_personal: str) -> None:
        now = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        resultado_folder = os.path.join(RESULT_FOLDER, f"{now}-CV-Sorter")
        os.makedirs(resultado_folder, exist_ok=True)
    
        tasks = [
            cls.process_file(os.path.join(folder, filename), resultado_folder, tipo_personal)
            for filename in os.listdir(folder)
            if filename.endswith('.pdf')
        ]
    
        await asyncio.gather(*tasks)
    
    @classmethod
    async def process_file(cls, filepath: str, resultado_folder: str, tipo_personal: str) -> None:
        text = await cls.extract_text_from_pdf(filepath)
        
        keywords = KEYWORDS_CAMPO if tipo_personal == "Campo" else KEYWORDS_OFICINA
        if cls.filter_keywords(text, keywords):
            await cls.process_candidate(text, resultado_folder, os.path.basename(filepath), tipo_personal)
    
    @staticmethod
    def filter_keywords(text: str, keywords: List[str]) -> bool:
        return any(keyword.lower() in text.lower() for keyword in keywords)
    
    @classmethod
    @log_method
    async def process_candidate(cls, text: str, resultado_folder: str, filename: str, tipo_personal: str) -> None:
        candidate_info = {
            "nombre": cls.extract_name(text),
            "telefono": cls.extract_phone(text),
            "correo": cls.extract_email(text)
        }
    
        nombre_completo = candidate_info["nombre"].replace(' ', '_')
        candidate_folder = os.path.join(resultado_folder, candidate_info["nombre"])
        os.makedirs(candidate_folder, exist_ok=True)
    
        new_filepath = os.path.join(candidate_folder, filename)
        await asyncio.to_thread(shutil.copy2, os.path.join('../Curriculums', filename), new_filepath)
    
        whatsapp_link = (f"https://api.whatsapp.com/send/?phone={candidate_info['telefono']}&"
                         f"text=Hola_{candidate_info['nombre']},_hemos recibido tu CV&type=phone_number&app_absent=0"
                         if candidate_info['telefono'] != "Teléfono no encontrado" else "No disponible")
    
        txt_filename = f"{tipo_personal}_Candidato_{nombre_completo}.txt"
        with open(os.path.join(candidate_folder, txt_filename), 'w') as f:
            f.write(f"Nombre completo: {candidate_info['nombre']}\n")
            f.write(f"Número de teléfono: {candidate_info['telefono']}\n")
            f.write(f"Correo electrónico: {candidate_info['correo']}\n")
            f.write(f"WhatsApp: {whatsapp_link}\n")
    
        logging.info(f"Procesado candidato: {candidate_info['nombre']}")