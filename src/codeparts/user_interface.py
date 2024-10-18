import os
import asyncio
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from InquirerPy import get_style
from InquirerPy.validator import EmptyInputValidator
from codeparts.get_certificate import download_certificate
from tabulate import tabulate
from datetime import datetime
from codeparts.winda_validator import WindaValidator
from codeparts.cv_processor import CVProcessor
from codeparts.pdf_converter import PDFConverter
from system.config import ASCII_ART, LASTVERSION
from termcolor import colored
import colorama

colorama.init()
style = get_style({"questionmark": "#ff8400", "answer": "#ffffff", "pointer": "#ff8400"}, style_override=False)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

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

class UserInterface:
    @staticmethod
    def set_console_title(title: str):
        if os.name == 'nt':
            import ctypes
            ctypes.windll.kernel32.SetConsoleTitleW(title)

    @staticmethod
    async def main_menu():
        UserInterface.set_console_title(f'CJR Toolkit v{LASTVERSION} - Menú Principal')
        while True:
            clear_screen()
            terminal_width = os.get_terminal_size().columns
            centered_ascii_art = center_text(ASCII_ART.format(LASTVERSION), terminal_width)
            colored_ascii_art = color_gradient(centered_ascii_art, '#fff200', '#ff0000', ['#ff4000', '#ff8400'])
            print(colored_ascii_art)
            
            choices = [
                Separator(),
                Choice("validar", "Validar Winda ID"),
                Choice("procesar", "Procesar CVs"),
                Choice("doc", "DOC Utilities"),
                Choice("convert", "PDF Converter"),
                Choice("opcion5", "Opción 5"),
                Choice("opcion6", "Opción 6"),
                Choice("opcion7", "Opción 7"),
                Choice("opcion8", "Opción 8"),
                Choice("opcion9", "Opción 9"),
                Choice("opcion10", "Opción 10"),
                Separator(),
                Choice("salir", "Salir")
            ]

            choice = await inquirer.select(
                message="   (Use las flechas ↑↓ para navegar, Enter para seleccionar)\n\n   Seleccione una opción:",
                choices=choices,
                default="validar",
                pointer="   >",
                qmark='',
                style=style
            ).execute_async()

            if choice == "validar":
                await UserInterface.validate_winda_id()
            elif choice == "procesar":
                await UserInterface.process_cvs_menu()
            elif choice == "doc":
                await UserInterface.doc_utilities()
            elif choice =="convert":
                await UserInterface.convert_file()
            elif choice == "salir":
                clear_screen()
                print("\n   Gracias por usar CJR Toolkit. ¡Hasta luego!")
                break
            else:
                print(f"La opción {choice} aún no está implementada.")
                await asyncio.sleep(2)

    @staticmethod
    async def convert_file():
        UserInterface.set_console_title(f'CJR Toolkit v{LASTVERSION} - File converter')
        while True:
            clear_screen()
            terminal_width = os.get_terminal_size().columns
            centered_ascii_art = center_text(ASCII_ART.format(LASTVERSION), terminal_width)
            colored_ascii_art = color_gradient(centered_ascii_art, '#fff200', '#ff0000', ['#ff4000', '#ff8400'])
            print(colored_ascii_art)
            choice = await inquirer.select(
                message="   (Use las flechas ↑↓ para navegar, Enter para seleccionar)\n\n   Seleccione el tipo de personal: ",
                choices=[
                    Separator(),
                    Choice("ptoword", "PDF --> Word"),
                    Choice("ptoexcel", "PDF --> Excel"),
                    Choice("ptopp", "PDF --> PowerPoint"),
                    Choice("extimg", "Extraer imágenes de PDF"),
                    Choice("alltopdf", "Word, Excel o PowerPoint --> PDF"),
                    Separator(),
                    Choice("volver", "Volver")
                ],
                default="oficina",
                pointer="   >",
                qmark='',
                style=style
            ).execute_async()
        
            
            if choice == "volver":
                clear_screen()
                UserInterface.set_console_title(f'CJR Toolkit v{LASTVERSION} - Menú Principal')
            break

        file_path = PDFConverter.select_file()
        if not file_path:
            print("No se seleccionó ningún archivo.")

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

        print(result)  # This line will display the return message
        await inquirer.text(message="Presione Enter para continuar...").execute_async()

    @staticmethod
    async def validate_winda_id():
        UserInterface.set_console_title(f'CJR Toolkit v{LASTVERSION} - Winda ID token validator')
        while True:
            clear_screen()
            terminal_width = os.get_terminal_size().columns
            centered_ascii_art = center_text(ASCII_ART.format(LASTVERSION), terminal_width)
            colored_ascii_art = color_gradient(centered_ascii_art, '#fff200', '#ff0000', ['#ff4000', '#ff8400'])
            print(colored_ascii_art)
            winda_id = await inquirer.text(
                message="Ingrese el Winda ID (o 'q' para volver al menú principal):",
                qmark="   >",
                validate=EmptyInputValidator("Este campo no puede estar vacío.")
            ).execute_async()
            
            if winda_id.lower() == 'q':
                UserInterface.set_console_title(f'CJR Toolkit v{LASTVERSION} - Menú Principal')
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
                terminal_width = os.get_terminal_size().columns
                centered_ascii_art = center_text(ASCII_ART.format(LASTVERSION), terminal_width)
                colored_ascii_art = color_gradient(centered_ascii_art, '#fff200', '#ff0000', ['#ff4000', '#ff8400'])
                print(colored_ascii_art)
                print("\n    Datos recuperados exitosamente:\n")
                print(center_text(tabulate(formatted_data, headers="keys", tablefmt="grid") + "\n ", terminal_width))
                if inquirer.confirm(
                    message=f'Te gustaría descargarla ahora?',
                    default=True,
                    qmark='      >',
                    style=style
                ).execute():
                    cookies = WindaValidator.load_cookies()
                    download_certificate(winda_id, cookies)
            else:
                clear_screen()
                terminal_width = os.get_terminal_size().columns
                centered_ascii_art = center_text(ASCII_ART.format(LASTVERSION), terminal_width)
                colored_ascii_art = color_gradient(centered_ascii_art, '#fff200', '#ff0000', ['#ff4000', '#ff8400'])
                print(colored_ascii_art)
                print("\n     No se pudieron recuperar los datos. Por favor, intente nuevamente.\n")

            await inquirer.text(message="Presione Enter para continuar...", qmark='   >').execute_async()

    @staticmethod
    async def process_cvs_menu():
        UserInterface.set_console_title(f'CJR Toolkit v{LASTVERSION} - CV Sorter')
        while True:
            clear_screen()
            terminal_width = os.get_terminal_size().columns
            centered_ascii_art = center_text(ASCII_ART.format(LASTVERSION), terminal_width)
            colored_ascii_art = color_gradient(centered_ascii_art, '#fff200', '#ff0000', ['#ff4000', '#ff8400'])
            print(colored_ascii_art)
            
            tipo_personal = await inquirer.select(
                message="   (Use las flechas ↑↓ para navegar, Enter para seleccionar)\n\n   Seleccione el tipo de personal: ",
                choices=[
                    Separator(),
                    Choice("oficina", "Oficina"),
                    Choice("campo", "Campo"),
                    Separator(),
                    Choice("volver", "Volver")
                ],
                default="oficina",
                pointer="   >",
                qmark='',
                style=style
            ).execute_async()

            if tipo_personal == "volver":
                UserInterface.set_console_title(f'CJR Toolkit v{LASTVERSION} - Menú Principal')
                break

            puestos = []

            if tipo_personal == "oficina":
                puestos = [
                    Separator("=== Puestos de Oficina ==="),
                    Choice("recepcionista", "Recepcionista"),
                    Choice("administrador", "Administrador"),
                    Choice("gerente", "Gerente"),
                    Choice("supervisor", "Supervisor"),
                    Choice("contador", "Contador"),
                    Separator("=== Puestos Auxiliares ==="),
                    Choice("auxiliar_recepcionista", "Auxiliar de Recepcionista"),
                    Choice("auxiliar_administrador", "Auxiliar de Administrador"),
                    Choice("auxiliar_gerente", "Auxiliar de Gerente"),
                    Choice("auxiliar_supervisor", "Auxiliar de Supervisor"),
                    Choice("auxiliar_contador", "Auxiliar de Contador"),
                ]
            else:  # campo
                puestos = [
                    Separator("=== Puestos Técnicos ==="),
                    Choice("ingeniero_energia_renovable", "Ingeniero de Energía Renovable"),
                    Choice("tecnico_instalacion", "Técnico de Instalación"),
                    Choice("tecnico_mantenimiento", "Técnico de Mantenimiento"),
                    Separator("=== Puestos de Gestión ==="),
                    Choice("gerente_proyectos", "Gerente de Proyectos de Energía Renovable"),
                    Choice("gerente_desarrollo_negocios", "Gerente de Desarrollo de Negocios de Energías Renovables"),
                    Choice("gerente_operaciones", "Gerente de Operaciones de Energías Renovables"),
                    Separator("=== Puestos de Investigación ==="),
                    Choice("investigador_energia_solar", "Investigador en Energía Solar"),
                    Choice("ingeniero_biomasa", "Ingeniero de Biomasa"),
                    Choice("ingeniero_almacenamiento_energia", "Ingeniero en Almacenamiento de Energía"),
                ]

            puestos.extend([
                Separator(),
                Choice("volver", "Volver")
            ])
            
            puesto = await inquirer.select(
                message="\n   Seleccione el puesto específico: ",
                choices=puestos,
                pointer="   >",
                qmark='',
                style=style
            ).execute_async()

            if puesto == "volver":
                continue

            print(f"Procesando CVs para {tipo_personal} - {puesto}...")
            try:
                resultados = await CVProcessor.process_cv('../Curriculums', tipo_personal, puesto)
                if resultados['top_candidatos']:
                    print("\nTop 3 Candidatos:")
                    for i, candidato in enumerate(resultados['top_candidatos'], 1):
                        print(f"\n{i}. {candidato['nombre']}")
                        print(f"   Teléfono: {candidato['telefono']}")
                        print(f"   Correo: {candidato['correo']}")
                        print(f"   Puntuación: {candidato['puntuacion']:.2f}")
                else:
                    print("\nNo se encontraron candidatos que cumplan con los requisitos mínimos.")
                    print("Se recomienda publicar la vacante en redes sociales para atraer más candidatos calificados.")
                
                print("\nProcesamiento completado.")
            except Exception as e:
                print(f"Error durante el procesamiento: {str(e)}")
            
            await inquirer.text(message="Presione Enter para continuar...").execute_async()

    @staticmethod
    async def doc_utilities():
        UserInterface.set_console_title(f'CJR Toolkit v{LASTVERSION} - DOC Utilities')
        clear_screen()
        terminal_width = os.get_terminal_size().columns
        centered_ascii_art = center_text(ASCII_ART.format(LASTVERSION), terminal_width)
        colored_ascii_art = color_gradient(centered_ascii_art, '#fff200', '#ff0000', ['#ff4000', '#ff8400'])
        print(colored_ascii_art)
        print("\n   Funcionalidad DOC Utilities aún no implementada.\n")
        await inquirer.text(message="Presione Enter para volver al menú principal...", qmark="   >").execute_async()
        UserInterface.set_console_title(f'CJR Toolkit v{LASTVERSION} - Menú Principal')

    @staticmethod
    async def run():
        await UserInterface.main_menu()

if __name__ == "__main__":
    asyncio.run(UserInterface.run())