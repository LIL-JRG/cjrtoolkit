import os
import re
import logging
import shutil
import asyncio
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from pdf2image import convert_from_path
import pytesseract
from system.config import RESULT_FOLDER

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
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group() if match else "Correo no encontrado"
    
    @staticmethod
    def extract_text_from_pdf(filepath: str) -> str:
        try:
            pages = convert_from_path(filepath)
        except Exception as e:
            logging.error(f"Error al convertir PDF: {e}")
            return ""
    
        def process_page(page):
            return pytesseract.image_to_string(page)
    
        with ThreadPoolExecutor() as executor:
            results = executor.map(process_page, pages)
    
        return "\n".join(f"\n--- Página {page_num} ---\n{page_text}" for page_num, page_text in enumerate(results, start=1))
    
    @classmethod
    async def process_cv(cls, folder: str, tipo_personal: str):
        now = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        resultado_folder = os.path.join(RESULT_FOLDER, f"{now}-CV-Sorter")
        os.makedirs(resultado_folder, exist_ok=True)
    
        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)
    
            if filename.endswith('.pdf'):
                text = await asyncio.to_thread(cls.extract_text_from_pdf, filepath)
            else:
                logging.warning(f"Archivo no soportado: {filename}")
                continue
    
            if tipo_personal == "Campo" and cls.filter_keywords_campo(text):
                await cls.process_candidate(text, resultado_folder, filename, "Campo")
            elif tipo_personal == "Oficina" and cls.filter_keywords_oficina(text):
                await cls.process_candidate(text, resultado_folder, filename, "Oficina")
    
    @staticmethod
    def filter_keywords_campo(text: str) -> bool:
        keywords = ['curso gwo', 'trabajos en altura', 'extinción de incendios', 'certificación BST', 'BSTR', 'Tecnico', 'Técnico', 'Especialista']
        return any(keyword.lower() in text.lower() for keyword in keywords)
    
    @staticmethod
    def filter_keywords_oficina(text: str) -> bool:
        keywords = ['administrador', 'administrador', 'contador', 'contadora', 'recepcionista', 'Recursos humanos', 'Licenciado', 'Licenciada', 'Lic.', 'Asistente']
        return any(keyword.lower() in text.lower() for keyword in keywords)
    
    @classmethod
    async def process_candidate(cls, text: str, resultado_folder: str, filename: str, tipo_personal: str):
        nombre = cls.extract_name(text)
        telefono = cls.extract_phone(text)
        correo = cls.extract_email(text)
    
        nombre_completo = nombre.replace(' ', '_')
    
        candidate_folder = os.path.join(resultado_folder, nombre_completo)
        os.makedirs(candidate_folder, exist_ok=True)
    
        new_filepath = os.path.join(candidate_folder, filename)
        await asyncio.to_thread(shutil.copy2, os.path.join('Curriculums', filename), new_filepath)
    
        whatsapp_link = f"https://api.whatsapp.com/send/?phone={telefono}&text=Hola {nombre_completo}, hemos recibido tu CV&type=phone_number&app_absent=0" if telefono != "Teléfono no encontrado" else "No disponible"
    
        txt_filename = f"{tipo_personal}_Candidato_{nombre_completo}.txt"
        with open(os.path.join(candidate_folder, txt_filename), 'w') as f:
            f.write(f"Nombre completo: {nombre}\n")
            f.write(f"Número de teléfono: {telefono}\n")
            f.write(f"Correo electrónico: {correo}\n")
            f.write(f"WhatsApp: {whatsapp_link}\n")
    
        logging.info(f"Nombre completo: {nombre}")
        logging.info(f"Número de teléfono: {telefono}")
        logging.info(f"Correo electrónico: {correo}")
        logging.info(f"Contacto: {whatsapp_link}\n")