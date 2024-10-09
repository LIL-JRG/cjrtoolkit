import os

def ensure_directory_exists(directory: str):
    """Asegura que el directorio especificado exista, creándolo si es necesario."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def sanitize_filename(filename: str) -> str:
    """Sanitiza el nombre de archivo para evitar caracteres no permitidos."""
    return "".join([c for c in filename if c.isalpha() or c.isdigit() or c in (' ', '.', '_')]).rstrip()