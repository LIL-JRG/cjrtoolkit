"""
Archivo de configuración de keywords y patrones para el procesamiento de CVs
"""

# Patrones bloqueados en el procesamiento de CVs
BLOCKED_PATTERNS = {
    "estudio", "bilingtie", "analista", "calle", "avenida", "experiencia laboral",
    "idioma", "inglés", "español", "francés", "alemán", "curriculum vitae", "cv",
    "teléfono", "email", "correo", "electrónico", "dirección", "código postal",
    "educación", "formación", "habilidades", "competencias", "referencias",
    "cualquier", "lugar", "nivel", "oral", "escrito", "avanzado", "intermedio", "básico"
}

# Títulos académicos y profesionales
TITLES = {
    "lic", "licenciado", "licenciada", "ing", "ingeniero", "ingeniera", 
    "prof", "profesor", "profesora", "dr", "doctor", "doctora", 
    "mtro", "maestro", "maestra"
}

# Nombres comunes para filtrar
COMMON_NAMES = {
    "juan", "pablo", "francisco", "amelia", "ocampo", "mercado", "jose", "julián", 
    "josé", "maría", "guadalupe", "carlos", "fernando", "alejandro", "sofia", 
    "valentina", "isabella", "martínez", "gonzález", "rodríguez", "lópez", 
    "pérez", "sánchez", "ramírez", "cruz", "hernández", "garcía", "morales", 
    "ortega", "vázquez", "mendoza", "castillo", "jiménez", "torres", "flores", 
    "ramos", "reyes", "gutiérrez", "chávez", "márquez", "domínguez", "cervantes", 
    "villanueva", "montes", "escalante", "quintana", "salazar", "valenzuela", 
    "aguilar", "navarro", "padilla", "santana", "treviño", "uribe", "zavala", 
    "ibarra", "maldonado", "pacheco", "santiago", "valdez", "zúñiga", "bautista", 
    "carrillo", "delgado", "espinoza", "figueroa", "gallegos", "huerta", "ibáñez", 
    "juárez", "luna", "medina", "nieto", "oliva"
}

# Palabras clave por área profesional
PROFESSIONAL_KEYWORDS = {
    "tecnología": {
        "programación": ["python", "java", "javascript", "c++", "desarrollo web", "frontend", "backend"],
        "redes": ["cisco", "redes", "networking", "tcp/ip", "vpn", "firewall"],
        "bases_datos": ["sql", "mysql", "postgresql", "mongodb", "oracle", "nosql"],
        "cloud": ["aws", "azure", "google cloud", "cloud computing", "docker", "kubernetes"]
    },
    "administración": {
        "finanzas": ["contabilidad", "finanzas", "presupuesto", "auditoría", "impuestos"],
        "recursos_humanos": ["reclutamiento", "selección", "capacitación", "nómina", "desarrollo organizacional"],
        "marketing": ["marketing digital", "redes sociales", "seo", "publicidad", "ventas"],
        "gestión": ["administración", "gestión de proyectos", "planeación estratégica"]
    },
    "ingeniería": {
        "civil": ["construcción", "estructuras", "hidráulica", "topografía", "autocad"],
        "industrial": ["procesos", "calidad", "producción", "logística", "six sigma"],
        "mecánica": ["diseño mecánico", "manufactura", "mantenimiento", "solidworks"],
        "eléctrica": ["electricidad", "electrónica", "automatización", "plc"]
    }
}

# Habilidades blandas
SOFT_SKILLS = {
    "liderazgo", "trabajo en equipo", "comunicación", "resolución de problemas",
    "adaptabilidad", "creatividad", "pensamiento crítico", "organización",
    "gestión del tiempo", "negociación", "empatía", "proactividad"
}

# Certificaciones comunes
CERTIFICATIONS = {
    "tecnología": ["CCNA", "AWS Certified", "Microsoft Certified", "CompTIA", "ITIL"],
    "administración": ["PMP", "CPA", "Six Sigma", "SHRM", "CFA"],
    "ingeniería": ["PE", "FE", "LEED", "ASQ", "PMI"]
}

# Idiomas y niveles
LANGUAGES = {
    "idiomas": ["inglés", "español", "francés", "alemán", "italiano", "portugués", "chino", "japonés"],
    "niveles": ["básico", "intermedio", "avanzado", "nativo", "fluido"]
}
