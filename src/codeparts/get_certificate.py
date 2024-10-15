import requests
from system.config import COOKIE_ENCRYPTION_KEY, COOKIES_FILE, LOGIN_URL, SEARCH_URL

# Función para descargar el certificado usando el winda_id y el nombre del participante
def download_certificate(winda_id, cookies):
    # Encabezados para la petición HTTP
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'es-419,es;q=0.9,es-ES;q=0.8,en;q=0.7,en-GB;q=0.6,en-US;q=0.5',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
        'sec-ch-ua': '"Microsoft Edge";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    # Petición para descargar el certificado
    try:
        response = requests.get(
            f'https://winda.globalwindsafety.org/course-participant/download-training-records/{winda_id}',
            cookies=cookies,
            headers=headers,
        )
        response.raise_for_status()  # Asegura que no hubo errores en la petición

        # Guardar el PDF en el directorio "../results/"
        file_path = f"../results/certificate.pdf"
        with open(file_path, "wb") as binary_file:
            binary_file.write(response.content)

        print(f"\n     Se terminó la descarga del PDF: {file_path}\n")
    except requests.exceptions.RequestException as e:
        print(f"\n     Error al descargar el certificado: {e}\n")
