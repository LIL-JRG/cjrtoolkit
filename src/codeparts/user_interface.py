import os
import asyncio
from datetime import datetime
from InquirerPy import inquirer
from InquirerPy import get_style
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from InquirerPy.validator import EmptyInputValidator
from tabulate import tabulate
from system.config import (
    MENU_CONFIG, 
    INQUIRER_STYLE, 
    UI_SYMBOLS, 
    LASTVERSION, 
    CURRICULUMS_FOLDER,
    Ascii_logo, 
    clear_screen,
    set_console_title,
    center_text
)
from codeparts.email_rewriter import rewrite_menu
from codeparts.sicaru_ia import sicaru_assistant_menu
from codeparts.get_certificate import download_certificate
from codeparts.winda_validator import WindaValidator
from codeparts.pdf_converter import PDFConverter
from termcolor import colored
import colorama
import io
import qrcode

colorama.init()

# Crear el objeto de estilo una vez
style = get_style(INQUIRER_STYLE)

# Configuración del estilo de InquirerPy
terminal_width = os.get_terminal_size().columns

class UserInterface:

    @staticmethod
    def generate_qr_code(url):
        qr = qrcode.QRCode()
        qr.add_data(url)
        f = io.StringIO()
        qr.print_ascii(out=f)
        f.seek(0)
        return f.read()

    @staticmethod
    async def main_menu():
        set_console_title(f'CJR Toolkit v{LASTVERSION} - Menú Principal')
        while True:
            clear_screen()
            Ascii_logo()
            
            choices = [Separator()]
            for item in MENU_CONFIG['main_menu'][:-1]:  
                choices.append(Choice(item['key'], item['name']))
            choices.append(Separator("\n"))  
            last_item = MENU_CONFIG['main_menu'][-1]
            choices.append(Choice(last_item['key'], last_item['name']))
            choices.append(Separator())
            choices.append(Separator("\n"))  

            choice = await inquirer.select(
                message="   (Use las flechas ↑↓ para navegar, Enter para seleccionar)\n\n   Seleccione una opción:",
                choices=choices,
                default=MENU_CONFIG['main_menu'][0]['key'],
                pointer=UI_SYMBOLS['pointer'],
                qmark='',
                style=style
            ).execute_async()

            clear_screen()
            Ascii_logo()

            if choice == "validar":
                set_console_title(f'CJR Toolkit v{LASTVERSION} - Winda ID Validator')
                await UserInterface.validate_winda_id()
            elif choice == "procesar":
                set_console_title(f'CJR Toolkit v{LASTVERSION} - CV Processor')
                await UserInterface.process_cvs_menu()
            elif choice == "doc":
                set_console_title(f'CJR Toolkit v{LASTVERSION} - PDF Converter')
                await UserInterface.convert_file()
            elif choice == "email_rewriter":
                set_console_title(f'CJR Toolkit v{LASTVERSION} - Email re-writer')
                await rewrite_menu()
            elif choice == "sicaru_ia":
                set_console_title(f'CJR Toolkit v{LASTVERSION} - Sicarú IA')
                await sicaru_assistant_menu()
            elif choice == "salir":
                clear_screen()
                Ascii_logo()
                set_console_title(f'CJR Toolkit v{LASTVERSION} - Exit')
                print("\n   Gracias por usar CJR Toolkit. ¡Hasta luego!")
                break
            else:
                print(f"La opción {choice} aún no está implementada.")
                await asyncio.sleep(2)

    @staticmethod
    async def convert_file():
        while True:
            clear_screen()
            Ascii_logo()
            choice = await inquirer.select(
                message="   Seleccione el tipo de conversión:",
                choices=[
                    Separator(),
                    Choice("ptoword", "PDF a Word"),
                    Choice("ptoexcel", "PDF a Excel"),
                    Choice("ptopp", "PDF a PowerPoint"),
                    Choice("extimg", "Extraer imágenes de PDF"),
                    Choice("alltopdf", "Word, Excel o PowerPoint a PDF"),
                    Separator("\n"),  
                    Choice("volver", "Volver"),
                    Separator()
                ],
                default="oficina",
                pointer=UI_SYMBOLS['pointer'],
                qmark='',
                style=style
            ).execute_async()
    
            if choice == "volver":
                clear_screen()
                set_console_title(f'CJR Toolkit v{LASTVERSION} - Menú Principal')
                return  

            file_path = PDFConverter.select_file()
            if not file_path:
                print("No se seleccionó ningún archivo.")
                await inquirer.text(message="Presione Enter para continuar...", qmark='   >', style=style).execute_async()
                continue  

            result = ""
            if choice == "ptoword" and file_path.lower().endswith('.pdf'):
                result = await PDFConverter.pdf_to_word(file_path)
            elif choice == "ptoexcel" and file_path.lower().endswith('.pdf'):
                result = await PDFConverter.pdf_to_excel(file_path)
            elif choice == "ptopp" and file_path.lower().endswith('.pdf'):
                result = await PDFConverter.pdf_to_powerpoint(file_path)
            elif choice == "extimg" and file_path.lower().endswith('.pdf'):
                result = await PDFConverter.extract_images_from_pdf(file_path)
            elif choice == "alltopdf" and file_path.lower().endswith(('.docx', '.xlsx', '.pptx')):
                result = await PDFConverter.office_to_pdf(file_path)
            else:
                result = "Formato de archivo no soportado o incompatible con la opción seleccionada."

            print(result)
            await inquirer.text(message="Presione Enter para continuar...", qmark='   >', style=style).execute_async()


    @staticmethod
    async def process_cvs_menu():
        from .cv_processor.processor import CVProcessor
        from .cv_processor.job_profiles import JOB_PROFILES
        from system.config import MENU_CONFIG
        
        if not os.path.exists(CURRICULUMS_FOLDER):
            print(f"\n   No se encontró la carpeta 'Curriculums' en {CURRICULUMS_FOLDER}. Por favor, créela y coloque los CVs en formato PDF.")
            await inquirer.text(message="Presione Enter para continuar...", qmark='   >', style=style).execute_async()
            return

        clear_screen()
        Ascii_logo()
        
        # Selección inicial del tipo de candidato
        tipo_candidato = await inquirer.select(
            message="   ¿Qué tipo de candidatos desea buscar?",
            choices=[
                Separator(),
                Choice("Oficina", "Candidatos para puestos administrativos"),
                Choice("Técnicos", "Candidatos para puestos técnicos"),
                Separator("\n"),
                Choice("volver", "Volver al menú principal"),
                Separator()
            ],
            default="Oficina",
            pointer=UI_SYMBOLS['pointer'],
            qmark='',
            style=style
        ).execute_async()

        if tipo_candidato == "volver":
            return

        clear_screen()
        Ascii_logo()

        # Obtener los puestos de la categoría seleccionada
        puestos_disponibles = MENU_CONFIG['cv_processor_menu']['categories'][tipo_candidato]
        
        # Crear las opciones del menú con nombres formateados
        job_choices = [Separator()]
        for puesto in puestos_disponibles:
            # Formatear el nombre del puesto para mejor presentación
            nombre_formateado = puesto.replace('_', ' ').title()
            job_choices.append(Choice(puesto.lower(), nombre_formateado))
        
        job_choices.extend([
            Separator("\n"),
            Choice("volver", "Volver al menú principal"),
            Separator()
        ])

        # Seleccionar puesto específico
        puesto = await inquirer.select(
            message="   Seleccione el puesto específico a buscar:",
            choices=job_choices,
            default=puestos_disponibles[0].lower(),
            pointer=UI_SYMBOLS['pointer'],
            qmark='',
            style=style
        ).execute_async()

        if puesto == "volver":
            return

        # Verificar que el puesto existe en JOB_PROFILES
        if puesto not in JOB_PROFILES:
            print(f"\n   Error: El puesto '{puesto}' no está definido en los perfiles de trabajo.")
            print(f"   Puestos disponibles: {', '.join(JOB_PROFILES.keys())}")
            await inquirer.text(message="Presione Enter para continuar...", qmark='   >', style=style).execute_async()
            return

        clear_screen()
        Ascii_logo()

        # Obtener nombre del reclutador
        recruiter_name = await inquirer.text(
            message="   Ingrese su nombre (para el mensaje de WhatsApp):",
            default="[Tu nombre]",
            validate=EmptyInputValidator("El nombre no puede estar vacío"),
            style=style
        ).execute_async()

        print("\n   Iniciando procesamiento de CVs...")
        
        # Procesar CVs
        processor = CVProcessor(os.getcwd())
        suitable_candidates = processor.process_all_cvs(puesto, recruiter_name)
        processor.display_results(suitable_candidates, recruiter_name)
        
        if not suitable_candidates:
            print("\n   No se encontraron candidatos aptos para el puesto.")
            print("   Recomendamos iniciar con el proceso de publicación de la vacante en Redes Sociales.")
        
        await inquirer.text(message="Presione Enter para continuar...", qmark='   >', style=style).execute_async()


    @staticmethod
    async def validate_winda_id():
        while True:
            clear_screen()
            Ascii_logo()
            
            email, password = WindaValidator.load_credentials()
            if not email or not password:
                print("\n   Para usar el validador de Winda ID, necesitamos tus credenciales de inicio de sesión.")
                print("   Estas se guardarán de forma segura y se usarán para refrescar las cookies automáticamente.\n")
                email = await inquirer.text(
                    message="Ingrese su email:",
                    qmark="   >",
                    validate=EmptyInputValidator("Este campo no puede estar vacío."),
                    style=style
                ).execute_async()
                password = await inquirer.secret(
                    message="Ingrese su contraseña:",
                    qmark="   >",
                    validate=EmptyInputValidator("Este campo no puede estar vacío."),
                    style=style
                ).execute_async()
                WindaValidator.login_and_save_cookies(email, password)

            clear_screen()
            Ascii_logo()
            print("\n")
            winda_id = await inquirer.text(
                message="Ingrese el Winda ID (o 'q' para volver al menú principal):",
                qmark="   >",
                validate=EmptyInputValidator("Este campo no puede estar vacío."),
                style=style
            ).execute_async()
            
            if winda_id.lower() == 'q':
                set_console_title(f'CJR Toolkit v{LASTVERSION} - Menú Principal')
                break

            print("\n")
            
            data = await WindaValidator.fetch_winda_data(winda_id)
            if data:
                clear_screen()
                formatted_data = []
                for entry in data:
                    valid_to = entry.get('ValidTo', 'N/A')
                    if valid_to != 'N/A':
                        try:
                            valid_to_date = datetime.strptime(valid_to, '%Y-%m-%d').date()
                            days_left = (valid_to_date - datetime.now().date()).days
                            status = f"{days_left} días"
                        except ValueError:
                            status = "Fecha inválida"
                    else:
                        status = "N/A"
                    
                    formatted_entry = {
                        "Winda ID": entry.get('Winda ID', 'N/A'),
                        "Nombre completo": entry.get('Nombre completo', 'N/A'),
                        "País": entry.get('País', 'N/A'),
                        "Título del curso": entry.get('Título del curso', 'N/A'),
                        "Proveedor del curso": entry.get('Proveedor del curso', 'N/A'),
                        "Validez": entry.get('Validez', 'N/A'),
                        "Estatus": status
                    }
                    formatted_data.append(formatted_entry)
                Ascii_logo()
                print("\n    Datos recuperados exitosamente:\n")
                # Acortar los nombres de las columnas para que la tabla sea más angosta
                formatted_data_compact = []
                for entry in formatted_data:
                    compact_entry = {
                        "ID": entry["Winda ID"],
                        "Nombre": entry["Nombre completo"],
                        "País": entry["País"],
                        "Curso": entry["Título del curso"],
                        "Proveedor": entry["Proveedor del curso"],
                        "Validez": entry["Validez"],
                        "Estatus": entry["Estatus"]
                    }
                    formatted_data_compact.append(compact_entry)
                
                table = tabulate(formatted_data_compact, headers="keys", tablefmt="heavy_grid")
                # Centrar cada línea de la tabla individualmente
                centered_table = "\n".join(" " * 4 + line for line in table.split("\n"))
                print(centered_table + "\n")
                if await inquirer.confirm(
                    message=f'   Te gustaría descargar el certificado ahora?',
                    default=True,
                    style=style,
                    qmark='',
                    instruction=''
                ).execute_async():
                    cookies = WindaValidator.load_cookies()
                    person_name = data[0]['Nombre completo']
                    download_certificate(winda_id, cookies, person_name)
            else:
                clear_screen()
                Ascii_logo()
                print("\n     No se pudieron recuperar los datos. Por favor, intente nuevamente.\n")

            await inquirer.text(message="Presione Enter para continuar...", qmark='   >', style=style).execute_async()

    @staticmethod
    async def run():
        await UserInterface.main_menu()

if __name__ == "__main__":
    asyncio.run(UserInterface.run())
