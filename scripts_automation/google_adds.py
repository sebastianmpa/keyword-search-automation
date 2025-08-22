#PASO 1 IMPORTACIONES
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyautogui
import time
import pickle


def iniciar_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--start-maximized")  
    chrome_options.add_argument("--disable-infobars")  
    chrome_options.add_argument("--disable-extensions")  
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])  
    chrome_options.add_experimental_option("useAutomationExtension", False)  

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 60)  
    return driver, wait


def ir_a_keyword_planner(driver, wait):
    try:
        # Paso 1: Click en Tools
        tools_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Tools']")))
        tools_button.click()
        print("✅ Se hizo clic en 'Tools'.")
        time.sleep(1)
    except Exception as e:
        print(f"❌ No se pudo hacer clic en 'Tools': {e}")
        return

    try:
        # Paso 2: Expandir Planning usando el nuevo selector
        planning_expand = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[normalize-space()='Planning']")))
        planning_expand.click()
        print("✅ Se expandió 'Planning'.")
        time.sleep(1)
    except Exception as e:
        print(f"❌ No se pudo expandir 'Planning': {e}")
        return

    try:
        # Paso 3: Click en Keyword Planner
        keyword_planner_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[normalize-space()='Keyword Planner']")))
        keyword_planner_btn.click()
        print("✅ Se hizo clic en 'Keyword Planner'.")
        time.sleep(1)
    except Exception as e:
        print(f"❌ No se pudo hacer clic en 'Keyword Planner': {e}")
        return

    try:
        # Paso 4: Click en Discover new keywords
        discover_keywords_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Discover new keywords']")))
        discover_keywords_button.click()
        print("✅ Se hizo clic en 'Discover new keywords'.")
    except Exception as e:
        print(f"❌ No se pudo hacer clic en 'Discover new keywords': {e}")



def ir_a_keyword_planner2(driver, wait):
    try:
        # Paso 3: Click en Keyword Planner
        keyword_planner_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[normalize-space()='Keyword Planner']")))
        keyword_planner_btn.click()
        print("✅ Se hizo clic en 'Keyword Planner'.")
        time.sleep(1)
    except Exception as e:
        print(f"❌ No se pudo hacer clic en 'Keyword Planner': {e}")
        return

    try:
        # Paso 4: Click en Discover new keywords
        discover_keywords_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Discover new keywords']")))
        discover_keywords_button.click()
        print("✅ Se hizo clic en 'Discover new keywords'.")
    except Exception as e:
        print(f"❌ No se pudo hacer clic en 'Discover new keywords': {e}")


# ✅ AGREGAR PALABRAS CLAVE EN EL INPUT DEL KEYWORD PLANNER
def agregar_keywords(driver, wait, keywords):
    try:
        # Esperar a que el input esté presente usando el nuevo XPath
        keyword_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Try \"meal delivery\" or \"leather boots\"']")))

        # Ingresar cada palabra clave y presionar ENTER
        for keyword in keywords:
            keyword_input.send_keys(keyword)
            keyword_input.send_keys(Keys.RETURN)
            time.sleep(1)  # Pequeña pausa entre entradas para estabilidad

        print(f"✅ Se ingresaron las palabras clave: {keywords}")

    except Exception as e:
        print(f"❌ No se pudieron ingresar las palabras clave: {e}")

# ✅ AGREGAR URL OPCIONAL PARA FILTRAR PALABRAS CLAVE
def agregar_url_filtro(driver, wait, site_url=None):
    if site_url:
        try:
            # Esperar a que el input de la URL esté presente
            url_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Enter a site to filter unrelated keywords']")))
            
            # Ingresar la URL
            url_input.send_keys(site_url)
            url_input.send_keys(Keys.RETURN)  # Presionar Enter para confirmar

            print(f"✅ Se ingresó la URL de filtrado: {site_url}")

        except Exception as e:
            print(f"❌ No se pudo ingresar la URL de filtrado: {e}")
    else:
        print("ℹ️ No se ingresó ninguna URL de filtrado.")

# ✅ HACER CLIC EN "GET RESULTS"
def obtener_resultados(driver, wait):
    try:
        # 🔍 Ajustar el zoom al 80%
        driver.execute_script("document.body.style.zoom='80%'")
        print("🔍 Zoom ajustado al 80%.")
        # Esperar hasta que el botón sea clickeable
        get_results_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//material-button[contains(@class, 'submit-button')]//material-ripple")))
        
        # Hacer clic en el botón
        get_results_button.click()
        
        print("✅ Se hizo clic en 'Get Results' correctamente.")

    except Exception as e:
        print(f"❌ No se pudo hacer clic en 'Get Results': {e}")


def descargar_keywords_pygui():
    try:
        print("🖱️ Enfocando la ventana del navegador...")

        # 🖥️ Hacer clic en la barra de título para enfocar la ventana
        pyautogui.click(100, 10)  # Ajusta si es necesario

        # 🕒 Pequeña espera para estabilizar
        time.sleep(1)

        print("🖱️ Moviendo el cursor y haciendo clic en el botón de descarga...")

        # 📍 Definir coordenadas del botón en la pantalla
        x, y = 1331, 280  # Ajusta estas coordenadas según tu pantalla

        # 🔍 Mover el cursor a la posición
        pyautogui.moveTo(x, y, duration=1)

        # 🖱️ Simular un clic real con presionar y soltar el mouse
        pyautogui.mouseDown()  # Presionar clic
        time.sleep(0.01)  # Esperar un poco
        pyautogui.mouseUp()  # Soltar clic
        print(f"✅ Clic simulado con mouseDown/mouseUp en las coordenadas ({x}, {y})")

        
        # ⏳ Esperar para ver si ocurre el cambio
        time.sleep(2)

        # ⌨️ Enviar Enter para confirmar la acción
        pyautogui.press("enter")
        print("✅ Enter presionado después del clic.")

        
        
    except Exception as e:
        print(f"❌ No se pudo completar la descarga de keywords con PyAutoGUI: {e}")


# ✅ CERRAR EL NAVEGADOR
def cerrar_navegador(driver):
    time.sleep(10)  
    driver.quit()
    print("🚪 Navegador cerrado correctamente.")

def login_automation_with_cookies(cookie_file=None):
    if cookie_file is None:
        cookie_file = r"C:\scripts\programatic_seo\scripts_automation\new_account_cookies.pkl"
    driver, wait = iniciar_driver()
    driver.get("https://ads.google.com")  # Abre el dominio raíz primero

    # Cargar cookies
    with open(cookie_file, 'rb') as file:
        cookies = pickle.load(file)
        for cookie in cookies:
            cookie.pop('sameSite', None)
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                print(f"⚠️ No se pudo agregar la cookie: {cookie.get('name')} - {e}")

    driver.get("https://ads.google.com/aw/campaigns?ocid=6878459735&euid=1390636465&__u=7102183785&uscid=6878459735&__c=5101490015&authuser=1&workspaceId=0&subid=us-en-awhp-g-aw-c-home-signin-bgc!o2-ahpm-0000000188-0000000001%7C-ahpm-0000000179-0000000001%7C-ahpm-0000000182-0000000001")  # Ahora sí, ve a la página deseada
    time.sleep(5)

    print("✅ Login con cookies realizado. Google Ads debería estar autenticado.")
    return driver, wait

def login_automation(cookie_file=None):
    """
    Login automático usando cookies generados previamente y navega al Keyword Planner.
    """
    driver, wait = login_automation_with_cookies(cookie_file)
    ir_a_keyword_planner(driver, wait)
    return driver, wait



def keyword_planner_automation(driver, wait, keywords, url=None):
    """
    Automatiza el proceso de agregar keywords en el Keyword Planner:
    - Agrega palabras clave
    - Aplica filtros de URL si existen
    - Obtiene los resultados
    - Descarga los datos
    """
    time.sleep(5)
    ir_a_keyword_planner2(driver, wait)
    # Agregar keywords
    agregar_keywords(driver, wait, keywords)

    # Agregar URL opcional si se proporciona
    if url:
        agregar_url_filtro(driver, wait, url)

    # Obtener resultados y descargar datos
    obtener_resultados(driver, wait)
    descargar_keywords_pygui()

    print(f"✅ Automatización completada para: {keywords}")

if __name__ == "__main__":
    driver, wait = login_automation()
    ir_a_keyword_planner2(driver, wait)
    cerrar_navegador(driver)