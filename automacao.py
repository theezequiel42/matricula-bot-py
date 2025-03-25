# automacao.py

import os
import time
from config import UNIDADE_ESCOLAR, MODALIDADE, DISTANCIA_PADRAO, ESCOLA_MODAL_XPATH, PARADA_PADRAO
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pyautogui

# ⏳ Carrega variáveis de ambiente
load_dotenv()

# 🔐 Constantes de acesso
EDUCARWEB_URL = "https://fraiburgo.educarweb.net.br"
USUARIO = os.getenv("USUARIO")
SENHA = os.getenv("SENHA")

# 🚀 Inicia o navegador com Selenium
def iniciar_navegador():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    return driver

# 🔐 Faz login no sistema EducarWeb
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

# 📂 Acessa o menu Matrícula Transporte
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

        wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'DIGITE AQUI O NOME DA PESSOA')]")))

    except Exception as e:
        print(f"❌ Erro ao acessar Matrícula Transporte: {e}")

# 🔎 Pesquisa se o aluno já possui matrícula
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
        print(f"❌ Erro ao pesquisar {nome_aluno}: {e}")
        return False

# 📝 Inicia o cadastro se o aluno não estiver matriculado
def cadastrar_aluno(driver, aluno):
    wait = WebDriverWait(driver, 10)
    nome_completo = aluno['NOME']
    selecionado = False

    try:
        print(f"\n📝 Iniciando cadastro de {nome_completo}...")

        # 2️⃣ Tentativas com Selenium (exato, parcial, fallback)
        if not selecionado:
            tentativas = [
                f"//div[@class='x-grid-cell-inner' and text()='{nome_completo}']",
                f"//div[@class='x-grid-cell-inner' and contains(text(), '{nome_completo.split()[0]}')]",
                "//table[contains(@class, 'x-grid-table')]//tr[contains(@class, 'x-grid-row')]"
            ]

            for xpath in tentativas:
                try:
                    print(f"🔍 Tentando clicar com Selenium em: {xpath}")
                    elemento = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                    driver.execute_script("arguments[0].scrollIntoView();", elemento)
                    ActionChains(driver).move_to_element(elemento).pause(0.2).click().perform()
                    time.sleep(1)

                    wait.until(EC.element_to_be_clickable((By.ID, "ext-gen1323")))
                    print("✅ Seleção com Selenium funcionou!")
                    selecionado = True
                    break
                except Exception as e:
                    print(f"⚠️ Tentativa com Selenium falhou: {e}")

        # 3️⃣ Se não conseguiu selecionar, aborta
        if not selecionado:
            print(f"🚫 Não foi possível selecionar {nome_completo}. Pulando...")
            return

        # 4️⃣ Clica no botão 'Incluir' e verifica se o modal abriu
        print("🧩 Tentando clicar no botão 'Incluir'...")

        for tentativa in range(2):
            try:
                botao_incluir = wait.until(EC.element_to_be_clickable((By.ID, "ext-gen1323")))
                driver.execute_script("arguments[0].scrollIntoView();", botao_incluir)
                ActionChains(driver).move_to_element(botao_incluir).pause(0.2).click().perform()
                print(f"✅ Botão 'Incluir' clicado (tentativa {tentativa + 1})")
                time.sleep(2)

                # Verifica se o formulário/modal foi realmente aberto
                modal_xpath = "//div[contains(@class,'x-window') and contains(@role, 'dialog')]"
                wait.until(EC.presence_of_element_located((By.XPATH, modal_xpath)))
                print("✅ Modal de matrícula detectado. Continuando...")
                break

            except Exception as e:
                print(f"⚠️ Tentativa {tentativa + 1} falhou ao clicar no botão 'Incluir': {e}")
                if tentativa == 1:
                    print("🚫 Não foi possível abrir o formulário. Pulando este aluno.")
                    return
                time.sleep(1)

        # 5️⃣ Preenche o formulário com PyAutoGUI
        preencher_com_tab(aluno, driver)

    except Exception as e:
        print(f"❌ Erro ao iniciar cadastro de {nome_completo}: {e}")
      
pyautogui.PAUSE = 0.5
pyautogui.FAILSAFE = True

def preencher_com_tab(aluno, driver):
    print(f"📌 Iniciando preenchimento via PyAutoGUI para {aluno['NOME']}")
    wait = WebDriverWait(driver, 10)

    time.sleep(1)  # Aguarda o formulário carregar

    # 1️⃣ Ir do campo "Data de Vencimento" até o campo "Turno"
    print("➡️ Pulando campo 'Data Vencimento' (pressionando TAB 1x)...")
    pyautogui.press('tab')
    time.sleep(1)

    # 2️⃣ Preencher Turno
    turno = aluno["TURNO"].upper()
    turno_mapa = {
        "MATUTINO": "Manhã",
        "VESPERTINO": "Tarde",
        "NOTURNO": "Noite",
        "INTEGRAL": "Integral"
    }
    turno_label = turno_mapa.get(turno, "Integral")

    print(f"🕓 Preenchendo turno: {turno_label}")
    pyautogui.write(turno_label)
    pyautogui.press('enter')
    pyautogui.press('tab')
    time.sleep(1)

    # 3️⃣ Unidade
    print("🏫 Selecionando unidade")
    pyautogui.write(UNIDADE_ESCOLAR)
    time.sleep(1)
    pyautogui.press('down')
    pyautogui.press('enter')
    time.sleep(1)

    # 4️⃣ Modalidade
    print("🎓 Selecionando modalidade")
    pyautogui.write(MODALIDADE)
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(1)

    # 5️⃣ Série
    ano = str(aluno["ANO"]).strip()
    print(f"📚 Selecionando série: {ano} ANO")
    pyautogui.write(f"{ano}")
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(1)

   # 6️⃣ Trajeto
    trajeto_codigo = aluno["LINHA"].strip()
    print(f"🚌 Selecionando trajeto (LINHA): {trajeto_codigo}")
    pyautogui.write(trajeto_codigo)
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    print("📏 Preenchendo PARADA")
    pyautogui.write(PARADA_PADRAO)
    time.sleep(2)
    
    # 🔍 Abrir modal clicando na lupa
    print("🔍 Clicando na lupa para abrir modal...")
    pyautogui.moveTo(808, 600)  # <- Posição da lupa
    pyautogui.click()
    print("⏳ Aguardando modal abrir...")
    time.sleep(4)  # Aumentar se necessário
    
    # Seleciona "escola" usando Selenium
    print("🎯 Localizando 'escola' dentro do modal...")
    escola_xpath = ESCOLA_MODAL_XPATH
    escola_elemento = wait.until(EC.element_to_be_clickable((By.XPATH, escola_xpath)))

    driver.execute_script("arguments[0].scrollIntoView();", escola_elemento)
    ActionChains(driver).move_to_element(escola_elemento).pause(0.2).click().perform()
    print("✅ Escola selecionada!")

    # ✅ Clicar em 'Selecionar'
    print("🖱️ Clicando no botão 'Selecionar'...")
    selecionar_xpath = "//div[contains(@class, 'x7-text-el') and text()='Selecionar']"
    selecionar_botao = wait.until(EC.element_to_be_clickable((By.XPATH, selecionar_xpath)))
    ActionChains(driver).move_to_element(selecionar_botao).pause(0.2).click().perform()
    print("✅ Botão 'Selecionar' clicado!")
    time.sleep(4)

    # 7️⃣ Distância
    print("📏 Localizando campo de distância com Selenium...")

    try:
        campo_distancia = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//input[@name='txtDistanciaEscolaMatriculaTransporte' and @maxlength='5']"))
        )
        driver.execute_script("arguments[0].scrollIntoView();", campo_distancia)
        ActionChains(driver).move_to_element(campo_distancia).pause(0.2).click().perform()

        campo_distancia.clear()
        campo_distancia.send_keys(DISTANCIA_PADRAO)
        print("✅ Distância preenchida com sucesso!")
        time.sleep(1)
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('enter')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        time.sleep(1)
    
    except Exception as e:
        print(f"❌ Erro ao preencher a distância: {e}")

    # 8️⃣ Salvar
    print("💾 Salvando cadastro...")
    pyautogui.press('enter')
    print(f"✅ Cadastro de {aluno['NOME']} finalizado!\n")
    time.sleep(4)