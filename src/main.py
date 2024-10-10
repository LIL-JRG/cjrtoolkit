import os
import sys
import asyncio
import nest_asyncio
nest_asyncio.apply()
import requests
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy import get_style
from system.config import ASCII_ART, LASTVERSION
from codeparts.user_interface import center_text, color_gradient

style = get_style({"questionmark": "#ff8400", "answer": "#ffffff", "pointer": "#ff8400"}, style_override=False)

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, 'codeparts'))
sys.path.append(os.path.join(current_dir, 'system'))

from codeparts.user_interface import UserInterface
from system.config import ASCII_ART

def maximize_console():
    if sys.platform == "win32":
        import ctypes
        user32 = ctypes.windll.user32
        user32.ShowWindow(user32.GetForegroundWindow(), 3)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def check_for_updates():
    try:
        with open(os.path.join(current_dir, "system", "ver.txt"), 'r') as r:
            current_version = r.read().strip()
        
        response = requests.get('https://api.github.com/repos/lil-jrg/cjrtoolkit/releases')
        latest_version = response.json()[0]['tag_name']
        
        if latest_version != current_version:
            print(f"   La nueva versión {latest_version} ya está disponible!")
            if inquirer.confirm(
                message=f'Te gustaría descargarla ahora?',
                default=True,
                qmark='      >',
                style=style
            ).execute():
                parent_path = os.path.abspath(os.path.join(current_dir, os.pardir))
                os.chdir(parent_path)
                os.system(f'{parent_path}/updater.bat')
                sys.exit(0)
    except Exception as e:
        print(f"No se pudo descargar la nueva versión, : {e}")

async def main():
    UserInterface.set_console_title(f'CRT v{LASTVERSION} - Checking updates...')
    maximize_console()
    clear_screen()
    terminal_width = os.get_terminal_size().columns
    centered_ascii_art = center_text(ASCII_ART.format(LASTVERSION), terminal_width)
    colored_ascii_art = color_gradient(centered_ascii_art, '#fff200', '#ff0000', ['#ff4000', '#ff8400'])
    print(colored_ascii_art)    
    check_for_updates()
    await UserInterface.run()
    clear_screen()

if __name__ == "__main__":
    asyncio.run(main())