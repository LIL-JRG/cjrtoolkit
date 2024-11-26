from typing import Dict, List
from system.config import CV_PROCESSOR_CONFIG

def analyze_professional_keywords(text: str) -> Dict:
    """Analiza las palabras clave profesionales en el texto"""
    results = {}
    keywords = CV_PROCESSOR_CONFIG["keywords"]["professional"]
    
    for area, subareas in keywords.items():
        area_matches = {}
        for subarea, keywords in subareas.items():
            matches = [kw for kw in keywords if kw.lower() in text.lower()]
            if matches:
                area_matches[subarea] = matches
        if area_matches:
            results[area] = area_matches
    return results

def analyze_soft_skills(text: str) -> List[str]:
    """Analiza las habilidades blandas en el texto"""
    skills = CV_PROCESSOR_CONFIG["keywords"]["soft_skills"]
    return [skill for skill in skills if skill.lower() in text.lower()]

def analyze_certifications(text: str) -> Dict[str, List[str]]:
    """Analiza las certificaciones en el texto"""
    results = {}
    certifications = CV_PROCESSOR_CONFIG["keywords"]["certifications"]
    
    for area, certs in certifications.items():
        matches = [cert for cert in certs if cert.upper() in text.upper()]
        if matches:
            results[area] = matches
    return results

def analyze_languages(text: str) -> Dict[str, str]:
    """Analiza los idiomas y sus niveles en el texto"""
    results = {}
    languages = CV_PROCESSOR_CONFIG["keywords"]["languages"]
    
    for lang in languages["idiomas"]:
        if lang.lower() in text.lower():
            # Buscar el nivel del idioma
            for nivel in languages["niveles"]:
                if nivel.lower() in text.lower():
                    results[lang] = nivel
                    break
            if lang not in results:
                results[lang] = "no especificado"
    return results
