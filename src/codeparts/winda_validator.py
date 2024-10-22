import os
import json
import logging
import requests
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from cryptography.fernet import Fernet, InvalidToken
from system.config import COOKIE_ENCRYPTION_KEY, COOKIES_FILE, LOGIN_URL, SEARCH_URL, ASSETS_DIR

class WindaValidator:
    @staticmethod
    def setup_driver(headless=False):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--start-maximized")
        try:
            service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            logging.error(f"   Error al inicializar ChromeDriver: {str(e)}")
            return None

    @staticmethod
    def save_cookies(driver):
        cookies = driver.get_cookies()
        fernet = Fernet(COOKIE_ENCRYPTION_KEY)
        encrypted_cookies = fernet.encrypt(json.dumps(cookies).encode())
        os.makedirs(os.path.dirname(COOKIES_FILE), exist_ok=True)
        with open(COOKIES_FILE, 'wb') as file:
            file.write(encrypted_cookies)
        logging.info(f"   Cookies guardadas en {COOKIES_FILE}")

    @staticmethod
    def load_cookies():
        if os.path.exists(COOKIES_FILE):
            try:
                with open(COOKIES_FILE, 'rb') as file:
                    encrypted_cookies = file.read()
                fernet = Fernet(COOKIE_ENCRYPTION_KEY)
                decrypted_cookies = fernet.decrypt(encrypted_cookies)
                cookies = json.loads(decrypted_cookies)
                return {cookie['name']: cookie['value'] for cookie in cookies}
            except (InvalidToken, json.JSONDecodeError) as e:
                logging.error(f"   Error al cargar las cookies: {str(e)}")
                os.remove(COOKIES_FILE)
        return None

    @staticmethod
    def save_credentials(email, password):
        fernet = Fernet(COOKIE_ENCRYPTION_KEY)
        encrypted_credentials = fernet.encrypt(f"{email}:{password}".encode())
        credentials_file = os.path.join(ASSETS_DIR, "credentials.encrypted")
        with open(credentials_file, 'wb') as file:
            file.write(encrypted_credentials)
        logging.info("   Credenciales guardadas de forma segura")

    @staticmethod
    def load_credentials():
        credentials_file = os.path.join(ASSETS_DIR, "credentials.encrypted")
        logging.info(f"Intentando cargar credenciales desde: {credentials_file}")
        if os.path.exists(credentials_file):
            try:
                with open(credentials_file, 'rb') as file:
                    encrypted_credentials = file.read()
                logging.info("Credenciales encriptadas leídas correctamente")
                fernet = Fernet(COOKIE_ENCRYPTION_KEY)
                decrypted_credentials = fernet.decrypt(encrypted_credentials).decode()
                logging.info("Credenciales desencriptadas correctamente")
                email, password = decrypted_credentials.split(':')
                logging.info(f"Credenciales cargadas para el email: {email}")
                return email, password
            except Exception as e:
                logging.error(f"   Error al cargar las credenciales: {str(e)}")
        else:
            logging.error(f"El archivo de credenciales no existe: {credentials_file}")
        return None, None

    @classmethod
    def login_and_save_cookies(cls, email=None, password=None):
        driver = cls.setup_driver()
        if not driver:
            return None
        try:
            driver.get(LOGIN_URL)
            if email and password:
                email_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "Login"))
                )
                password_field = driver.find_element(By.ID, "Password")
                email_field.send_keys(email)
                password_field.send_keys(password)
                cookie_accept = driver.find_element(By.ID,"CybotCookiebotDialogBodyLevelButtonAccept")
                cookie_accept.click()
                login_button = driver.find_element(By.ID, "loginButton")
                login_button.click()
            else:
                logging.info("   Por favor inicie sesión en los próximos 60 segundos...")
                WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, "full-name")))
            
            logging.info("   Inicio de sesión detectado!")
            cls.save_cookies(driver)
            if email and password:
                cls.save_credentials(email, password)
            return cls.load_cookies()
        except Exception as e:
            logging.error(f"   Error durante el proceso de inicio de sesión: {str(e)}")
            return None
        finally:
            driver.quit()

    @classmethod
    def refresh_cookies(cls):
        email, password = cls.load_credentials()
        if email and password:
            logging.info("Credenciales cargadas correctamente")
            driver = cls.setup_driver()
            if not driver:
                logging.error("No se pudo inicializar el driver de Selenium")
                return None
            try:
                driver.get(LOGIN_URL)
                logging.info(f"Navegando a {LOGIN_URL}")
                try:
                    email_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "Login"))
                        )
                    logging.info("Campo de email encontrado")
                except TimeoutException:
                    logging.error("   Tiempo de espera agotado al buscar el campo de email")
                    return None
            
                try:
                    password_field = driver.find_element(By.ID, "Password")
                    logging.info("Campo de contraseña encontrado")
                except NoSuchElementException:
                    logging.error("   No se pudo encontrar el campo de contraseña")
                    return None
            
                email_field.send_keys(email)
                password_field.send_keys(password)
                logging.info("Credenciales ingresadas en los campos")
        
                try:
                    cookie_accept = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonAccept"))
                    )
                    cookie_accept.click()
                    logging.info("Botón de aceptar cookies clickeado")
                except:
                    logging.info("   No se encontró el botón de aceptar cookies o no fue necesario.")
        
                login_button = driver.find_element(By.ID, "loginButton")
                login_button.click()
                logging.info("Botón de login clickeado")
        
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "full-name")))
                logging.info("Login exitoso, elemento 'full-name' encontrado")
                cls.save_cookies(driver)
                logging.info("Cookies guardadas")
                return cls.load_cookies()
            except Exception as e:
                logging.error(f"   Error al refrescar las cookies: {str(e)}")
                return None
            finally:
                driver.quit()
        else:
            logging.error("   No se encontraron credenciales guardadas")
            return None

    @staticmethod
    def make_request(winda_id, cookies):
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://winda.globalwindsafety.org',
            'referer': f'https://winda.globalwindsafety.org/organisation/search/?searchString={winda_id}',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        }
        data = {
            'draw': '1',
            'columns[0][data]': 'WindaId',
            'columns[0][name]': 'WindaId',
            'columns[0][searchable]': 'true',
            'columns[0][orderable]': 'true',
            'columns[0][search][value]': '',
            'columns[0][search][regex]': 'false',
            'columns[1][data]': 'FirstName',
            'columns[1][name]': 'FirstName',
            'columns[1][searchable]': 'true',
            'columns[1][orderable]': 'true',
            'columns[1][search][value]': '',
            'columns[1][search][regex]': 'false',
            'columns[2][data]': 'Surname',
            'columns[2][name]': 'Surname',
            'columns[2][searchable]': 'true',
            'columns[2][orderable]': 'true',
            'columns[2][search][value]': '',
            'columns[2][search][regex]': 'false',
            'columns[3][data]': 'CourseTitle',
            'columns[3][name]': 'CourseTitle',
            'columns[3][searchable]': 'true',
            'columns[3][orderable]': 'true',
            'columns[3][search][value]': '',
            'columns[3][search][regex]': 'false',
            'columns[4][data]': 'CourseCode',
            'columns[4][name]': 'CourseCode',
            'columns[4][searchable]': 'true',
            'columns[4][orderable]': 'true',
            'columns[4][search][value]': '',
            'columns[4][search][regex]': 'false',
            'columns[5][data]': 'TrainingProviderName',
            'columns[5][name]': 'TrainingProviderName',
            'columns[5][searchable]': 'true',
            'columns[5][orderable]': 'true',
            'columns[5][search][value]': '',
            'columns[5][search][regex]': 'false',
            'columns[6][data]': 'Country',
            'columns[6][name]': 'Country',
            'columns[6][searchable]': 'true',
            'columns[6][orderable]': 'true',
            'columns[6][search][value]': '',
            'columns[6][search][regex]': 'false',
            'columns[7][data]': 'CompletionDate',
            'columns[7][name]': 'CompletionDate',
            'columns[7][searchable]': 'true',
            'columns[7][orderable]': 'true',
            'columns[7][search][value]': '',
            'columns[7][search][regex]': 'false',
            'columns[8][data]': 'ValidFrom',
            'columns[8][name]': 'ValidFrom',
            'columns[8][searchable]': 'true',
            'columns[8][orderable]': 'true',
            'columns[8][search][value]': '',
            'columns[8][search][regex]': 'false',
            'columns[9][data]': 'ValidTo',
            'columns[9][name]': 'ValidTo',
            'columns[9][searchable]': 'true',
            'columns[9][orderable]': 'true',
            'columns[9][search][value]': '',
            'columns[9][search][regex]': 'false',
            'columns[10][data]': 'Status',
            'columns[10][name]': 'Status',
            'columns[10][searchable]': 'true',
            'columns[10][orderable]': 'false',
            'columns[10][search][value]': '',
            'columns[10][search][regex]': 'false',
            'order[0][column]': '0',
            'order[0][dir]': 'asc',
            'start': '0',
            'length': '10',
            'search[value]': '',
            'search[regex]': 'false',
            'SearchString': winda_id,
        }
        response = requests.post(SEARCH_URL, cookies=cookies, headers=headers, data=data)
        return response

    @classmethod
    async def fetch_winda_data(cls, winda_id):
        cookies = cls.load_cookies()
        if not cookies:
            logging.info("   No se encontraron cookies válidas. Iniciando proceso de inicio de sesión.")
            cookies = cls.login_and_save_cookies()
            if not cookies:
                logging.error("   No se pudieron obtener las cookies. Saliendo.")
                return None
    
        response = cls.make_request(winda_id, cookies)
        try:
            json_data = response.json()
        except requests.exceptions.JSONDecodeError:
            logging.info("   Error al decodificar JSON. Las cookies pueden haber expirado. Refrescando cookies.")
            cookies = cls.refresh_cookies()
            if not cookies:
                logging.error("   No se pudieron refrescar las cookies. Saliendo.")
                return None
            response = cls.make_request(winda_id, cookies)
            try:
                json_data = response.json()
            except requests.exceptions.JSONDecodeError:
                logging.error("   Error persistente al decodificar JSON. Verifique la conexión o el estado del servidor.")
                return None

        current_date = datetime.now().date()
    
        return [
            {
                "Winda ID": result.get('WindaId', 'N/A'),
                "Nombre completo": f"{result.get('FirstName', '')} {result.get('Surname', '')}".strip() or 'N/A',
                "País": result.get('Country', 'N/A'),
                "Título del curso": result.get('CourseTitle', 'N/A'),
                "Proveedor del curso": result.get('TrainingProviderName', 'N/A'),
                "Validez": f"{result.get('ValidFrom', 'N/A')} - {result.get('ValidTo', 'N/A')}",
                "ValidTo": result.get('ValidTo', 'N/A')
            }
            for result in json_data['data']
        ]