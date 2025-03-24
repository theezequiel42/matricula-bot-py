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

        # 🚫 Trajetos excluídos (sem EEB Gonçalves Dias)
        trajetos_excluidos = [
            "A", "B4", "C10", "C11", "C12", "C13", "C8", "SME 04", "SME 09", "SME 10"
        ]

        # ✅ Todos os trajetos válidos
        trajetos_validos = [
            "A1", "A", "B1", "B2", "B3", "B4", "B5", "B6", "C1", "C2", "C3", "C4", "C5", "C6",
            "C7", "C8", "C9", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17",
            "D1", "D2", "D3", "D4", "D5", "SME 01", "SME 02", "SME 03", "SME 04", "SME 05",
            "SME 06", "SME 07", "SME 08", "SME 09", "SME 10"
        ]

        for aluno in alunos:
            nome = aluno.get("NOME", "").strip()
            linha = aluno.get("LINHA", "").strip().upper()

            if not nome:
                print("⚠️ Nome vazio, pulando...")
                continue

            if not linha:
                print(f"⛔ {nome} está sem trajeto definido — ignorando.")
                continue

            if not any(linha.startswith(t) for t in trajetos_validos):
                print(f"❌ {nome} está com trajeto desconhecido: '{linha}' — ignorando.")
                continue

            if any(linha.startswith(excluido) for excluido in trajetos_excluidos):
                print(f"⛔ {nome} pertence à linha '{linha}' (trajeto excluído) — ignorando.")
                continue

            # ✅ Aluno apto para cadastro
            if not pesquisar_aluno(driver, nome):
                cadastrar_aluno(driver, aluno)

    finally:
        time.sleep(5)
        driver.quit()


if __name__ == "__main__":
    main()
