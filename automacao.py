# automacao.py

import os
import time
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

    try:
        print(f"\n📝 Iniciando cadastro de {aluno['NOME']}...")

        nome_completo = aluno['NOME']
        selecionado = False

        # 1️⃣ Tentativas de clique: exato, parcial e fallback
        tentativas = [
            f"//div[@class='x-grid-cell-inner' and text()='{nome_completo}']",
            f"//div[@class='x-grid-cell-inner' and contains(text(), '{nome_completo.split()[0]}')]",
            "//table[contains(@class, 'x-grid-table')]//tr[contains(@class, 'x-grid-row')]"
        ]

        for tentativa_xpath in tentativas:
            try:
                print(f"🔍 Tentando clicar em: {tentativa_xpath}")
                elemento = wait.until(EC.element_to_be_clickable((By.XPATH, tentativa_xpath)))
                driver.execute_script("arguments[0].scrollIntoView();", elemento)
                ActionChains(driver).move_to_element(elemento).pause(0.2).click().perform()
                time.sleep(1)

                # ✅ Verifica se o botão 'Incluir' está habilitado
                try:
                    wait.until(EC.element_to_be_clickable((By.ID, "ext-gen1323")))
                    print("✅ Aluno realmente selecionado! Botão 'Incluir' habilitado.")
                    selecionado = True
                    break
                except:
                    print("⚠️ Botão 'Incluir' não habilitado após o clique.")

            except Exception as e:
                print(f"⚠️ Falha na tentativa: {e}")

        # ❌ Se não selecionou, aborta
        if not selecionado:
            print(f"🚫 Não foi possível selecionar {nome_completo}. Pulando para o próximo.")
            return

        # 2️⃣ Clica no botão "Incluir" com verificação de modal
        print("🧩 Tentando clicar no botão 'Incluir'...")

        for tentativa in range(2):
            try:
                botao_incluir = wait.until(EC.element_to_be_clickable((By.ID, "ext-gen1323")))
                driver.execute_script("arguments[0].scrollIntoView();", botao_incluir)
                ActionChains(driver).move_to_element(botao_incluir).pause(0.2).click().perform()
                print(f"✅ Clique no botão 'Incluir' (tentativa {tentativa + 1})")
                time.sleep(2)

                # 3️⃣ Confirma se o formulário/modal apareceu
                modal_xpath = "//div[contains(@class,'x-window') and contains(@role, 'dialog')]"
                wait.until(EC.presence_of_element_located((By.XPATH, modal_xpath)))
                print("✅ Modal de matrícula detectado. Continuando...")
                break

            except Exception as e:
                print(f"⚠️ Tentativa {tentativa + 1} falhou ao clicar no botão 'Incluir': {e}")
                if tentativa == 1:
                    print("🚫 Não foi possível abrir o formulário. Pulando este aluno.")
                    return
                else:
                    time.sleep(1)

        # 3️⃣ Preenche o formulário com PyAutoGUI
        preencher_com_tab(aluno)

    except Exception as e:
        print(f"❌ Erro ao iniciar cadastro de {aluno['NOME']}: {e}")

# 📋 Preenche o formulário de cadastro do aluno
def preencher_formulario(driver, aluno):
    wait = WebDriverWait(driver, 10)

    turnos_map = {
        "MATUTINO": "Manhã",
        "VESPERTINO": "Tarde",
        "NOTURNO": "Noite",
        "INTEGRAL": "Integral"
    }

    try:
        print("📌 Entrou na função preencher_formulario()")
        print("⏳ Aguardando modal do formulário...")

        modal = wait.until(EC.presence_of_element_located((
            By.XPATH, "//div[contains(@class,'x-window') and contains(@role, 'dialog')]"
        )))
        wait.until(EC.visibility_of(modal))
        print("✅ Modal do formulário carregado!")

        # 1️⃣ Selecionar Turno
        print("🔍 Buscando dropdown de turno...")
        dropdown_turno = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//div[contains(@class, 'x-form-arrow-trigger') and @role='button']"
        )))
        dropdown_turno.click()
        time.sleep(1)

        turno_normalizado = aluno["TURNO"].upper()
        turno_label = turnos_map.get(turno_normalizado, "Integral")

        print(f"⌛ Buscando opção do turno: {turno_label}")
        opcao_turno = wait.until(EC.presence_of_element_located((
            By.XPATH, f"//li[contains(text(),'{turno_label}')]"
        )))
        driver.execute_script("arguments[0].scrollIntoView(true);", opcao_turno)
        wait.until(EC.element_to_be_clickable((
            By.XPATH, f"//li[contains(text(),'{turno_label}')]"
        )))
        driver.execute_script("arguments[0].click();", opcao_turno)
        print(f"✅ Turno '{turno_label}' selecionado com JS!")

        # 2️⃣ Selecionar Unidade Escolar
        print("🔍 Fechando dropdown anterior clicando no botão da unidade...")
        dropdown_unidade_botao = wait.until(EC.element_to_be_clickable((By.ID, "ext-gen1811")))
        driver.execute_script("arguments[0].click();", dropdown_unidade_botao)
        time.sleep(1)

        print("🔍 Aguardando lista de unidades aparecer...")
        lista_unidade = wait.until(EC.presence_of_element_located((
            By.XPATH, "//li[contains(text(),'EEB GONÇALVES DIAS')]"
        )))
        driver.execute_script("arguments[0].scrollIntoView(true);", lista_unidade)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", lista_unidade)
        print("✅ Unidade selecionada!")

        # 3️⃣ Modalidade
        print("🔍 Selecionando modalidade...")
        dropdown_modalidade = wait.until(EC.element_to_be_clickable((By.ID, "ext-gen1801")))
        dropdown_modalidade.click()
        time.sleep(1)

        modalidade_opcao = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//li[contains(text(),'MÉDIO')]")
        ))
        modalidade_opcao.click()
        print("✅ Modalidade selecionada!")

        # 4️⃣ Série
        print(f"🔍 Selecionando série: {aluno['ANO']} ANO")
        dropdown_serie = wait.until(EC.element_to_be_clickable((By.ID, "ext-gen1810")))
        dropdown_serie.click()
        time.sleep(1)

        serie_ano = str(aluno["ANO"]).strip()
        serie_opcao = wait.until(EC.element_to_be_clickable(
            (By.XPATH, f"//li[contains(text(),'{serie_ano} ANO')]")
        ))
        serie_opcao.click()
        print(f"✅ Série {serie_ano} ANO selecionada!")

        # 5️⃣ Trajeto
        print("🔍 Selecionando trajeto...")
        dropdown_trajeto = wait.until(EC.element_to_be_clickable((By.ID, "ext-gen1814")))
        dropdown_trajeto.click()
        time.sleep(1)

        turno_tag = {
            "MATUTINO": ["(M)", "(M/V)"],
            "VESPERTINO": ["(V)", "(M/V)"],
            "NOTURNO": ["(N)"],
            "INTEGRAL": ["(M)", "(V)", "(M/V)"]
        }.get(turno_normalizado, ["(M)", "(V)", "(M/V)"])

        for tag in turno_tag:
            try:
                trajeto_opcao = wait.until(EC.element_to_be_clickable((
                    By.XPATH,
                    f"//li[contains(text(),'{aluno['LOCALIDADE']}') and contains(text(),'{tag}')]"
                )))
                trajeto_opcao.click()
                print(f"✅ Trajeto com tag '{tag}' selecionado!")
                break
            except:
                continue
        else:
            print("⚠️ Nenhum trajeto encontrado para a localidade/turno. Pulando trajeto.")

        # 6️⃣ Distância
        print("🔍 Preenchendo distância...")
        campo_distancia = wait.until(EC.presence_of_element_located((By.ID, "ext-gen1863")))
        campo_distancia.clear()
        campo_distancia.send_keys("5")
        print("✅ Distância preenchida!")

        # 7️⃣ Salvar
        print("🔍 Clicando em salvar...")
        botao_salvar = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Salvar']")))
        driver.execute_script("arguments[0].click();", botao_salvar)
        print(f"✅ Matrícula de {aluno['NOME']} salva com sucesso!")

    except Exception as e:
        print(f"❌ Erro ao preencher o formulário para {aluno['NOME']}: {e}")
        
pyautogui.PAUSE = 0.5
pyautogui.FAILSAFE = True

def preencher_com_tab(aluno):
    print(f"📌 Iniciando preenchimento via PyAutoGUI para {aluno['NOME']}")

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
    print("🏫 Selecionando unidade: EEB GONÇALVES DIAS")
    pyautogui.write("EEB G")
    time.sleep(1)
    pyautogui.press('down')
    pyautogui.press('enter')
    time.sleep(1)

    # 4️⃣ Modalidade
    print("🎓 Selecionando modalidade: MÉDIO")
    pyautogui.write("M")
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
    print("📏 Preenchendo PARADA: 5")
    pyautogui.write("5")
    time.sleep(2)
    # 🔍 Abrir modal clicando na lupa
    print("🔍 Clicando na lupa para abrir modal...")
    pyautogui.moveTo(808, 600)  # <- Posição da lupa
    pyautogui.click()
    print("⏳ Aguardando modal abrir...")
    time.sleep(4)  # Aumentar se necessário

    # ✅ Clicar em 'Selecionar'
    print("✅ Clicando no botão 'Selecionar' do modal...")
    pyautogui.moveTo(1178, 942)  # Posição do botão
    pyautogui.click()
    time.sleep(4)

    # 7️⃣ Distância
    pyautogui.moveTo(730, 800)
    pyautogui.click()
    time.sleep(2)
    print("📏 Preenchendo distância: 5")
    pyautogui.write("5")
    time.sleep(1)
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('enter')
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('tab')
    time.sleep(1)

    # 8️⃣ Salvar
    print("💾 Salvando cadastro...")
    pyautogui.press('enter')
    print(f"✅ Cadastro de {aluno['NOME']} finalizado!\n")
    time.sleep(4)