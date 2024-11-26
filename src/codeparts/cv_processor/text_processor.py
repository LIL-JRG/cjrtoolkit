import re
import spacy
from typing import Set
from system.config import CV_PROCESSOR_CONFIG

class TextProcessor:
    def __init__(self):
        self.nlp = spacy.load(CV_PROCESSOR_CONFIG["nlp_model"])
        self.blocked_patterns = CV_PROCESSOR_CONFIG["blocked_patterns"]
        self.titles = CV_PROCESSOR_CONFIG["titles"]
        self.common_names = CV_PROCESSOR_CONFIG["common_names"]
        
        # Keywords profesionales por área
        self.professional_keywords = {
            'administración': ['gestión', 'administración', 'finanzas', 'contabilidad', 'recursos_humanos', 'marketing'],
            'tecnología': ['programación', 'desarrollo', 'software', 'sistemas', 'redes', 'bases_de_datos'],
            'ventas': ['ventas', 'comercial', 'atención_al_cliente', 'servicio_al_cliente', 'retail'],
            'ingeniería': ['industrial', 'mecánica', 'eléctrica', 'civil', 'química'],
            'educación': ['profesor', 'docente', 'tutor', 'enseñanza', 'pedagogía'],
            'salud': ['médico', 'enfermería', 'psicología', 'nutrición', 'farmacia']
        }
        
        # Habilidades blandas comunes
        self.soft_skills = [
            'liderazgo', 'trabajo_en_equipo', 'comunicación', 'organización', 
            'resolución_de_problemas', 'adaptabilidad', 'creatividad', 'proactividad',
            'responsabilidad', 'puntualidad', 'empatía', 'flexibilidad'
        ]
        
        # Certificaciones por área
        self.certifications = {
            'tecnología': ['CCNA', 'AWS', 'Azure', 'CompTIA', 'MCSE', 'PMP'],
            'finanzas': ['CFA', 'CPA', 'ACCA', 'FRM'],
            'ingeniería': ['PE', 'FE', 'PMP', 'Six Sigma'],
            'marketing': ['Google Analytics', 'HubSpot', 'Facebook Blueprint'],
            'idiomas': ['TOEFL', 'IELTS', 'Cambridge', 'DELF', 'DELE']
        }
        
        # Idiomas comunes
        self.languages = [
            'inglés', 'español', 'francés', 'alemán', 'italiano', 
            'portugués', 'chino', 'japonés', 'coreano'
        ]

    def clean_text(self, text: str) -> str:
        """Limpia el texto eliminando caracteres especiales y normalizando espacios"""
        # Convertir a minúsculas
        text = text.lower()
        
        # Eliminar caracteres especiales pero mantener letras acentuadas
        text = re.sub(r'[^a-záéíóúñü\s]', ' ', text)
        
        # Normalizar espacios
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()

    def remove_blocked_patterns(self, text: str) -> str:
        """Elimina patrones bloqueados del texto"""
        for pattern in self.blocked_patterns:
            text = re.sub(r'\b' + re.escape(pattern) + r'\b', '', text, flags=re.IGNORECASE)
        return text

    def remove_common_names(self, text: str) -> str:
        """Elimina nombres comunes del texto"""
        for name in self.common_names:
            text = re.sub(r'\b' + re.escape(name) + r'\b', '', text, flags=re.IGNORECASE)
        return text

    def remove_titles(self, text: str) -> str:
        """Elimina títulos académicos y profesionales del texto"""
        for title in self.titles:
            text = re.sub(r'\b' + re.escape(title) + r'\b\.?', '', text, flags=re.IGNORECASE)
        return text

    def process_text(self, text: str) -> str:
        """Procesa el texto aplicando todas las transformaciones necesarias"""
        text = self.clean_text(text)
        text = self.remove_blocked_patterns(text)
        text = self.remove_common_names(text)
        text = self.remove_titles(text)
        text = re.sub(r'\s+', ' ', text)  # Normalizar espacios nuevamente
        return text.strip()

    def extract_keywords(self, text: str) -> dict:
        """Extrae keywords profesionales del texto."""
        if not text:
            return {}
        
        text = self.process_text(text)
        found_keywords = {}
        
        for area, keywords in self.professional_keywords.items():
            found = []
            for keyword in keywords:
                if keyword.lower() in text:
                    found.append(keyword)
            if found:
                found_keywords[area] = found
        
        return found_keywords

    def extract_soft_skills(self, text: str) -> list:
        """Extrae habilidades blandas del texto."""
        if not text:
            return []
        
        text = self.process_text(text)
        found_skills = []
        
        for skill in self.soft_skills:
            if skill.lower() in text:
                found_skills.append(skill)
        
        return found_skills

    def extract_certifications(self, text: str) -> dict:
        """Extrae certificaciones del texto."""
        if not text:
            return {}
        
        text = self.process_text(text)
        found_certs = {}
        
        for area, certs in self.certifications.items():
            found = []
            for cert in certs:
                if cert.lower() in text:
                    found.append(cert)
            if found:
                found_certs[area] = found
        
        return found_certs

    def extract_languages(self, text: str) -> dict:
        """Extrae idiomas del texto."""
        if not text:
            return {}
        
        text = self.process_text(text)
        found_languages = {}
        
        for lang in self.languages:
            if lang.lower() in text:
                # Por ahora solo marcamos como "encontrado"
                found_languages[lang] = "no especificado"
        
        return found_languages
