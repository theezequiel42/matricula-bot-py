# main.py
from automacao import iniciar_navegador, fazer_login, acessar_matricula_transporte, pesquisar_aluno, cadastrar_aluno
from dados import ler_csv
import time

def main():
    driver = iniciar_navegador()
    try:
        fazer_login(driver)
        acessar_matricula_transporte(driver)

        alunos = ler_csv("data/alunos.csv")

        for aluno in alunos:
            nome = aluno.get("NOME", "").strip()
            if not nome:
                print("⚠️ Nome vazio, pulando...")
                continue

            if not pesquisar_aluno(driver, nome):
                cadastrar_aluno(driver, aluno)

    finally:
        time.sleep(5)
        driver.quit()

if __name__ == "__main__":
    main()
