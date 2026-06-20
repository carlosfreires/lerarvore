# 🌳 lerarvore

**lerarvore** é uma ferramenta de linha de comando (com interface gráfica opcional) que varre recursivamente um diretório de código‑fonte, extrai o conteúdo de arquivos de texto e PDFs e gera um único arquivo Markdown consolidado para documentação, análise ou arquivamento.

Além disso, ao final do Markdown é incluída uma **árvore completa de diretórios e arquivos**, similar ao comando `tree` do Linux, facilitando a visualização da estrutura do projeto.

---

## ✨ Funcionalidades

- 📁 **Seleção de pasta** via janela gráfica (Tkinter) ou argumento `--dir`
- 📄 **Leitura de múltiplos formatos**: TypeScript, JavaScript, Python, HTML, CSS, C/C++, Java, JSON, YAML, Markdown, PDF e muitos outros
- 📑 **Extração de texto de PDFs** com a biblioteca `pypdf`
- 🚫 **Ignora pastas automaticamente**: `node_modules`, `.git`, `venv`, `__pycache__`, `.nx`, `dist`, `build`, etc.
- 🌲 **Geração de árvore completa** da estrutura de diretórios ao final do Markdown
- 🧠 **Auto‑instalação de dependências** – o `pypdf` é instalado automaticamente na primeira execução
- 🎨 **Exibição elegante** no terminal com emojis, logs coloridos (via `logging`) e feedback interativo

---

## 📋 Requisitos

- Python **3.10** ou superior
- Tkinter (normalmente já vem com o Python; se não: `sudo apt install python3-tk`)
- A biblioteca `pypdf` é instalada automaticamente pelo script, mas também pode ser instalada manualmente via `pip install pypdf`

---

## 🚀 Como usar

### 1. Clone o repositório

```bash
git clone https://github.com/carlosfreires/lerarvore.git
cd lerarvore
```

### 2. Execute o script

```bash
python3 lerarvore.py
```

Uma janela será aberta. **Navegue para dentro** da pasta que deseja documentar e clique em **"Selecionar pasta"**.

### 3. Confirme o caminho

No terminal, será exibido o caminho selecionado. Você poderá confirmar ou digitar manualmente o caminho correto, evitando erros comuns de seleção do diretório pai.

### 4. Resultado

O Markdown será gerado na pasta `output/` com o nome `<nome_da_pasta>.md`.

Exemplo de saída:

```bash
✅ Sucesso! 90 arquivos indexados.
📂 Markdown gerado em: /home/usuario/lerarvore/output/meuprojeto.md

🌳 Estrutura de diretórios gerada:

meuprojeto/
├── src
│   ├── main.py
│   └── utils.py
├── README.md
└── requirements.txt
```

---

## 🖥️ Uso via linha de comando (headless)

Para ambientes sem interface gráfica, utilize o argumento `--dir`:

```bash
python3 lerarvore.py --dir /caminho/para/projeto
```

---

## 📂 Estrutura do Markdown gerado

- Cabeçalho com o nome do projeto
- Para cada arquivo: título com caminho relativo, bloco de código com realce de sintaxe
- Para PDFs: conteúdo extraído página por página
- Seção final com a árvore de diretórios completa (estilo `tree`)

---

## ⚙️ Dependências

- `pypdf` – instalação automática
- `tkinter` – já incluso na maioria das distribuições Python; se necessário, instale com o gerenciador de pacotes do sistema

---

## 🤝 Contribuição

Sinta‑se à vontade para abrir issues, enviar PRs ou sugerir melhorias!

---

## 📄 Licença

Este projeto é distribuído sob a licença MIT. Consulte o arquivo `LICENSE` para mais detalhes.
