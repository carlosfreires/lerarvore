import sys
import subprocess
import importlib.util
import importlib
import logging
import os
import site
from pathlib import Path

# ------------------------------------------------------------------------------
# Configuração de logging
# ------------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# Bootstrapper de dependências (auto-instalação com self-reboot)
# ------------------------------------------------------------------------------
def garantir_dependencias():
    """
    Verifica e instala automaticamente as dependências de terceiros necessárias.
    Utiliza um mecanismo de 'self-reboot' para que o interpretador recarregue
    os pacotes recém-instalados no sys.path.
    """
    dependencias = {
        'pypdf': 'pypdf'
    }
    algo_instalado = False

    for modulo, pacote in dependencias.items():
        if importlib.util.find_spec(modulo) is None:
            logger.info(f"Dependência ausente: '{pacote}'. Iniciando instalação...")
            try:
                # 1ª tentativa: instalação padrão no diretório do usuário
                cmd = [sys.executable, "-m", "pip", "install", "--user", pacote]
                subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logger.info(f"'{pacote}' instalado com sucesso (--user).")
                algo_instalado = True
            except subprocess.CalledProcessError:
                logger.warning("Instalação padrão falhou. Tentando com --break-system-packages...")
                try:
                    cmd_fallback = [
                        sys.executable, "-m", "pip", "install",
                        "--user", "--break-system-packages", pacote
                    ]
                    subprocess.check_call(cmd_fallback, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    logger.info(f"'{pacote}' instalado com --break-system-packages.")
                    algo_instalado = True
                except subprocess.CalledProcessError:
                    logger.error(f"Não foi possível instalar '{pacote}'. Instale manualmente.")
                    sys.exit(1)

    # Tkinter é dependência de sistema – verificamos apenas se pode ser importado
    try:
        import tkinter
    except ImportError:
        logger.error("Tkinter não encontrado. Instale-o (ex: sudo apt install python3-tk).")
        sys.exit(1)

    # Se algo foi instalado, reiniciamos o script para recarregar o ambiente Python
    if algo_instalado:
        logger.info("Reiniciando script para carregar novo ambiente (self-reboot)...")
        importlib.invalidate_caches()
        user_site = site.getusersitepackages()
        if user_site not in sys.path:
            sys.path.append(user_site)
        os.execv(sys.executable, [sys.executable] + sys.argv)

# Executa o bootstrapper ANTES de qualquer import de terceiros
garantir_dependencias()

# ------------------------------------------------------------------------------
# Imports seguros (agora as dependências estão garantidas)
# ------------------------------------------------------------------------------
from tkinter import Tk, filedialog
import pypdf

# ------------------------------------------------------------------------------
# Classe principal: conversor de árvore de diretórios para Markdown
# ------------------------------------------------------------------------------
class CodebaseToMarkdownConverter:
    """
    Varre recursivamente um diretório, lê TODOS os arquivos (texto, PDF e binários),
    e gera um único arquivo Markdown consolidado para documentação.
    Ao final, adiciona uma árvore de diretórios completa (estilo `tree`).
    """

    # Pastas que devem ser ignoradas durante a varredura
    PASTAS_IGNORADAS = {
        '.git', 'node_modules', 'venv', '.venv', '__pycache__',
        '.nx', '.vscode', 'dist', 'build', '.idea'
    }

    # Mapeamento de extensão -> linguagem para realce de sintaxe no Markdown
    EXTENSAO_PARA_LINGUAGEM = {
        '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
        '.html': 'html', '.css': 'css', '.c': 'c', '.cpp': 'cpp',
        '.cs': 'csharp', '.java': 'java', '.r': 'r', '.json': 'json',
        '.md': 'markdown', '.sql': 'sql', '.yaml': 'yaml', '.yml': 'yaml',
        '.sh': 'bash', '.bat': 'batch', '.txt': 'text',
        '.mts': 'typescript', '.mjs': 'javascript',
        '.env': 'text', '.gitignore': 'text', '.example': 'text',
        '.dockerfile': 'dockerfile', '.toml': 'toml', '.ini': 'ini',
        '.cfg': 'ini', '.conf': 'ini', '.xml': 'xml', '.svg': 'xml',
        '.rst': 'rst', '.tex': 'latex', '.bib': 'bibtex',
    }

    # Mapeamento de nome exato do arquivo -> linguagem (para arquivos sem extensão)
    NOME_PARA_LINGUAGEM = {
        'dockerfile': 'dockerfile',
        'makefile': 'makefile',
        '.gitignore': 'text',
        '.gitattributes': 'text',
        '.editorconfig': 'ini',
        '.env': 'text',
        '.env.example': 'text',
        'license': 'text',
        'readme': 'markdown',
    }

    def __init__(self, output_dir: str = "output"):
        """
        Inicializa o conversor.

        Args:
            output_dir: Nome do diretório de saída (relativo ao script).
        """
        self.diretorio_script = Path(__file__).resolve().parent
        self.diretorio_saida = self.diretorio_script / output_dir
        self.diretorio_saida.mkdir(parents=True, exist_ok=True)

    def obter_pasta_origem(self) -> Path | None:
        """
        Determina a pasta alvo, primeiro por argumento de linha de comando,
        depois via diálogo gráfico (Tkinter) com confirmação interativa para
        evitar erros de seleção do diretório pai.

        Returns:
            Caminho absoluto da pasta escolhida ou None se cancelado.
        """
        if len(sys.argv) >= 3 and sys.argv[1] == '--dir':
            caminho = Path(sys.argv[2]).resolve()
            if not caminho.is_dir():
                logger.error(f"O caminho fornecido não é um diretório: {caminho}")
                sys.exit(1)
            logger.info(f"📁 Usando diretório via argumento: {caminho}")
            return caminho

        while True:
            try:
                print("ℹ️  Importante: navegue até **dentro** da pasta desejada e clique em 'Selecionar pasta'.")
                root = Tk()
                root.withdraw()
                root.attributes('-topmost', True)
                pasta_str = filedialog.askdirectory(title="Selecione a pasta com o código")
                root.destroy()
                if not pasta_str:
                    return None

                caminho = Path(pasta_str).resolve()
                print(f"\n📁 Pasta selecionada: {caminho}")
                confirma = input("✔️  Este é o diretório correto? (S/n): ").strip().lower()
                if confirma in ('', 's', 'sim', 'y', 'yes'):
                    return caminho
                else:
                    manual = input("📝 Digite o caminho absoluto correto (ou 'cancelar' para sair): ").strip()
                    if manual.lower() == 'cancelar':
                        return None
                    caminho_manual = Path(manual).resolve()
                    if caminho_manual.is_dir():
                        return caminho_manual
                    else:
                        print("❌ Caminho inválido. Tente novamente.\n")
            except Exception as e:
                logger.error(f"Erro ao abrir diálogo gráfico: {e}")
                logger.info("Use '--dir <caminho>' para especificar a pasta manualmente.")
                sys.exit(1)

    def ler_arquivo(self, caminho: Path) -> str:
        """
        Lê o conteúdo de um arquivo, tratando texto e PDFs.
        Para arquivos que não podem ser decodificados como texto,
        retorna uma mensagem de conteúdo binário.

        Args:
            caminho: Caminho do arquivo.

        Returns:
            Conteúdo textual ou mensagem de erro/binário.
        """
        if not caminho.exists():
            return f"[ARQUIVO NÃO ENCONTRADO: {caminho}]"

        if caminho.suffix.lower() == '.pdf':
            return self._ler_pdf(caminho)

        # Tenta múltiplas codificações comuns
        for encoding in ('utf-8', 'latin-1', 'cp1252', 'iso-8859-15', 'utf-16'):
            try:
                with open(caminho, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
            except PermissionError:
                return "[PERMISSÃO NEGADA]"
            except Exception as e:
                return f"[ERRO AO LER ARQUIVO: {e}]"

        # Se nenhuma codificação funcionou, consideramos binário
        return "[ARQUIVO BINÁRIO – CONTEÚDO NÃO TEXTUAL]"

    def _ler_pdf(self, caminho: Path) -> str:
        """
        Extrai texto de um PDF usando a biblioteca pypdf.

        Args:
            caminho: Caminho do arquivo PDF.

        Returns:
            Texto extraído ou mensagem de erro.
        """
        try:
            with open(caminho, 'rb') as f:
                leitor = pypdf.PdfReader(f)
                paginas = []
                for i, pagina in enumerate(leitor.pages):
                    texto = pagina.extract_text()
                    if texto:
                        paginas.append(f"--- Página {i+1} ---\n{texto}")
            if paginas:
                return "\n".join(paginas)
            return "[PDF SEM TEXTO EXTRAÍVEL (possível imagem escaneada)]"
        except Exception as e:
            return f"[ERRO AO PROCESSAR PDF: {e}]"

    def obter_linguagem_markdown(self, caminho: Path) -> str:
        """
        Retorna o identificador de linguagem para blocos de código Markdown.
        Primeiro verifica o nome exato do arquivo (para Dockerfile, etc.),
        depois a extensão.

        Args:
            caminho: Caminho completo do arquivo.

        Returns:
            String com o nome da linguagem.
        """
        nome = caminho.name.lower()
        if nome in self.NOME_PARA_LINGUAGEM:
            return self.NOME_PARA_LINGUAGEM[nome]

        # Tratamento para dupla extensão (ex: .env.example)
        if caminho.suffixes:
            for sufixo in reversed(caminho.suffixes):
                linguagem = self.EXTENSAO_PARA_LINGUAGEM.get(sufixo.lower())
                if linguagem:
                    return linguagem

        # Fallback para a última extensão
        extensao = caminho.suffix.lower()
        return self.EXTENSAO_PARA_LINGUAGEM.get(extensao, 'text')

    def gerar_arvore(self, diretorio: Path, prefixo: str = "") -> str:
        """
        Gera uma representação em árvore (estilo comando tree) do diretório,
        listando todos os arquivos e diretórios, ignorando pastas excluídas.

        Args:
            diretorio: Caminho do diretório raiz.
            prefixo: Prefixo usado na recursão para desenho das linhas.

        Returns:
            String multilinha formatada corretamente.
        """
        linhas = []
        try:
            itens = sorted(diretorio.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        except PermissionError:
            return f"{prefixo}[PERMISSÃO NEGADA]\n"

        # Filtra pastas ignoradas
        itens_visiveis = [item for item in itens if not (item.is_dir() and item.name in self.PASTAS_IGNORADAS)]

        total = len(itens_visiveis)
        for indice, item in enumerate(itens_visiveis):
            eh_ultimo = (indice == total - 1)
            conector = "└── " if eh_ultimo else "├── "
            linhas.append(f"{prefixo}{conector}{item.name}")

            if item.is_dir():
                novo_prefixo = prefixo + ("    " if eh_ultimo else "│   ")
                sub_arvore = self.gerar_arvore(item, novo_prefixo)
                if sub_arvore:
                    linhas.append(sub_arvore)

        return "\n".join(linhas) + ("\n" if linhas else "")

    def executar(self) -> None:
        """
        Pipeline principal: seleciona pasta, varre TODOS os arquivos,
        gera o Markdown e adiciona a árvore de diretórios no final.
        """
        logger.info("🔍 Aguardando seleção da pasta de origem...")
        pasta_origem = self.obter_pasta_origem()
        if not pasta_origem:
            logger.warning("Nenhuma pasta selecionada. Encerrando.")
            return

        print(f"\n🔎 Iniciando varredura em: {pasta_origem}")
        logger.info(f"Iniciando varredura em: {pasta_origem}")

        nome_saida = f"{pasta_origem.name}.md"
        caminho_saida = self.diretorio_saida / nome_saida

        linhas_markdown = [f"# Documentação da Base de Código: `{pasta_origem.name}`\n\n"]
        arquivos_processados = 0

        # Percorre recursivamente todos os arquivos (sem filtro de extensão)
        for item in pasta_origem.rglob('*'):
            if not item.is_file():
                continue

            # Ignora arquivos dentro de pastas proibidas
            if any(pasta in item.parts for pasta in self.PASTAS_IGNORADAS):
                continue

            relativo = item.relative_to(pasta_origem)
            linguagem = self.obter_linguagem_markdown(item)
            conteudo = self.ler_arquivo(item)

            # Cabeçalho com caminho relativo
            linhas_markdown.append(f"## `/{relativo}`\n")

            if item.suffix.lower() == '.pdf':
                linhas_markdown.append("**[Documento PDF]**\n")
                linhas_markdown.append(conteudo)
                linhas_markdown.append("\n\n---\n\n")
            elif conteudo.startswith("[ARQUIVO BINÁRIO"):
                # Arquivo binário: registra a informação mas não tenta exibir conteúdo
                linhas_markdown.append("**[Arquivo Binário]**\n")
                linhas_markdown.append(f"*{conteudo}*\n")
                linhas_markdown.append("\n---\n\n")
            else:
                linhas_markdown.append(f"```{linguagem}\n")
                linhas_markdown.append(conteudo)
                linhas_markdown.append("\n```\n\n---\n\n")

            arquivos_processados += 1

        # Geração da árvore de diretórios (inclui todos os itens, sem filtro)
        arvore_str = self.gerar_arvore(pasta_origem)
        linhas_markdown.append("\n## 📂 Estrutura Completa de Arquivos\n\n")
        linhas_markdown.append("```text\n")
        linhas_markdown.append(f"{pasta_origem.name}/\n")
        linhas_markdown.append(arvore_str)
        linhas_markdown.append("```\n")

        # Escreve o arquivo Markdown consolidado
        try:
            with open(caminho_saida, 'w', encoding='utf-8') as f:
                f.write("".join(linhas_markdown))
            print(f"\n✅ Sucesso! {arquivos_processados} arquivos indexados.")
            print(f"📂 Markdown gerado em: {caminho_saida}")
            logger.info(f"✅ Sucesso! {arquivos_processados} arquivos indexados.")
            logger.info(f"📂 Markdown gerado em: {caminho_saida}")
        except Exception as e:
            logger.error(f"❌ Falha ao escrever o arquivo de saída: {e}")
            return

        # Exibição elegante da árvore no terminal
        print(f"\n🌳 Estrutura de diretórios gerada:\n")
        print(f"{pasta_origem.name}/")
        print(arvore_str)

# ------------------------------------------------------------------------------
# Ponto de entrada
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        conversor = CodebaseToMarkdownConverter()
        conversor.executar()
    except Exception as e:
        logger.error(f"Erro inesperado: {e}", exc_info=True)
        sys.exit(1)