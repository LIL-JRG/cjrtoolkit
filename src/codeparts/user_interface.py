import os
import asyncio
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from tabulate import tabulate
from datetime import datetime
from codeparts.winda_validator import WindaValidator
from codeparts.cv_processor import CVProcessor
from system.config import ASCII_ART, LASTVERSION
from termcolor import colored
import colorama

colorama.init()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def center_text(text, width):
    lines = text.split('\n')
    centered_lines = [line.center(width) for line in lines]
    return '\n'.join(centered_lines)

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
        if os.name == 'nt':  # Solo para Windows
            import ctypes
            ctypes.windll.kernel32.SetConsoleTitleW(title)

    @staticmethod
    async def main_menu():
        UserInterface.set_console_title('CRT v1.0 - Menú Principal')
        while True:
            clear_screen()
            terminal_width = os.get_terminal_size().columns
            centered_ascii_art = center_text(ASCII_ART.format(LASTVERSION), terminal_width)
            #colored_ascii_art = color_gradient(centered_ascii_art, '#0000FF', '#00FF00', ['#FF0000', '#FFD700'])
            colored_ascii_art = color_gradient(centered_ascii_art, '#fff200', '#ff0000', ['#ff4000', '#ff8400'])
            print(colored_ascii_art)
            
            choices = [
                Separator(),
                Choice("validar", "Validar Winda ID"),
                Choice("procesar", "Procesar CVs"),
                Choice("doc", "DOC Utilities"),
                Choice("opcion4", "Opción 4"),
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
                pointer="   >",  # Tres espacios antes del '>' para separarlo del borde
                qmark='',
            ).execute_async()

            if choice == "validar":
                await UserInterface.validate_winda_id()
            elif choice == "procesar":
                await UserInterface.process_cvs_menu()
            elif choice == "doc":
                await UserInterface.doc_utilities()
            elif choice == "salir":
                clear_screen()
                break
            else:
                print(f"La opción {choice} aún no está implementada.")
                await asyncio.sleep(2)

    @staticmethod
    async def validate_winda_id():
        UserInterface.set_console_title('CRT v1.0 - Winda ID token validator')
        while True:
            clear_screen()
            winda_id = await inquirer.text(
                message="Ingrese el Winda ID (o 'q' para volver al menú principal):"
            ).execute_async()
            
            if winda_id.lower() == 'q':
                break

            print(f"Buscando datos para el ID de Winda: {winda_id}")
            
            data = await WindaValidator.fetch_winda_data(winda_id)
            if data:
                clear_screen()
                print("Datos recuperados exitosamente:")
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
                print(tabulate(formatted_data, headers="keys", tablefmt="grid"))
            else:
                print("No se pudieron recuperar los datos. Por favor, intente nuevamente.")

            await inquirer.text(message="Presione Enter para continuar...").execute_async()

    @staticmethod
    async def process_cvs_menu():
        UserInterface.set_console_title('CRT v1.0 - CV Sorter')
        while True:
            clear_screen()
            choice = await inquirer.select(
                message="Seleccione el tipo de personal: ",
                choices=[
                    Choice("oficina", "Oficina"),
                    Choice("campo", "Campo"),
                    Choice("volver", "Volver al menú principal")
                ],
                default="oficina",
                pointer=">",
                qmark=''
            ).execute_async()

            if choice == "volver":
                break

            print(f"Procesando CVs para {choice}...")
            try:
                await CVProcessor.process_cv('Curriculums', choice.capitalize())
                print("Procesamiento completado.")
            except Exception as e:
                print(f"Error durante el procesamiento: {str(e)}")
            
            await inquirer.text(message="Presione Enter para continuar...").execute_async()

    @staticmethod
    async def doc_utilities():
        UserInterface.set_console_title('CRT v1.0 - DOC Utilities')
        clear_screen()
        print("Funcionalidad DOC Utilities aún no implementada.")
        await inquirer.text(message="Presione Enter para volver al menú principal...").execute_async()

    @staticmethod
    async def run():
        await UserInterface.main_menu()