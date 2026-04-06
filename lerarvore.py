import os
from tkinter import Tk, filedialog


# =========================
# UI: Seleção de pasta
# =========================
def selecionar_pasta():
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    pasta = filedialog.askdirectory(title="Selecione a pasta")
    return pasta


# =========================
# Util: Criar pasta de saída
# =========================
def criar_pasta_saida():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "output")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    return output_dir


# =========================
# Util: Nome do arquivo final
# =========================
def gerar_nome_arquivo(pasta_origem):
    nome_base = os.path.basename(os.path.normpath(pasta_origem))
    return f"{nome_base}.md"


# =========================
# Leitura segura de arquivos
# =========================
def ler_arquivo(caminho):
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "[ERRO AO LER ARQUIVO OU BINÁRIO]"


# =========================
# Core: Gerar conteúdo markdown
# =========================
def gerar_markdown(pasta):
    conteudo_final = []

    for root, dirs, files in os.walk(pasta):
        for file in files:
            caminho_completo = os.path.join(root, file)

            conteudo_final.append(caminho_completo)
            conteudo_final.append("")

            conteudo = ler_arquivo(caminho_completo)
            conteudo_final.append(conteudo)
            conteudo_final.append("\n---\n")

    return "\n".join(conteudo_final)


# =========================
# Escrita do arquivo final
# =========================
def salvar_markdown(output_dir, nome_arquivo, conteudo):
    caminho_saida = os.path.join(output_dir, nome_arquivo)

    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(conteudo)

    return caminho_saida


# =========================
# Pipeline principal
# =========================
def main():
    print("Selecione a pasta...")

    pasta = selecionar_pasta()

    if not pasta:
        print("Nenhuma pasta selecionada.")
        return

    print(f"Pasta selecionada: {pasta}")

    output_dir = criar_pasta_saida()
    nome_arquivo = gerar_nome_arquivo(pasta)

    print("Gerando markdown...")
    conteudo = gerar_markdown(pasta)

    caminho_final = salvar_markdown(output_dir, nome_arquivo, conteudo)

    print(f"\nArquivo gerado com sucesso em:\n{caminho_final}")


# =========================
# Execução
# =========================
if __name__ == "__main__":
    main()