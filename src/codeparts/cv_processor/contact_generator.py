"""
Generador de enlaces de WhatsApp para contacto
"""

import re
import urllib.parse
import requests

def _generate_short_url(long_url: str) -> str:
    """
    Genera una URL corta usando TinyURL
    """
    try:
        response = requests.get(f'http://tinyurl.com/api-create.php?url={long_url}')
        if response.status_code == 200:
            return response.text.strip()
        return long_url
    except:
        return long_url

def generate_whatsapp_link(telefono: str, recruiter_name: str = "Recursos Humanos", nombre: str = "Candidato") -> str:
    """
    Genera un enlace corto de WhatsApp con un mensaje predefinido
    """
    # Limpiar teléfono
    telefono = ''.join(filter(str.isdigit, telefono))
    if not telefono:
        return "No disponible"
        
    # Si el teléfono no comienza con +, agregar código de país
    if not telefono.startswith('+'):
        telefono = '+52' + telefono
        
    # Mensaje predefinido
    mensaje = f"Hola {nombre}, soy {recruiter_name} de la empresa. ¿Podríamos agendar una entrevista?"
    
    # Generar enlace
    url = f"https://wa.me/{telefono}?text={urllib.parse.quote(mensaje)}"
    
    # Acortar enlace usando tinyurl
    try:
        response = requests.get(f'http://tinyurl.com/api-create.php?url={url}')
        if response.status_code == 200:
            return response.text
    except:
        pass
        
    return url
