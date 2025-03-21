# automacao.py
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()

EDUCARWEB_URL = "https://fraiburgo.educarweb.net.br"
USUARIO = os.getenv("USUARIO")
SENHA = os.getenv("SENHA")

def iniciar_navegador():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    return driver

def fazer_login(driver):
    driver.get(EDUCARWEB_URL)
    wait = WebDriverWait(driver, 10)

    wait.until(EC.presence_of_element_located((By.ID, "usuario"))).send_keys(USUARIO)
    driver.find_element(By.ID, "senha").send_keys(SENHA)
    driver.find_element(By.ID, "btnlogin").click()

    wait.until(EC.url_contains("selecione-o-portal"))
    portal = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Administrador Do Transporte')]")))
    driver.execute_script("arguments[0].click();", portal)

    wait.until(EC.url_contains("/Home"))

def acessar_matricula_transporte(driver):
    wait = WebDriverWait(driver, 10)

    try:
        driver.implicitly_wait(2)
        menu = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(),'Matrícula')]")))
        driver.execute_script("arguments[0].scrollIntoView();", menu)
        if menu.get_attribute("aria-expanded") == "false":
            driver.execute_script("arguments[0].click();", menu)
        
        transporte = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Matrícula Transporte')]")))
        driver.execute_script("arguments[0].click();", transporte)

        # Espera o campo de pesquisa carregar
        wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'DIGITE AQUI O NOME DA PESSOA')]")))

    except Exception as e:
        print(f"Erro ao acessar Matrícula Transporte: {e}")

def pesquisar_aluno(driver, nome_aluno):
    wait = WebDriverWait(driver, 10)

    try:
        campo = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//input[contains(@placeholder, 'DIGITE AQUI O NOME DA PESSOA')]")
        ))
        campo.clear()
        campo.send_keys(nome_aluno)

        botao = driver.find_element(By.XPATH, "//button[contains(span/text(), 'Pesquisar')]")
        driver.execute_script("arguments[0].click();", botao)
        driver.implicitly_wait(3)

        resultado = driver.find_elements(By.XPATH, "//div[@title='Possui Matrícula']")
        if resultado:
            print(f"✅ {nome_aluno} já está matriculado.")
            return True

        print(f"📌 {nome_aluno} ainda não está matriculado.")
        return False

    except Exception as e:
        print(f"Erro ao pesquisar {nome_aluno}: {e}")
        return False
