import os
import sys
import asyncio
import nest_asyncio
import requests
from InquirerPy import inquirer
from InquirerPy import get_style
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from system.config import (
    MENU_CONFIG,
    INQUIRER_STYLE,
    UI_SYMBOLS,
    LASTVERSION,
    Ascii_logo,
    clear_screen,
    set_console_title
)
from codeparts.user_interface import UserInterface

nest_asyncio.apply()

style = get_style(INQUIRER_STYLE)

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([current_dir, os.path.join(current_dir, 'codeparts'), os.path.join(current_dir, 'system')])

def maximize_console():
    """Maximiza la ventana de la consola"""
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.user32.GetForegroundWindow(), 3)

def check_for_updates():
    """Verifica si hay actualizaciones disponibles"""
    try:
        with open(os.path.join(current_dir, "system", "ver.txt"), 'r') as r:
            current_version = r.read().strip()
        
        response = requests.get('https://api.github.com/repos/lil-jrg/cjrtoolkit/releases')
        latest_version = response.json()[0]['tag_name']
        
        if latest_version != current_version:
            update = inquirer.confirm(
                message=f'   Nueva versión {latest_version} disponible. ¿Descargar ahora?',
                default=True,
                qmark='',
                style=style
            ).execute()
            
            if update:
                os.chdir(os.path.abspath(os.path.join(current_dir, os.pardir)))
                os.system('updater.bat')
                sys.exit(0)
    except Exception as e:
        print(f"   No se pudo verificar actualizaciones: {e}")

async def main():
    """Función principal"""
    set_console_title(f'CJR Toolkit v{LASTVERSION} - Checking updates...')
    maximize_console()
    clear_screen()
    Ascii_logo()
    check_for_updates()
    
    # Iniciar la interfaz de usuario
    ui = UserInterface()
    await ui.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
