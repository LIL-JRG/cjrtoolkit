import os
from typing import List, Dict
from cryptography.fernet import Fernet
import colorama
import logging
import logging.config

colorama.init()

# ============= PATHS AND VERSION =============
# Directorios base
SRC_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR: str = os.path.dirname(SRC_DIR)

# Leer versión del archivo
with open(os.path.join(SRC_DIR, 'system', 'ver.txt'), 'r') as f:
    LASTVERSION: str = f.read().strip()

# Directorios de recursos y assets
ASSETS_DIR: str = os.path.join(SRC_DIR, "assets")
KEY_FILE: str = os.path.join(ASSETS_DIR, "encryption_key.key")
COOKIES_FILE: str = os.path.join(ASSETS_DIR, "cookies.encrypted")

# Directorios de trabajo
CURRICULUMS_FOLDER: str = os.path.join(BASE_DIR, "Curriculums")
RESULT_FOLDER: str = os.path.join(BASE_DIR, "results")
CV_PROCESSOR_FOLDER: str = os.path.join(RESULT_FOLDER, "CV Processor")
CV_PROCESSOR_TOP3_FOLDER: str = os.path.join(CV_PROCESSOR_FOLDER, "Top 3")

# Directorios de trabajo internos
LOGS_DIR: str = os.path.join(SRC_DIR, "logs")

# Crear directorios si no existen
DIRS_TO_CREATE: list = [
    ASSETS_DIR,
    CURRICULUMS_FOLDER,
    RESULT_FOLDER,
    CV_PROCESSOR_FOLDER,
    CV_PROCESSOR_TOP3_FOLDER,
    LOGS_DIR
]

for dir_path in DIRS_TO_CREATE:
    os.makedirs(dir_path, exist_ok=True)

# ============= MENU CONFIGURATION =============
MENU_CONFIG: Dict = {
    'main_menu': [
        {'key': 'validar', 'name': 'Winda ID Validator', 'description': 'Validación de certificados Winda'},
        {'key': 'procesar', 'name': 'CV Processor', 'description': 'Procesamiento de currículums'},
        {'key': 'doc', 'name': 'DOC Utilities', 'description': 'Utilidades para documentos'},
        {'key': 'email_rewriter', 'name': 'Email Rewriter', 'description': 'Reescribe correos electrónicos'},
        {'key': 'sicaru_ia', 'name': 'Sicarú IA', 'description': 'Asistente de IA'},
        {'key': 'salir', 'name': 'Salir', 'description': 'Salir del programa'}
    ],
    'cv_processor_menu': {
        'title': 'Seleccione el puesto a buscar:',
        'style': {
            'frame': True,
            'align': 'left',
            'padding': 2
        },
        'categories': {
            'Oficina': [
                'administracion_finanzas',
                'control_proyectos',
                'gerente_administracion',
                'auxiliar_contable',
                'flotilla_vehicular',
                'almacen_compras',
                'recursos_humanos',
                'gerente_ventas',
                'ejecutivo_ventas',
                'gerente_alta_media_tension',
                'gerente_qshe',
                'coordinador_sgi',
                'coordinador_qshe',
                'gestor_documental',
                'gerente_oym',
                'coordinador_proyectos_norte',
                'licitaciones_norte',
                'coordinador_grandes_correctivos',
                'coordinador_proyectos_sur',
                'jefe_proyecto',
                'gerente_suministros_reparacion'
            ],
            'Técnicos': [
                'operacion_mantenimiento',
                'alta_media_tension',
                'reparacion_componentes',
                'reparacion_palas',
                'grandes_correctivos'
            ]
        },
        'footer': [
            'back'
        ]
    },
    'pdf_menu': [
        {'key': 'convert', 'name': 'Convertir PDF', 'description': 'Convierte archivos a PDF'},
        {'key': 'merge', 'name': 'Unir PDFs', 'description': 'Combina múltiples archivos PDF'},
        {'key': 'split', 'name': 'Dividir PDF', 'description': 'Divide un PDF en múltiples archivos'},
        {'key': 'back', 'name': 'Volver', 'description': 'Volver al menú principal'}
    ],
    'email_menu': [
        {'key': 'formal', 'name': 'Formal', 'description': 'Tono formal y profesional'},
        {'key': 'casual', 'name': 'Casual', 'description': 'Tono casual y amigable'},
        {'key': 'professional', 'name': 'Profesional', 'description': 'Tono profesional equilibrado'},
        {'key': 'back', 'name': 'Volver', 'description': 'Volver al menú principal'}
    ]
}

# ============= SYSTEM MESSAGES =============
MESSAGES: Dict = {
    'welcome': 'Bienvenido a CJR Toolkit',
    'goodbye': 'Gracias por usar CJR Toolkit. ¡Hasta luego!',
    'error': {
        'file_not_found': 'El archivo no fue encontrado',
        'invalid_input': 'Entrada inválida, por favor intente de nuevo',
        'api_error': 'Error en la conexión con la API',
        'conversion_error': 'Error durante la conversión del archivo',
        'permission_error': 'Error de permisos al acceder al archivo'
    },
    'success': {
        'file_converted': 'Archivo convertido exitosamente',
        'email_generated': 'Email generado exitosamente',
        'operation_complete': 'Operación completada con éxito'
    },
    'info': {
        'processing': 'Procesando su solicitud...',
        'please_wait': 'Por favor espere...',
        'enter_to_continue': 'Presione Enter para continuar...'
    }
}

# ============= AI CONFIGURATION =============

# AI Models Configuration
AI_CONFIG: Dict = {
    "gemini": {
        "model_name": "gemini-1.5-flash",
        "base_config": {
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        },
        "safety_settings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
    }
}

# Sicaru IA Configuration
SICARU_CONFIG: Dict = {
    **AI_CONFIG["gemini"],
    "temperature": 0.9,  # Higher temperature for more creative responses
    "max_history_length": 20,
    "initial_prompt": "Soy Sicarú, tu asistente personal. ¿En qué puedo ayudarte hoy?",
}

# Email Rewriter Configuration
EMAIL_REWRITER_CONFIG: Dict = {
    **AI_CONFIG["gemini"],
    "temperature": 0.7,  # Lower temperature for more formal responses
    "tones": {
        "formal": {
            "temperature": 0.6,
            "prompt": """Eres un redactor de correo electrónico profesional experto. Tu tarea es reescribir y EXPANDIR el texto dado en un tono FORMAL y profesional, mejorando significativamente su claridad, estructura y eficacia.

El texto debe:
1. Ser respetuoso y utilizar lenguaje corporativo apropiado
2. Mantener una distancia profesional adecuada
3. Incluir y EXPANDIR todos los detalles relevantes del mensaje original
4. Tener una estructura clara con saludo, introducción, cuerpo detallado y despedida formal
5. Usar frases completas y bien estructuradas
6. Incluir fórmulas de cortesía apropiadas
7. Mantener un tono asertivo pero respetuoso
8. Añadir contexto y detalles adicionales relevantes
9. Incluir seguimiento o pasos siguientes cuando sea apropiado

IMPORTANTE: El texto final debe ser significativamente más detallado y completo que el original. Expande la información proporcionada y añade contexto profesional relevante."""
        },
        "casual": {
            "temperature": 0.8,
            "prompt": """Eres un redactor de correo electrónico experto. Tu tarea es reescribir y EXPANDIR el texto dado en un tono CASUAL y amigable, haciéndolo más cercano y detallado.

El texto debe:
1. Ser cordial y natural, sin perder el profesionalismo
2. Usar un lenguaje claro y conversacional
3. Mantener un tono amigable pero respetuoso
4. Incluir y EXPANDIR todos los detalles relevantes del mensaje original
5. Tener una estructura clara pero relajada
6. Usar expresiones amigables y cercanas
7. Transmitir calidez y empatía
8. Añadir contexto personal cuando sea apropiado
9. Incluir detalles adicionales que mejoren la comunicación

IMPORTANTE: El texto final debe ser significativamente más detallado y personal que el original. Expande la información proporcionada y añade un toque humano y cercano."""
        },
        "professional": {
            "temperature": 0.7,
            "prompt": """Eres un redactor de correo electrónico profesional experto. Tu tarea es reescribir y EXPANDIR el texto dado en un tono PROFESIONAL y equilibrado, mejorando significativamente su eficacia comunicativa.

El texto debe:
1. Encontrar un balance perfecto entre formalidad y cercanía
2. Ser claro y completo, con detalles expandidos
3. Incluir y EXPANDIR todos los detalles relevantes del mensaje original
4. Tener una estructura clara y profesional con introducción, desarrollo y conclusión
5. Usar un lenguaje accesible pero refinado
6. Incluir fórmulas de cortesía apropiadas
7. Transmitir confianza y competencia
8. Añadir contexto y detalles adicionales relevantes
9. Proponer pasos siguientes o acciones concretas

IMPORTANTE: El texto final debe ser significativamente más detallado y completo que el original. Expande la información proporcionada y añade valor profesional al mensaje."""
        }
    },
    "max_cache_size": 100  # Maximum number of cached email rewrites
}

AI_CONFIG: Dict = {
    'sicaru': SICARU_CONFIG,
    'email_rewriter': EMAIL_REWRITER_CONFIG
}

# ============= UI CONFIGURATION =============
# Estilos para InquirerPy
INQUIRER_STYLE: Dict = {
    'qmark': '',  # Sin marcador de pregunta
    'answer': 'fg:#00c853 bold',  # Verde brillante para las respuestas
    'pointer': 'fg:#ff1744',  # Color rojo para el pointer
    'highlighted': 'fg:#00c853 bold',  # Verde brillante para elementos resaltados
    'selected': 'fg:#ff1744',  # Rojo para elementos seleccionados
    'separator': 'fg:#ff1744',  # Rojo para separadores
    'instruction': 'fg:#4caf50',  # Verde más suave para instrucciones
    'text': '',  # default
    'disabled': 'fg:#858585 italic'  # Gris para elementos deshabilitados
}

# Símbolos para la interfaz
UI_SYMBOLS: Dict = {
    'pointer': '    >',  # Símbolo para el pointer
    'separator': '─',  # Símbolo para separadores
    'bullet': '•'  # Símbolo para listas
}

# Colores para la interfaz con tema navideño
COLORS: Dict = {
    'primary': '#00c853',    # Verde brillante (árbol)
    'secondary': '#ff1744',  # Rojo brillante (adornos)
    'accent': '#ffd700',     # Dorado (estrella/luces)
    'text': '#ffffff',       # Blanco (nieve)
    'disabled': '#858585'    # Gris
}

# ============= FILE CONFIGURATION =============
FILE_CONFIG: Dict = {
    'allowed_extensions': {
        'pdf': ['.pdf'],
        'documents': ['.doc', '.docx', '.txt'],
        'images': ['.jpg', '.jpeg', '.png']
    },
    'max_file_size': 10 * 1024 * 1024,  # 10MB en bytes
    'temp_dir': os.getenv('TEMP') or os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Temp'),
    'log_dir': LOGS_DIR
}

# ============= VALIDATION RULES =============
VALIDATION_RULES: Dict = {
    'email': {
        'min_length': 3,
        'max_length': 1000,
        'required_elements': ['saludo', 'cuerpo', 'despedida'],
        'forbidden_words': ['spam', 'virus', 'hack']
    },
    'pdf': {
        'max_pages': 50,
        'allowed_languages': ['es', 'en'],
        'max_file_size_mb': 10
    },
    'general': {
        'max_retries': 3,
        'timeout_seconds': 30
    }
}

# ============= LOGGING CONFIGURATION =============
LOGGING_CONFIG: Dict = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'simple': {
            'format': '%(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'INFO'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'app.log'),
            'formatter': 'detailed',
            'level': 'DEBUG'
        }
    },
    'loggers': {
        'app': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True
        }
    }
}

# Configurar logging
logging.config.dictConfig(LOGGING_CONFIG)

# ============= CACHE CONFIGURATION =============
CACHE_CONFIG: Dict = {
    'enabled': True,
    'timeout': 3600,  # 1 hora
    'max_size': 100,  # Número máximo de items en cache
    'file_path': os.path.join(BASE_DIR, 'cache', 'app_cache.db'),
    'types': {
        'memory': {
            'enabled': True,
            'max_items': 1000
        },
        'disk': {
            'enabled': True,
            'max_size_mb': 100
        }
    }
}

# ============= ENCRYPTION =============
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

# ============= URLs =============
LOGIN_URL: str = os.getenv('LOGIN_URL', "https://winda.globalwindsafety.org/account/")
SEARCH_URL: str = os.getenv('SEARCH_URL', "https://winda.globalwindsafety.org/organisation/search-bulk-result")

# ============= APP SETTINGS =============
MAX_RETRY_ATTEMPTS: int = 3
CACHE_EXPIRATION_TIME: int = 3600

# ============= PDF CONVERTER CONFIGURATION =============
PDF_CONVERTER_CONFIG: Dict = {
    "supported_formats": {
        "input": [
            ("PDF files", "*.pdf"),
            ("Word files", "*.docx"),
            ("Excel files", "*.xlsx"),
            ("PowerPoint files", "*.pptx")
        ],
        "output": ["pdf", "docx", "xlsx", "pptx", "txt", "images"]
    },
    "image_settings": {
        "dpi": 300,
        "format": "PNG"
    },
    "table_settings": {
        "flavor": "lattice",
        "line_scale": 15
    }
}

from .keywords import (
    BLOCKED_PATTERNS, TITLES, COMMON_NAMES, PROFESSIONAL_KEYWORDS,
    SOFT_SKILLS, CERTIFICATIONS, LANGUAGES
)

# ============= CV PROCESSOR CONFIGURATION =============
CV_PROCESSOR_CONFIG: Dict = {
    "nlp_model": "es_core_news_sm",
    "blocked_patterns": BLOCKED_PATTERNS,
    "titles": TITLES,
    "common_names": COMMON_NAMES,
    "keywords": {
        "professional": PROFESSIONAL_KEYWORDS,
        "soft_skills": SOFT_SKILLS,
        "certifications": CERTIFICATIONS,
        "languages": LANGUAGES
    },
    "ocr_settings": {
        "language": "spa",
        "dpi": 300
    },
    "similarity_threshold": 0.8,
    "max_workers": 4,
    "max_score": 60,  # Puntaje mínimo para considerar un candidato apto
}

# ============= ASCII ART AND DISPLAY FUNCTIONS =============
def clear_screen():
    """Limpia la pantalla de la consola"""
    os.system('cls' if os.name == 'nt' else 'clear')

def set_console_title(title: str) -> None:
    """Establece el título de la consola"""
    if os.name == 'nt':  # Windows
        os.system(f'title {title}')

def center_text(text, width):
    return '\n'.join(line.center(width) for line in text.split('\n'))

def hex_to_rgb(hex_color):
    return tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))

def rgb_to_ansi(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"

def interpolate_color(color1, color2, factor: float):
    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)
    r = int(r1 + factor * (r2 - r1))
    g = int(g1 + factor * (g2 - g1))
    b = int(b1 + factor * (b2 - b1))
    return f"#{r:02x}{g:02x}{b:02x}"

def color_gradient(text, start_color, end_color, mid_colors):
    lines = text.split('\n')
    total_lines = len(lines)
    colored_lines = []

    for i, line in enumerate(lines):
        if i == 0:
            color = start_color
        elif i == total_lines - 1:
            color = end_color
        else:
            progress = i / (total_lines - 1)
            if progress < 0.33:
                color = interpolate_color(start_color, mid_colors[0], progress * 3)
            elif progress < 0.66:
                color = interpolate_color(mid_colors[0], mid_colors[1], (progress - 0.33) * 3)
            else:
                color = interpolate_color(mid_colors[1], end_color, (progress - 0.66) * 3)
        
        r, g, b = hex_to_rgb(color)
        colored_lines.append(f"{rgb_to_ansi(r, g, b)}{line}\033[0m")

    return '\n'.join(colored_lines)

def Ascii_logo():
    terminal_width = os.get_terminal_size().columns
    centered_ascii_art = center_text(ASCII_ART.format(LASTVERSION=LASTVERSION), terminal_width)
    colored_ascii_art = color_gradient(centered_ascii_art, '#ffffff', '#ff9100', ['#ff0000', '#5eff00'])
    print(colored_ascii_art)

ASCII_ART: str = """

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