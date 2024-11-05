import os
import logging
import comtypes.gen
from dotenv import load_dotenv

load_dotenv()

comtypes_logger = logging.getLogger('comtypes')
comtypes_logger.setLevel(logging.WARNING)

logging.basicConfig(level=logging.INFO)
import sys
import asyncio
import nest_asyncio
import requests
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy import get_style
from system.config import ASCII_ART, LASTVERSION
from codeparts.user_interface import UserInterface, clear_screen, Ascii_logo


nest_asyncio.apply()

style = get_style({"questionmark": "#ff8400", "answer": "#ffffff", "pointer": "#ff8400"}, style_override=False)

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([current_dir, os.path.join(current_dir, 'codeparts'), os.path.join(current_dir, 'system')])

def maximize_console():
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.user32.GetForegroundWindow(), 3)

def check_for_updates():
    try:
        with open(os.path.join(current_dir, "system", "ver.txt"), 'r') as r:
            current_version = r.read().strip()
        
        response = requests.get('https://api.github.com/repos/lil-jrg/cjrtoolkit/releases')
        latest_version = response.json()[0]['tag_name']
        
        if latest_version != current_version:
            if inquirer.confirm(message=f'Nueva versión {latest_version} disponible. ¿Descargar ahora?', default=True, qmark='      >', style=style).execute():
                os.chdir(os.path.abspath(os.path.join(current_dir, os.pardir)))
                os.system('updater.bat')
                sys.exit(0)
    except requests.RequestException as e:
        print(f"No se pudo verificar actualizaciones: {e}")

async def display_ascii_art():
    Ascii_logo()

async def main():
    UserInterface.set_console_title(f'CJR Toolkit v{LASTVERSION} - Checking updates...')
    maximize_console()
    clear_screen()
    await display_ascii_art()
    check_for_updates()
    await UserInterface.run()
    clear_screen()

if __name__ == "__main__":
    asyncio.run(main())
