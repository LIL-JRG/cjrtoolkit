import os
from typing import List
from cryptography.fernet import Fernet

BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(BASE_DIR, 'system', 'ver.txt'), 'r') as f:
    LASTVERSION: str = f.read().strip()

ASSETS_DIR: str = os.path.join(BASE_DIR, "assets")
KEY_FILE: str = os.path.join(ASSETS_DIR, "encryption_key.key")
COOKIES_FILE: str = os.path.join(ASSETS_DIR, "cookies.encrypted")
RESULT_FOLDER: str = os.path.join(BASE_DIR, '..', 'results')

OPENAI_API_KEY = "Your_Api_Key"

def get_or_create_key() -> bytes:
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
    else:
        with open(KEY_FILE, "rb") as key_file:
            key = key_file.read()
    return key

COOKIE_ENCRYPTION_KEY: bytes = get_or_create_key()

LOGIN_URL: str = os.getenv('LOGIN_URL', "https://winda.globalwindsafety.org/account/")
SEARCH_URL: str = os.getenv('SEARCH_URL', "https://winda.globalwindsafety.org/organisation/search-bulk-result")

MAX_RETRY_ATTEMPTS: int = 3
CACHE_EXPIRATION_TIME: int = 3600

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ASCII_ART: str = f"""

                     ██████╗     ██╗██████╗                    
                    ██╔════╝     ██║██╔══██╗                   
                    ██║          ██║██████╔╝                   
                    ██║     ██   ██║██╔══██╗                   
                    ╚██████╗╚█████╔╝██║  ██║                   
                     ╚═════╝ ╚════╝ ╚═╝  ╚═╝                   
                                                       
████████╗ ██████╗  ██████╗ ██╗     ██╗  ██╗██╗████████╗
╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██║ ██╔╝██║╚══██╔══╝
   ██║   ██║   ██║██║   ██║██║     █████╔╝ ██║   ██║   
   ██║   ██║   ██║██║   ██║██║     ██╔═██╗ ██║   ██║   
   ██║   ╚██████╔╝╚██████╔╝███████╗██║  ██╗██║   ██║   
   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝   ╚═╝    
   v{LASTVERSION}   
"""

KEYWORDS_CAMPO: List[str] = [
    'curso gwo', 'trabajos en altura', 'extinción de incendios', 
    'certificación BST', 'BSTR', 'Tecnico', 'Técnico', 'Especialista'
]

KEYWORDS_OFICINA: List[str] = [
    'administrador', 'administradora', 'contador', 'contadora', 
    'recepcionista', 'Recursos humanos', 'Licenciado', 'Licenciada', 
    'Lic.', 'Asistente'
]

