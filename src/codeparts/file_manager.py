import os
import logging
from datetime import datetime, timedelta

class FileManager:
    @staticmethod
    async def clean_old_files(directory: str, days: int = 30):
        cutoff = datetime.now() - timedelta(days=days)
        for root, dirs, files in os.walk(directory):
            for file in files:
                filepath = os.path.join(root, file)
                file_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
                if file_modified < cutoff:
                    logging.info(f"Eliminando archivo antiguo: {filepath}")
                    os.remove(filepath)