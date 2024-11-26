"""
Perfiles de puestos y sus requerimientos para el ranking de candidatos
"""

JOB_PROFILES = {
    # Puestos de Oficina
    "administracion_finanzas": {
        "required_skills": [
            "administración",
            "finanzas",
            "contabilidad",
            "excel avanzado",
            "gestión financiera"
        ],
        "preferred_skills": [
            "sap",
            "erp",
            "presupuestos",
            "análisis financiero",
            "planeación estratégica"
        ],
        "min_experience_years": 2,
        "required_languages": ["español"],
        "preferred_languages": ["inglés"],
        "min_score": 70
    },
    "control_proyectos": {
        "required_skills": [
            "gestión de proyectos",
            "ms project",
            "excel avanzado",
            "planificación",
            "control de costos"
        ],
        "preferred_skills": [
            "pmp",
            "metodologías ágiles",
            "análisis de riesgos",
            "kpis",
            "reporting"
        ],
        "min_experience_years": 2,
        "required_languages": ["español"],
        "preferred_languages": ["inglés"],
        "min_score": 70
    },
    "gerente_administracion": {
        "required_skills": [
            "administración",
            "liderazgo",
            "gestión financiera",
            "planificación estratégica",
            "toma de decisiones"
        ],
        "preferred_skills": [
            "erp",
            "gestión de equipos",
            "negociación",
            "presupuestos",
            "optimización de procesos"
        ],
        "min_experience_years": 2,
        "required_languages": ["español", "inglés"],
        "preferred_languages": [],
        "min_score": 75
    },
    "auxiliar_contable": {
        "required_skills": [
            "contabilidad",
            "excel",
            "cálculos contables",
            "registro de operaciones",
            "archivo"
        ],
        "preferred_skills": [
            "software contable",
            "conciliaciones bancarias",
            "facturación",
            "impuestos",
            "nómina"
        ],
        "min_experience_years": 1,
        "required_languages": ["español"],
        "preferred_languages": ["inglés"],
        "min_score": 65
    },
    "flotilla_vehicular": {
        "required_skills": [
            "gestión de flotillas",
            "logística",
            "mantenimiento vehicular",
            "excel",
            "control de gastos"
        ],
        "preferred_skills": [
            "gps tracking",
            "gestión de combustible",
            "seguros vehiculares",
            "programación de mantenimiento",
            "reportes de rendimiento"
        ],
        "min_experience_years": 2,
        "required_languages": ["español"],
        "preferred_languages": ["inglés"],
        "min_score": 70
    },
    "almacen_compras": {
        "required_skills": [
            "gestión de inventarios",
            "compras",
            "logística",
            "control de almacén",
            "excel"
        ],
        "preferred_skills": [
            "sap",
            "erp",
            "negociación con proveedores",
            "control de costos",
            "gestión de pedidos"
        ],
        "min_experience_years": 2,
        "required_languages": ["español"],
        "preferred_languages": ["inglés"],
        "min_score": 70
    },
    "recursos_humanos": {
        "required_skills": [
            "reclutamiento",
            "selección de personal",
            "gestión de personal",
            "nómina",
            "relaciones laborales"
        ],
        "preferred_skills": [
            "desarrollo organizacional",
            "capacitación",
            "clima laboral",
            "legislación laboral",
            "evaluación de desempeño"
        ],
        "min_experience_years": 3,
        "required_languages": ["español"],
        "preferred_languages": ["inglés"],
        "min_score": 75
    },
    "gerente_ventas": {
        "required_skills": [
            "gestión comercial",
            "liderazgo",
            "estrategia de ventas",
            "negociación",
            "desarrollo de negocios"
        ],
        "preferred_skills": [
            "crm",
            "análisis de mercado",
            "gestión de equipos",
            "kpis comerciales",
            "planeación estratégica"
        ],
        "min_experience_years": 3,
        "required_languages": ["español", "inglés"],
        "preferred_languages": [],
        "min_score": 80
    },
    "ejecutivo_ventas": {
        "required_skills": [
            "ventas",
            "atención a clientes",
            "negociación",
            "prospección",
            "seguimiento comercial"
        ],
        "preferred_skills": [
            "crm",
            "presentaciones ejecutivas",
            "técnicas de venta",
            "análisis de mercado",
            "reportes de ventas"
        ],
        "min_experience_years": 2,
        "required_languages": ["español"],
        "preferred_languages": ["inglés"],
        "min_score": 70
    },
    "gerente_alta_media_tension": {
        "required_skills": [
            "gestión de proyectos eléctricos",
            "alta tensión",
            "media tensión",
            "liderazgo",
            "planificación estratégica"
        ],
        "preferred_skills": [
            "gestión de equipos",
            "normativas eléctricas",
            "control de presupuestos",
            "gestión de riesgos",
            "relaciones con clientes"
        ],
        "min_experience_years": 2,
        "required_languages": ["español", "inglés"],
        "preferred_languages": [],
        "min_score": 80
    },
    "gerente_qshe": {
        "required_skills": [
            "sistemas de gestión",
            "seguridad industrial",
            "salud ocupacional",
            "gestión ambiental",
            "liderazgo"
        ],
        "preferred_skills": [
            "iso 9001",
            "iso 14001",
            "iso 45001",
            "auditorías",
            "gestión de riesgos"
        ],
        "min_experience_years": 2,
        "required_languages": ["español", "inglés"],
        "preferred_languages": [],
        "min_score": 80
    },
    "coordinador_sgi": {
        "required_skills": [
            "sistemas integrados de gestión",
            "documentación",
            "auditorías internas",
            "mejora continua",
            "indicadores de gestión"
        ],
        "preferred_skills": [
            "iso 9001",
            "iso 14001",
            "iso 45001",
            "gestión de procesos",
            "capacitación"
        ],
        "min_experience_years": 2,
        "required_languages": ["español"],
        "preferred_languages": ["inglés"],
        "min_score": 75
    },
    "coordinador_qshe": {
        "required_skills": [
            "seguridad industrial",
            "salud ocupacional",
            "medio ambiente",
            "normativa sst",
            "gestión de riesgos"
        ],
        "preferred_skills": [
            "investigación de accidentes",
            "capacitación en seguridad",
            "permisos de trabajo",
            "planes de emergencia",
            "auditorías"
        ],
        "min_experience_years": 2,
        "required_languages": ["español"],
        "preferred_languages": ["inglés"],
        "min_score": 75
    },
    "gestor_documental": {
        "required_skills": [
            "gestión documental",
            "organización de archivos",
            "control de documentos",
            "digitalización",
            "excel"
        ],
        "preferred_skills": [
            "sistemas de gestión documental",
            "normativas iso",
            "gestión de la información",
            "base de datos",
            "sharepoint"
        ],
        "min_experience_years": 2,
        "required_languages": ["español"],
        "preferred_languages": ["inglés"],
        "min_score": 70
    },
    "gerente_oym": {
        "required_skills": [
            "gestión de operaciones",
            "mantenimiento industrial",
            "liderazgo",
            "planificación estratégica",
            "gestión de proyectos"
        ],
        "preferred_skills": [
            "gestión de activos",
            "kpis operativos",
            "mejora continua",
            "gestión de presupuestos",
            "gestión de contratos"
        ],
        "min_experience_years": 2,
        "required_languages": ["español", "inglés"],
        "preferred_languages": [],
        "min_score": 80
    },
    "coordinador_proyectos_norte": {
        "required_skills": [
            "gestión de proyectos",
            "coordinación de equipos",
            "planificación",
            "seguimiento de obras",
            "control de costos"
        ],
        "preferred_skills": [
            "ms project",
            "gestión de contratos",
            "reportes ejecutivos",
            "gestión de recursos",
            "resolución de conflictos"
        ],
        "min_experience_years": 2,
        "required_languages": ["español"],
        "preferred_languages": ["inglés"],
        "min_score": 80
    },
    "licitaciones_norte": {
        "required_skills": [
            "licitaciones públicas",
            "análisis de costos",
            "elaboración de propuestas",
            "excel avanzado",
            "normativa de contratación"
        ],
        "preferred_skills": [
            "compranet",
            "gestión de proyectos",
            "análisis de mercado",
            "negociación",
            "presentaciones ejecutivas"
        ],
        "min_experience_years": 2,
        "required_languages": ["español"],
        "preferred_languages": ["inglés"],
        "min_score": 75
    },
    "coordinador_grandes_correctivos": {
        "required_skills": [
            "gestión de mantenimiento",
            "planificación de trabajos",
            "coordinación de equipos",
            "control de costos",
            "gestión de recursos"
        ],
        "preferred_skills": [
            "mantenimiento predictivo",
            "gestión de contratos",
            "kpis de mantenimiento",
            "mejora continua",
            "reportes técnicos"
        ],
        "min_experience_years": 2,
        "required_languages": ["español"],
        "preferred_languages": ["inglés"],
        "min_score": 80
    },
    "coordinador_proyectos_sur": {
        "required_skills": [
            "gestión de proyectos",
            "coordinación de equipos",
            "planificación",
            "seguimiento de obras",
            "control de costos"
        ],
        "preferred_skills": [
            "ms project",
            "gestión de contratos",
            "reportes ejecutivos",
            "gestión de recursos",
            "resolución de conflictos"
        ],
        "min_experience_years": 2,
        "required_languages": ["español"],
        "preferred_languages": ["inglés"],
        "min_score": 80
    },
    "jefe_proyecto": {
        "required_skills": [
            "dirección de proyectos",
            "liderazgo",
            "gestión de recursos",
            "planificación estratégica",
            "control presupuestario"
        ],
        "preferred_skills": [
            "pmp",
            "gestión de riesgos",
            "gestión de stakeholders",
            "metodologías ágiles",
            "negociación"
        ],
        "min_experience_years": 3,
        "required_languages": ["español", "inglés"],
        "preferred_languages": [],
        "min_score": 85
    },
    "gerente_suministros_reparacion": {
        "required_skills": [
            "gestión de suministros",
            "cadena de suministro",
            "gestión de reparaciones",
            "liderazgo",
            "planificación estratégica"
        ],
        "preferred_skills": [
            "erp",
            "gestión de inventarios",
            "negociación con proveedores",
            "control de calidad",
            "optimización de procesos"
        ],
        "min_experience_years": 2,
        "required_languages": ["español", "inglés"],
        "preferred_languages": [],
        "min_score": 85
    },

    # Puestos Técnicos
    "operacion_mantenimiento": {
        "required_skills": [
            "mantenimiento industrial",
            "operación de equipos",
            "diagnóstico técnico",
            "seguridad industrial",
            "lectura de planos"
        ],
        "preferred_skills": [
            "automatización",
            "hidráulica",
            "neumática",
            "gestión de mantenimiento",
            "predictivo"
        ],
        "min_experience_years": 2,
        "required_languages": ["español"],
        "preferred_languages": ["inglés"],
        "min_score": 70
    },
    "alta_media_tension": {
        "required_skills": [
            "electricidad industrial",
            "alta tensión",
            "media tensión",
            "protecciones eléctricas",
            "normas de seguridad"
        ],
        "preferred_skills": [
            "subestaciones",
            "transformadores",
            "pruebas eléctricas",
            "termografía",
            "mantenimiento predictivo"
        ],
        "min_experience_years": 2,
        "required_languages": ["español"],
        "preferred_languages": ["inglés"],
        "min_score": 80
    },
    "reparacion_componentes": {
        "required_skills": [
            "mecánica",
            "diagnóstico",
            "reparación",
            "herramientas especializadas",
            "lectura de planos"
        ],
        "preferred_skills": [
            "soldadura",
            "metrología",
            "control de calidad",
            "hidráulica",
            "neumática"
        ],
        "min_experience_years": 2,
        "required_languages": ["español"],
        "preferred_languages": ["inglés"],
        "min_score": 75
    },
    "reparacion_palas": {
        "required_skills": [
            "reparación de palas",
            "materiales compuestos",
            "fibra de vidrio",
            "resinas",
            "trabajo en altura"
        ],
        "preferred_skills": [
            "inspección de daños",
            "acabados superficiales",
            "técnicas de laminado",
            "control de calidad",
            "mantenimiento preventivo"
        ],
        "min_experience_years": 2,
        "required_languages": ["español"],
        "preferred_languages": ["inglés"],
        "min_score": 70
    },
    "grandes_correctivos": {
        "required_skills": [
            "mantenimiento correctivo",
            "diagnóstico de fallos",
            "reparaciones mayores",
            "gestión de proyectos",
            "seguridad industrial"
        ],
        "preferred_skills": [
            "planificación de trabajos",
            "supervisión de equipos",
            "control de costos",
            "gestión de recursos",
            "reportes técnicos"
        ],
        "min_experience_years": 2,
        "required_languages": ["español"],
        "preferred_languages": ["inglés"],
        "min_score": 80
    }
}

def is_candidate_suitable(cv_data: dict, puesto: str) -> tuple[bool, float]:
    """
    Determina si un candidato es apto para el puesto y calcula su puntaje
    """
    if not cv_data or not isinstance(cv_data, dict):
        return False, 0
    
    # Obtener perfil del puesto
    perfil = JOB_PROFILES.get(puesto.lower(), {})
    if not perfil:
        return False, 0

    # Obtener y normalizar habilidades del candidato
    habilidades = cv_data.get('habilidades', [])
    if isinstance(habilidades, str):
        habilidades = [habilidades]
    
    # Convertir a minúsculas y normalizar
    habilidades = [h.lower().strip() for h in habilidades if isinstance(h, str)]
    
    # Obtener experiencia del candidato
    experiencia = cv_data.get('experiencia', [])
    experiencia_str = []
    años_experiencia = 0
    
    if isinstance(experiencia, list):
        for exp in experiencia:
            if isinstance(exp, dict):
                # Extraer años de experiencia
                periodo = exp.get('periodo', '').lower()
                if 'presente' in periodo or 'actual' in periodo:
                    try:
                        año_inicio = int(''.join(filter(str.isdigit, periodo.split('-')[0])))
                        años_experiencia += 2024 - año_inicio
                    except:
                        pass
                
                # Agregar puesto y responsabilidades como habilidades potenciales
                puesto_exp = exp.get('puesto', '').lower().strip()
                if puesto_exp:
                    experiencia_str.append(puesto_exp)
                for resp in exp.get('responsabilidades', []):
                    if isinstance(resp, str):
                        experiencia_str.append(resp.lower().strip())
    
    # Combinar habilidades explícitas y de experiencia
    todas_habilidades = habilidades + experiencia_str
    
    # Obtener habilidades requeridas y deseables
    requeridas = [h.lower().strip() for h in perfil.get('required_skills', [])]
    deseables = [h.lower().strip() for h in perfil.get('preferred_skills', [])]
    
    # Calcular puntaje base (50%)
    puntaje = 0
    total_requeridas = len(requeridas) if requeridas else 1
    
    # Puntaje por habilidades requeridas (50%)
    for hab in requeridas:
        # Buscar coincidencias parciales
        palabras_hab = set(hab.split())
        mejor_coincidencia = 0
        
        for h in todas_habilidades:
            palabras_h = set(h.split())
            # Calcular porcentaje de coincidencia
            if palabras_hab:
                # Buscar coincidencias por palabras individuales
                coincidencia = len(palabras_hab & palabras_h) / len(palabras_hab)
                mejor_coincidencia = max(mejor_coincidencia, coincidencia)
                
                # Buscar coincidencias por subcadenas
                if any(p in h for p in palabras_hab):
                    mejor_coincidencia = max(mejor_coincidencia, 0.75)
        
        # Asignar puntaje proporcional a la mejor coincidencia
        puntaje += (50 / total_requeridas) * mejor_coincidencia
    
    # Puntaje por habilidades deseables (30%)
    if deseables:
        for hab in deseables:
            palabras_hab = set(hab.split())
            mejor_coincidencia = 0
            
            for h in todas_habilidades:
                palabras_h = set(h.split())
                if palabras_hab:
                    # Buscar coincidencias por palabras individuales
                    coincidencia = len(palabras_hab & palabras_h) / len(palabras_hab)
                    mejor_coincidencia = max(mejor_coincidencia, coincidencia)
                    
                    # Buscar coincidencias por subcadenas
                    if any(p in h for p in palabras_hab):
                        mejor_coincidencia = max(mejor_coincidencia, 0.75)
            
            puntaje += (30 / len(deseables)) * mejor_coincidencia
    
    # Puntaje por idiomas (10%)
    idiomas_candidato = []
    idiomas = cv_data.get('idiomas', [])
    if isinstance(idiomas, list):
        for idioma in idiomas:
            if isinstance(idioma, str):
                idiomas_candidato.append(idioma.lower())
            elif isinstance(idioma, dict):
                idiomas_candidato.append(idioma.get('idioma', '').lower())
    
    idiomas_requeridos = [i.lower() for i in perfil.get('required_languages', [])]
    idiomas_deseables = [i.lower() for i in perfil.get('preferred_languages', [])]
    
    # Verificar idiomas requeridos (7%)
    if idiomas_requeridos:
        for idioma in idiomas_requeridos:
            if any(idioma in i for i in idiomas_candidato):
                puntaje += 7 / len(idiomas_requeridos)
    
    # Verificar idiomas deseables (3%)
    if idiomas_deseables:
        for idioma in idiomas_deseables:
            if any(idioma in i for i in idiomas_candidato):
                puntaje += 3 / len(idiomas_deseables)
    
    # Bonus por experiencia (hasta 10% extra)
    años_minimos = perfil.get('min_experience_years', 2)
    if años_experiencia >= años_minimos:
        # Dar bonus proporcional a los años de experiencia extra
        bonus = min(10, (años_experiencia - años_minimos + 1) * 2.5)
        puntaje = min(100, puntaje + bonus)
    
    # Bonus por coincidencias parciales (hasta 10% extra)
    if puntaje >= 40:  # Si ya tiene un puntaje decente
        puntaje = min(100, puntaje + 10)
    
    # Redondear puntaje
    puntaje = round(puntaje, 1)
    
    # Determinar si es apto (más flexible)
    min_score = perfil.get('min_score', 40)  # Bajamos el mínimo predeterminado a 40
    return puntaje >= min_score, puntaje
