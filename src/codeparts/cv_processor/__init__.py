from .processor import CVProcessor

__all__ = ['CVProcessor', 'process_cvs_menu']

import os
import asyncio
from InquirerPy import inquirer
from InquirerPy import get_style
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from InquirerPy.validator import EmptyInputValidator
from system.config import (
    MENU_CONFIG,
    INQUIRER_STYLE,
    UI_SYMBOLS,
    LASTVERSION,
    Ascii_logo,
    clear_screen,
    set_console_title,
    CURRICULUMS_FOLDER
)

style = get_style(INQUIRER_STYLE)

async def process_cvs_menu():
    """Menú principal del procesador de CVs"""
    # Verificar que exista la carpeta de curriculums
    if not os.path.exists(CURRICULUMS_FOLDER):
        print(f"\n   No se encontró la carpeta 'Curriculums' en {CURRICULUMS_FOLDER}. Por favor, créela y coloque los CVs en formato PDF.")
        await inquirer.text(message="Presione Enter para continuar...", qmark='   >', style=style).execute_async()
        set_console_title(f'CJR Toolkit v{LASTVERSION} - Menú Principal')
        return

    while True:
        clear_screen()
        Ascii_logo()
        
        # Primer nivel: Selección de categoría
        category_choices = [Separator()]
        for category in MENU_CONFIG['cv_processor_menu']['categories'].keys():
            category_choices.append(Choice(category, f"Puestos de {category}"))
        category_choices.append(Separator("\n"))
        category_choices.append(Choice("volver", "Volver al menú principal"))
        category_choices.append(Separator())

        # Seleccionar categoría
        selected_category = await inquirer.select(
            message="   Seleccione la categoría de puesto:",
            choices=category_choices,
            default=None,
            pointer=UI_SYMBOLS['pointer'],
            qmark='',
            style=style
        ).execute_async()

        if selected_category == "volver":
            set_console_title(f'CJR Toolkit v{LASTVERSION} - Menú Principal')
            return

        # Segundo nivel: Selección de puesto dentro de la categoría
        clear_screen()
        Ascii_logo()
        
        job_choices = [Separator()]
        jobs = MENU_CONFIG['cv_processor_menu']['categories'][selected_category]
        job_choices.extend([Choice(job, job.replace('_', ' ').title()) for job in jobs])
        job_choices.append(Separator("\n"))
        job_choices.append(Choice("atras", "Volver a categorías"))
        job_choices.append(Separator())

        # Seleccionar puesto
        puesto = await inquirer.select(
            message=f"   Seleccione el puesto de {selected_category}:",
            choices=job_choices,
            default=None,
            pointer=UI_SYMBOLS['pointer'],
            qmark='',
            style=style
        ).execute_async()

        if puesto == "atras":
            continue

        # Obtener nombre del reclutador
        clear_screen()
        Ascii_logo()
        
        recruiter_name = await inquirer.text(
            message="   Ingrese su nombre (para el mensaje de WhatsApp):",
            default="[Tu nombre]",
            validate=EmptyInputValidator("El nombre no puede estar vacío"),
            style=style
        ).execute_async()

        clear_screen()
        Ascii_logo()
        print("\n   Iniciando procesamiento de CVs...")
        
        # Procesar CVs
        processor = CVProcessor(os.path.dirname(CURRICULUMS_FOLDER))
        candidates = processor.process_all_cvs(puesto, recruiter_name)
        
        if not candidates:
            print("\n   No se encontraron candidatos aptos para el puesto.")
            print("   Recomendamos iniciar con el proceso de publicación de la vacante en Redes Sociales.")
            await inquirer.text(message="Presione Enter para continuar...", qmark='   >', style=style).execute_async()
            continue
        
        # Mostrar resultados
        print("\n   === TOP 3 CANDIDATOS ===\n")
        for i, (cv_data, score) in enumerate(candidates, 1):
            print(f"\n   {'='*20} Candidato #{i} {'='*20}")
            formatted_info = processor._format_candidate_info(cv_data, score)
            # Agregar indentación a cada línea
            formatted_info = "\n".join(f"   {line}" for line in formatted_info.split("\n"))
            print(formatted_info)
            
        print("\n   Los resultados completos han sido guardados en la carpeta 'Results/CV Processor'")
        
        await inquirer.text(message="Presione Enter para continuar...", qmark='   >', style=style).execute_async()
        set_console_title(f'CJR Toolkit v{LASTVERSION} - Menú Principal')
        return
