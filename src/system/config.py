import os
from cryptography.fernet import Fernet

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(BASE_DIR, 'system', 'ver.txt'), 'r') as f:
    LASTVERSION = f.read().strip()

# Generar una clave de encriptación persistente
KEY_FILE = os.path.join(BASE_DIR, "assets", "encryption_key.key")
if not os.path.exists(KEY_FILE):
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)
else:
    with open(KEY_FILE, "rb") as key_file:
        key = key_file.read()

COOKIE_ENCRYPTION_KEY = key
COOKIES_FILE = os.path.join(BASE_DIR, "assets", "cookies.encrypted")
LOGIN_URL = "https://winda.globalwindsafety.org/account/"
SEARCH_URL = "https://winda.globalwindsafety.org/organisation/search-bulk-result"
MAX_RETRY_ATTEMPTS = 3
CACHE_EXPIRATION_TIME = 3600  # 1 hora
RESULT_FOLDER = os.path.join(BASE_DIR, 'Resultados')

# Logging configuration
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ASCII Art
ASCII_ART = f"""

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