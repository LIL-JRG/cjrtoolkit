import os
import re
import logging
import shutil
import spacy
from typing import List, Set
import asyncio
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional, Dict
from pdf2image import convert_from_path
import pytesseract
from system.config import RESULT_FOLDER
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
    nlp = spacy.load("es_core_news_sm")

    blocked_patterns: Set[str] = {
        "estudio", "bilingtie", "analista", "calle", "avenida", "experiencia laboral",
        "idioma", "inglés", "español", "francés", "alemán", "curriculum vitae", "cv",
        "teléfono", "email", "correo", "electrónico", "dirección", "código postal",
        "educación", "formación", "habilidades", "competencias", "referencias",
        "cualquier", "lugar", "nivel", "oral", "escrito", "avanzado", "intermedio", "básico"
    }

    titles: Set[str] = {"lic", "licenciado", "licenciada", "ing", "ingeniero", "ingeniera", 
                        "prof", "profesor", "profesora", "dr", "doctor", "doctora", 
                        "mtro", "maestro", "maestra"}

    common_names: Set[str] = { "juan", "pablo", "francisco", "amelia", "ocampo", "mercado", "jose", "julián", "josé", "maría", "guadalupe", "carlos", "fernando", "alejandro", "sofia", "valentina", "isabella","martínez", "gonzález", "rodríguez", "lópez", "pérez", "sánchez", "ramírez", "cruz", "hernández", "garcía", "morales", "ortega", "vázquez", "mendoza", "castillo", "jiménez", "torres", "flores", "ramos", "reyes", "gutiérrez", "chávez", "márquez", "domínguez","cervantes", "villanueva", "montes", "escalante", "quintana", "salazar", "valenzuela", "aguilar", "navarro", "padilla", "santana", "treviño", "uribe", "zavala", "ibarra", "maldonado", "pacheco", "santiago", "valdez", "zúñiga", "bautista", "carrillo", "delgado", "espinoza", "figueroa", "gallegos", "huerta", "ibáñez", "juárez", "luna", "medina", "nieto", "olivares", "pineda", "quiroz", "rosales", "sosa", "tapia", "urías", "villalobos", "xochitl", "yáñez", "zárate", "álvarez", "barrera", "camarillo", "díaz", "estrada", "fuentes", "gómez", "hidalgo", "izquierdo", "jara", "kuri", "lara", "mármol", "nava", "ojeda", "pinedo", "quintanilla", "rangel", "serrano", "téllez", "urbina", "villaseñor", "wenceslao", "xicoténcatl", "yolanda", "zapata", "ángel", "baltazar", "candelaria", "delfina", "eulalia", "feliciano", "gregorio", "heriberto", "ignacio", "jovita", "karen", "leonardo", "marcelino", "nicolás", "octavio", "patricia", "quintín", "rosario", "santos", "teodoro", "ulises", "vicente", "wilfrido", "ximena", "yadira", "zulema", "viviana", "mariano", "martín", "gael", "miguel", "vazques", "diana"}

    @staticmethod
    def is_valid_name(name: str) -> bool:

        name_lower = name.lower()

        if any(pattern in name_lower for pattern in CVProcessor.blocked_patterns):
            return False
        
        name_parts = name.split()
        if len(name_parts) < 2:
            return False
        
        if len(name) > 50:
            return False
        
        if not all(part.istitle() for part in name_parts):
            return False
        
        if not any(part.lower() in CVProcessor.common_names for part in name_parts):
            return False
        
        return True

    @staticmethod
    def remove_titles(name: str) -> str:
        name_parts = name.split()
        while name_parts and name_parts[0].lower().rstrip('.') in CVProcessor.titles:
            name_parts.pop(0)
        return " ".join(name_parts)

    @staticmethod
    def extract_name(text: str) -> str:
        doc = CVProcessor.nlp(text)
        names = [CVProcessor.remove_titles(ent.text) for ent in doc.ents if ent.label_ == "PER"]
        valid_names = [name for name in names if CVProcessor.is_valid_name(name)]
        
        if valid_names:
            return max(valid_names, key=len)
        
        name_pattern = r"\b(?:(?:Lic|Ing|Prof|Dr|Mtro)\.?\s+)?([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){1,3})\b"
        matches = re.finditer(name_pattern, text)
        for match in matches:
            name = match.group(1)
            if CVProcessor.is_valid_name(name):
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
        candidates = [c for c in candidates if c]
        
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
                "recepcionista": [
                    "recepción",
                    "atención al cliente",
                    "agenda",
                    "llamadas",
                    "organización",
                    "gestión de visitas",
                    "manejo de centralita telefónica",
                    "correspondencia",
                    "gestión de correo electrónico",
                    "software de oficina",
                    "Microsoft Office",
                    "habilidades de comunicación",
                    "resolución de problemas",
                    "multitarea",
                    "protocolo empresarial",
                    "gestión del tiempo",
                    "confidencialidad",
                    "atención al detalle",
                    "gestión de conflictos",
                    "idiomas",
                    "primeros auxilios",
                    "seguridad en oficina",
                    "manejo de quejas",
                    "gestión de reservas",
                    "organización de eventos",
                    "archivo y documentación",
                    "gestión de suministros de oficina",
                    "software de gestión de visitantes",
                    "etiqueta telefónica",
                    "redacción de correos electrónicos",
                    "gestión de calendarios",
                    "coordinación de reuniones",
                    "manejo de equipos de oficina",
                    "servicio al cliente",
                    "adaptabilidad",
                    "trabajo en equipo",
                    "gestión del estrés",
                    "presentación personal",
                    "conocimientos básicos de IT",
                    "gestión de redes sociales",
                ],
                "administrador": [
                    "administración",
                    "gestión",
                    "finanzas",
                    "recursos",
                    "planificación",
                    "presupuestos",
                    "análisis financiero",
                    "gestión de proyectos",
                    "recursos humanos",
                    "contratación",
                    "evaluación de desempeño",
                    "gestión de proveedores",
                    "negociación de contratos",
                    "optimización de procesos",
                    "análisis de datos",
                    "toma de decisiones",
                    "gestión de riesgos",
                    "cumplimiento normativo",
                    "software ERP",
                    "SAP",
                    "Microsoft Excel avanzado",
                    "Power BI",
                    "gestión de activos",
                    "control de costos",
                    "auditoría interna",
                    "gestión de la calidad",
                    "ISO 9001",
                    "lean management",
                    "Six Sigma",
                    "gestión del cambio",
                    "liderazgo de equipos",
                    "comunicación efectiva",
                    "resolución de problemas",
                    "pensamiento estratégico",
                    "gestión de crisis",
                    "desarrollo organizacional",
                    "gestión de la cadena de suministro",
                    "análisis de mercado",
                    "planificación estratégica",
                    "gestión de la innovación",
                ],
                "gerente": [
                    "liderazgo",
                    "estrategia",
                    "gestión de equipos",
                    "toma de decisiones",
                    "objetivos",
                    "visión empresarial",
                    "planificación estratégica",
                    "gestión del cambio",
                    "desarrollo de negocios",
                    "negociación",
                    "gestión financiera",
                    "análisis de mercado",
                    "gestión de crisis",
                    "motivación de equipos",
                    "resolución de conflictos",
                    "comunicación ejecutiva",
                    "presentaciones de alto nivel",
                    "networking",
                    "innovación",
                    "gestión de proyectos",
                    "KPIs",
                    "balanced scorecard",
                    "gestión de stakeholders",
                    "responsabilidad social corporativa",
                    "ética empresarial",
                    "gestión de la calidad total",
                    "desarrollo de talento",
                    "coaching ejecutivo",
                    "gestión del rendimiento",
                    "análisis competitivo",
                    "fusiones y adquisiciones",
                    "expansión de mercado",
                    "gestión de riesgos empresariales",
                    "transformación digital",
                    "gestión de la innovación",
                    "pensamiento sistémico",
                    "inteligencia emocional",
                    "gestión del conocimiento",
                    "sostenibilidad empresarial",
                    "liderazgo adaptativo",
                ],
                "supervisor": [
                    "supervisión",
                    "control de calidad",
                    "coordinación",
                    "reportes",
                    "mejora continua",
                    "gestión de equipos",
                    "evaluación de desempeño",
                    "formación de personal",
                    "resolución de problemas",
                    "planificación de turnos",
                    "gestión de conflictos",
                    "implementación de políticas",
                    "seguridad laboral",
                    "optimización de procesos",
                    "KPIs operativos",
                    "lean management",
                    "Six Sigma",
                    "gestión de proyectos",
                    "comunicación efectiva",
                    "liderazgo situacional",
                    "motivación de equipos",
                    "gestión del tiempo",
                    "análisis de productividad",
                    "control de costos",
                    "gestión de inventarios",
                    "mantenimiento preventivo",
                    "auditorías internas",
                    "cumplimiento normativo",
                    "gestión de la calidad",
                    "ISO 9001",
                    "salud y seguridad ocupacional",
                    "gestión del cambio",
                    "mejora de procesos",
                    "análisis de datos operativos",
                    "toma de decisiones",
                    "gestión de crisis",
                    "trabajo en equipo",
                    "desarrollo de habilidades",
                    "feedback constructivo",
                    "gestión de estrés",
                ],
                "contador": [
                    "contabilidad",
                    "finanzas",
                    "impuestos",
                    "auditoría",
                    "estados financieros",
                    "normativa contable",
                    "NIIF",
                    "análisis financiero",
                    "presupuestos",
                    "control de costos",
                    "conciliaciones bancarias",
                    "gestión de tesorería",
                    "planificación fiscal",
                    "software contable",
                    "SAP",
                    "Excel avanzado",
                    "auditoría interna",
                    "gestión de riesgos financieros",
                    "reporting financiero",
                    "consolidación de cuentas",
                    "contabilidad de costes",
                    "análisis de desviaciones",
                    "flujo de caja",
                    "valoración de empresas",
                    "due diligence",
                    "control interno",
                    "cumplimiento normativo",
                    "gestión de activos fijos",
                    "contabilidad de gestión",
                    "análisis de rentabilidad",
                    "optimización fiscal",
                    "auditoría externa",
                    "PCGA",
                    "sistemas ERP",
                    "gestión de cuentas por cobrar y pagar",
                    "cierre contable",
                    "informes para la dirección",
                    "análisis de inversiones",
                    "contabilidad de costos ABC",
                    "ética profesional contable",
                ],
                "auxiliar_recepcionista": [
                    "apoyo",
                    "atención",
                    "organización",
                    "comunicación",
                    "multitarea",
                    "gestión de llamadas",
                    "manejo de agenda",
                    "atención al cliente",
                    "correspondencia",
                    "archivo de documentos",
                    "software de oficina",
                    "Microsoft Office",
                    "gestión de correo electrónico",
                    "organización de reuniones",
                    "gestión de suministros de oficina",
                    "protocolo empresarial",
                    "habilidades interpersonales",
                    "manejo de centralita telefónica",
                    "gestión de visitas",
                    "redacción básica",
                    "confidencialidad",
                    "trabajo en equipo",
                    "adaptabilidad",
                    "resolución de problemas",
                    "atención al detalle",
                    "gestión del tiempo",
                    "manejo de equipos de oficina",
                    "conocimientos básicos de IT",
                    "etiqueta telefónica",
                    "servicio al cliente",
                    "gestión de redes sociales básica",
                    "organización de eventos pequeños",
                    "manejo de quejas básico",
                    "primeros auxilios básicos",
                    "seguridad en oficina",
                    "idiomas básicos",
                    "presentación personal",
                    "gestión de calendarios",
                    "entrada de datos",
                    "habilidades de escucha activa",
                ],
                "auxiliar_administrador": [
                    "apoyo administrativo",
                    "archivo",
                    "datos",
                    "reportes",
                    "correspondencia",
                    "entrada de datos",
                    "gestión de documentos",
                    "organización de archivos",
                    "software de oficina",
                    "Microsoft Office",
                    "Excel intermedio",
                    "gestión de bases de datos",
                    "atención al cliente interno",
                    "gestión de agenda",
                    "organización de reuniones",
                    "preparación de informes básicos",
                    "gestión de suministros",
                    "facturación",
                    "gestión de pagos",
                    "conciliaciones bancarias básicas",
                    "apoyo en contratación",
                    "mantenimiento de registros",
                    "gestión de correo electrónico",
                    "atención telefónica",
                    "gestión de viajes corporativos",
                    "organización de eventos",
                    "apoyo en presupuestos",
                    "gestión de proveedores",
                    "control de gastos",
                    "gestión de inventario de oficina",
                    "apoyo en recursos humanos",
                    "gestión de tiempo y asistencia",
                    "preparación de presentaciones",
                    "manejo de software ERP básico",
                    "cumplimiento normativo básico",
                    "gestión de riesgos básica",
                    "apoyo en auditorías",
                    "gestión de proyectos básica",
                    "habilidades de comunicación escrita",
                    "confidencialidad y ética profesional",
                ],
                "auxiliar_gerente": [
                    "apoyo gerencial",
                    "agenda",
                    "reuniones",
                    "presentaciones",
                    "informes",
                    "gestión de correo electrónico ejecutivo",
                    "organización de viajes ejecutivos",
                    "preparación de documentos ejecutivos",
                    "gestión de agenda de alto nivel",
                    "coordinación de reuniones de directorio",
                    "toma de actas",
                    "seguimiento de tareas ejecutivas",
                    "investigación y análisis básico",
                    "preparación de presentaciones ejecutivas",
                    "manejo de información confidencial",
                    "protocolo empresarial",
                    "comunicación con stakeholders",
                    "gestión de proyectos básica",
                    "software de oficina avanzado",
                    "Microsoft Office avanzado",
                    "gestión de redes sociales corporativas",
                    "organización de eventos corporativos",
                    "apoyo en la toma de decisiones",
                    "filtrado de información",
                    "redacción de informes ejecutivos",
                    "gestión de crisis básica",
                    "habilidades de networking",
                    "manejo de CRM",
                    "análisis de datos básico",
                    "gestión de presupuestos básica",
                    "coordinación interdepartamental",
                    "gestión de la comunicación interna",
                    "apoyo en planificación estratégica",
                    "seguimiento de KPIs",
                    "preparación de reportes de gestión",
                    "gestión de la imagen corporativa",
                    "apoyo en relaciones públicas",
                    "gestión de la innovación básica",
                    "inteligencia emocional",
                    "resolución de problemas ejecutivos",
                ],
                "auxiliar_supervisor": [
                    "apoyo en supervisión",
                    "seguimiento",
                    "reportes",
                    "control",
                    "asistencia",
                    "apoyo en gestión de equipos",
                    "monitoreo de KPIs",
                    "recopilación de datos operativos",
                    "elaboración de informes de desempeño",
                    "apoyo en evaluaciones de personal",
                    "seguimiento de objetivos",
                    "control de calidad básico",
                    "apoyo en formación de personal",
                    "gestión de turnos",
                    "mantenimiento de registros de producción",
                    "apoyo en resolución de conflictos",
                    "comunicación interdepartamental",
                    "seguimiento de procedimientos",
                    "apoyo en implementación de políticas",
                    "gestión de inventario básica",
                    "control de asistencia y puntualidad",
                    "apoyo en seguridad laboral",
                    "mantenimiento de documentación",
                    "apoyo en auditorías internas",
                    "seguimiento de mejora continua",
                    "recopilación de feedback de empleados",
                    "apoyo en gestión de proyectos",
                    "uso de software de gestión",
                    "Excel avanzado",
                    "análisis de datos básico",
                    "apoyo en optimización de procesos",
                    "seguimiento de mantenimiento preventivo",
                    "coordinación de reuniones de equipo",
                    "apoyo en gestión del cambio",
                    "seguimiento de cumplimiento normativo",
                    "apoyo en control de costos",
                    "gestión de suministros operativos",
                    "apoyo en planificación de recursos",
                    "seguimiento de indicadores de productividad",
                    "habilidades de comunicación efectiva",
                ],
                "auxiliar_contador": [
                    "apoyo contable",
                    "registros",
                    "conciliaciones",
                    "facturas",
                    "pagos",
                    "entrada de datos contables",
                    "manejo de software contable",
                    "Excel avanzado",
                    
                    "conciliaciones bancarias",
                    "gestión de cuentas por cobrar",
                    "gestión de cuentas por pagar",
                    "preparación de informes financieros básicos",
                    "archivo de documentos contables",
                    "apoyo en cierre contable",
                    "control de gastos",
                    "gestión de activos fijos",
                    "apoyo en preparación de impuestos",
                    "manejo de caja chica",
                    "apoyo en auditorías",
                    "seguimiento de presupuestos",
                    "codificación de transacciones",
                    "manejo de libros contables",
                    "apoyo en nómina",
                    "gestión de inventario contable",
                    "preparación de estados financieros básicos",
                    "cumplimiento de plazos fiscales",
                    "manejo de software ERP básico",
                    "apoyo en control interno",
                    "reconciliación de cuentas",
                    "gestión de documentación fiscal",
                    "apoyo en análisis de costos",
                    "preparación de declaraciones de IVA",
                    "gestión de viáticos",
                    "apoyo en reportes para la gerencia",
                    "conocimiento de normativa contable básica",
                    "gestión de archivo contable digital",
                    "apoyo en flujo de caja",
                    "seguimiento de indicadores financieros",
                    "ética y confidencialidad financiera",
                    "atención al detalle",
                ],
            },
            "campo": {
                "tecnico_oym": [
                    "mantenimiento preventivo",
                    "mantenimiento correctivo",
                    "operación de plantas",
                    "monitoreo de sistemas",
                    "optimización de rendimiento",
                    "gestión de activos",
                    "análisis de datos operativos",
                    "protocolos de seguridad",
                    "eficiencia energética",
                    "SCADA",
                    "PLC",
                    "sistemas de control distribuido",
                    "turbinas eólicas",
                    "paneles solares",
                    "inversores",
                    "subestaciones",
                    "transformadores",
                    "análisis de vibraciones",
                    "termografía",
                    "lubricación",
                    "alineación de ejes",
                    "balance dinámico",
                    "gestión de inventario de repuestos",
                    "planificación de mantenimiento",
                    "KPIs de mantenimiento",
                    "análisis de causa raíz",
                    "gestión de órdenes de trabajo",
                    "procedimientos operativos estándar",
                    "cumplimiento normativo",
                    "auditorías de seguridad",
                    "trabajo en altura",
                    "rescate en altura",
                    "primeros auxilios",
                    "gestión ambiental",
                    "ISO 55000",
                    "lean maintenance",
                    "Six Sigma",
                    "TPM (Mantenimiento Productivo Total)",
                    "RCM (Mantenimiento Centrado en Confiabilidad)",
                    "análisis de ciclo de vida",
                ],
                "especialista_aymt": [
                    "sistemas de alta tensión",
                    "sistemas de media tensión",
                    "subestaciones eléctricas",
                    "protección de sistemas eléctricos",
                    "normativas eléctricas",
                    "diagnóstico de fallas",
                    "mantenimiento de transformadores",
                    "seguridad eléctrica",
                    "esquemas de conexión",
                    "interruptores de potencia",
                    "seccionadores",
                    "pararrayos",
                    "aisladores",
                    "cables de potencia",
                    "pruebas de aislamiento",
                    "factor de potencia",
                    "análisis de aceite dieléctrico",
                    "termografía en subestaciones",
                    "coordinación de protecciones",
                    "relés de protección",
                    "SCADA para subestaciones",
                    "sistemas de puesta a tierra",
                    "cálculo de cortocircuitos",
                    "análisis de transitorios",
                    "compensación de potencia reactiva",
                    "calidad de energía",
                    "armónicos",
                    "regulación de tensión",
                    "conmutación de taps",
                    "mantenimiento de celdas",
                    "pruebas de rigidez dieléctrica",
                    "medición de resistencia de contacto",
                    "análisis de descargas parciales",
                    "IEC 61850",
                    "ANSI/IEEE",
                    "mantenimiento de baterías",
                    "sistemas de corriente continua",
                    "análisis de redes eléctricas",
                    "gestión de activos eléctricos",
                ],
                "tecnico_reparacion_componentes": [
                    "reparación de inversores",
                    "mantenimiento de generadores",
                    "diagnóstico de averías electrónicas",
                    "calibración de equipos",
                    "sistemas de control",
                    "reparación de placas de circuito",
                    "actualización de firmware",
                    "pruebas de funcionamiento",
                    "soldadura de componentes electrónicos",
                    "lectura de esquemas eléctricos",
                    "osciloscopios",
                    "multímetros",
                    "analizadores de espectro",
                    "programación de microcontroladores",
                    "reparación de fuentes de alimentación",
                    "mantenimiento de baterías",
                    "sistemas de refrigeración",
                    "compatibilidad electromagnética",
                    "protección contra sobretensiones",
                    "análisis de fallos en semiconductores",
                    "reparación de motores eléctricos",
                    "mantenimiento de transformadores",
                    "sistemas de monitoreo remoto",
                    "reparación de sensores",
                    "calibración de instrumentos de medición",
                    "gestión térmica de componentes",
                    "pruebas de estrés en componentes",
                    "análisis de vibraciones en equipos",
                    "reparación de convertidores DC/DC",
                    "mantenimiento de UPS",
                    "reparación de controladores de carga",
                    "sistemas de protección eléctrica",
                    "reparación de displays y HMI",
                    "actualización de sistemas legacy",
                    "gestión de obsolescencia de componentes",
                    "pruebas de compatibilidad de software",
                    "reparación de equipos de comunicación",
                    "mantenimiento predictivo",
                    "análisis de datos de fallas",
                    "gestión de inventario de componentes",
                ],
                "especialista_palas": [
                    "inspección de palas",
                    "reparación de fibra de vidrio",
                    "análisis estructural",
                    "técnicas de laminado",
                    "mantenimiento preventivo de palas",
                    "evaluación de daños",
                    "trabajos en altura",
                    "aerodinámica de palas",
                    "materiales compuestos",
                    "resinas epoxy",
                    "fibra de carbono",
                    "técnicas de infusión",
                    "balanceo de palas",
                    "ensayos no destructivos",
                    "ultrasonido en materiales compuestos",
                    "termografía en palas",
                    "reparación de bordes de ataque",
                    "reparación de bordes de salida",
                    "sistemas de protección contra rayos",
                    "recubrimientos especiales",
                    "análisis de fatiga en palas",
                    "inspección por drones",
                    "técnicas de acceso por cuerdas",
                    "normativas de seguridad en trabajos verticales",
                    "diseño de reparaciones estructurales",
                    "análisis de vibraciones en palas",
                    "sistemas anti-hielo",
                    "optimización de perfiles aerodinámicos",
                    "análisis de cargas en palas",
                    "técnicas de unión adhesiva",
                    "reparación de núcleos de espuma",
                    "sistemas de monitoreo de integridad estructural",
                    "análisis de modos de fallo",
                    "técnicas de reparación en campo",
                    "gestión de proyectos de mantenimiento",
                    "evaluación de vida útil de palas",
                    "técnicas de extensión de vida útil",
                    "análisis de rendimiento aerodinámico",
                    "certificación de reparaciones",
                    "gestión de calidad en reparaciones",
                ],
                "ingeniero_grandes_correctivos": [
                    "planificación de correctivos",
                    "gestión de proyectos de mejora",
                    "análisis de causa raíz",
                    "optimización de sistemas",
                    "retrofit de equipos",
                    "coordinación de paradas programadas",
                    "evaluación de riesgos",
                    "mejora continua",
                    "gestión de contratos",
                    "análisis de costos",
                    "planificación de recursos",
                    "gestión de stakeholders",
                    "ingeniería de confiabilidad",
                    "análisis de modos y efectos de falla (AMEF)",
                    "gestión de la configuración",
                    "control de calidad",
                    "auditorías técnicas",
                    "gestión del cambio",
                    "análisis de impacto operacional",
                    "planificación de contingencias",
                    "optimización de procesos",
                    "gestión de proveedores",
                    "análisis de ciclo de vida de activos",
                    "gestión de documentación técnica",
                    "análisis de datos de mantenimiento",
                    "KPIs de rendimiento",
                    "técnicas de resolución de problemas",
                    "gestión de la seguridad",
                    "cumplimiento normativo",
                    "análisis de eficiencia energética",
                    "gestión de residuos",
                    "análisis de vibraciones",
                    "termografía",
                    "análisis de aceites",
                    "ultrasonido",
                    "balanceo dinámico",
                    "alineación láser",
                    "pruebas no destructivas",
                    "gestión de la obsolescencia",
                    "ingeniería de valor",
                ],
            },
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
        
        umbral_minimo = 0.3
        
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
            
            shutil.copy2(
                os.path.join(resultado_folder, sanitized_name, candidate['filename']),
                os.path.join(candidate_folder, candidate['filename'])
            )
            
            with open(os.path.join(candidate_folder, "info_candidato.txt"), 'w', encoding='utf-8') as f:
                f.write(f"Nombre: {candidate['nombre']}\n")
                f.write(f"Teléfono: {candidate['telefono']}\n")
                f.write(f"Correo: {candidate['correo']}\n")
                f.write(f"Tipo de personal: {candidate['tipo_personal']}\n")
                f.write(f"Puesto: {candidate['puesto']}\n")
                f.write(f"Puntuación: {candidate['puntuacion']*100:.2f}\n")