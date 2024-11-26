"""
Utilidades compartidas para la interfaz de usuario
"""
import os
from system.config import LASTVERSION

def set_console_title(title: str) -> None:
    """Establece el título de la consola"""
    if os.name == 'nt':  # Windows
        os.system(f'title {title}')
