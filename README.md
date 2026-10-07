# KillerWhale 🐋
### Workstation TUI para Auditoria e Pentest Autorizado (Arch Linux)

[![Interface](https://img.shields.io/badge/Interface-100%25%20TUI%20%7C%20ASCII-00FF66?style=flat-square&logo=gnubash&logoColor=black)](#)
[![Multiplexer](https://img.shields.io/badge/Multiplexer-tmux-00FF66?style=flat-square&logo=tmux&logoColor=black)](#)
[![Target OS](https://img.shields.io/badge/Target%20OS-Arch%20Linux-1793D1?style=flat-square&logo=archlinux&logoColor=white)](#)
[![Editor](https://img.shields.io/badge/Editor-Neovim%20(Isolado)-57A143?style=flat-square&logo=neovim&logoColor=white)](#)

O **KillerWhale** é um ambiente de trabalho completo em modo texto (TUI), projetado para execução em terminais puros (TTY) ou emuladores de terminal fullscreen (Alacritty / Kitty) em máquinas virtuais **Arch Linux**.

Construído sob a estética de terminais CRT de fósforo verde e caracteres box-drawing ASCII, o KillerWhale prioriza agilidade, baixo consumo de recursos, ergonomia focada 100% em teclado e rastreabilidade total de comandos em atividades de auditoria de segurança autorizada.

---

> [!IMPORTANT]
> **Aviso de Ambiente (Sandbox vs. VM Final)**:
> Os arquivos e configurações deste repositório foram gerados em ambiente isolado (sandbox `bwrap`). **Nenhum pacote foi instalado no host hospedeiro.**
> A instalação real de dependências e a aplicação dos dotfiles devem ser realizadas **exclusivamente na máquina virtual Arch Linux de destino** executando o script `bootstrap/install.sh`.

---

## 🏛️ Filosofia e Arquitetura

1. **100% Modo Texto (Sem GUI)**: Opera com perfeição em TTY puro ou terminal gráfico fullscreen, sem dependência de X11 ou Wayland.
2. **Workspaces em Tela Cheia via `tmux`**: Cada workspace lógico executa **uma única tarefa em tela cheia** por janela. Não há acúmulo de splits permanentes que causam poluição visual.
3. **Painel de Controle Central (`00-dashboard`)**: Ponto de partida com resumo de telemetria de hardware (`btop`), utilitários de limpeza/manutenção do sistema (`cleanup.sh`), cheatsheets e atalhos de navegação.
4. **Command Palette (`fzf`)**: Menu modal acessível globalmente para disparar workspaces, utilitários e wrappers com busca difusa.
5. **Wrappers Inteligentes**: Camada de execução sobre ferramentas padrão (`nmap`, `sqlmap`, etc.) que padroniza saídas em caixas ASCII usando Python (`rich`) e armazena logs auditáveis com timestamp em `logs/`.
6. **Neovim Isolado**: Configuração dedicada e modular do Neovim (`nvim/`) que não interfere nas preferências pessoais do usuário.
7. **Idempotência Total**: O instalador de bootstrap pode ser executado múltiplas vezes de forma segura, criando backups automáticos de configurações preexistentes.

---

## 📂 Estrutura de Diretórios

```
KillerWhale/
├── README.md                      # Documentação principal e guia de uso
├── config.fish                    # Configuração para fish shell (aliases e PATH)
├── bootstrap/
│   └── install.sh                 # Script idempotente de instalação para Arch Linux
├── tmux/
│   └── tmux.conf                  # Configuração do tmux (workspaces, status bar, atalhos)
├── workspaces/
│   ├── README.md                  # Manual de extensão de novos workspaces
│   ├── 00-dashboard/              # Workspace 00: Painel de Controle
│   │   ├── dashboard.sh           # Telemetria de CPU/RAM/Disco + menu rápido
│   │   ├── cleanup.sh             # Manutenção do sistema (cache pacman, vacuum, logs)
│   │   └── cheatsheet.sh          # Visualizador interativo fzf de comandos
│   ├── 01-recon/                  # Workspace 01: Reconhecimento e enumeração
│   └── 02-exploit/                # Workspace 02: Validação e auditoria controlada
├── launcher/
│   └── menu.sh                    # Command palette global (fzf)
├── wrappers/
│   ├── README.md                  # Padrão e guia para criação de wrappers
│   ├── nmap_wrap.py               # Wrapper formatador de varredura nmap
│   └── sqlmap_wrap.py             # Wrapper estruturado para sqlmap
├── nvim/
│   ├── init.lua                   # Entrada do Neovim isolado
│   └── lua/
│       └── killerwhale/           # Módulos lua (options, keymaps, lsp, telescope)
├── cheatsheets/                   # Folhas de consulta rápida em Markdown
│   ├── nmap.md
│   ├── sqlmap.md
│   └── general.md
├── theme/
│   ├── colors.sh                  # Paleta de cores central (fósforo verde / ASCII)
│   ├── alacritty.toml             # Tema e configuração para Alacritty
│   ├── kitty.conf                 # Tema e configuração para Kitty
│   └── btop.theme                 # Tema de telemetria para btop
├── tests/
│   └── smoke_test.sh              # Validador de sintaxe e integridade estrutural
└── logs/                          # Registro automático de execuções com timestamp
```

---

## 📦 Pacotes e Dependências da VM Arch

O script `bootstrap/install.sh` instala automaticamente os seguintes componentes através do `pacman` e `yay`:

### Base de Terminal e Interface
- `tmux`: Multiplexador de terminais central.
- `fzf`: Motor de busca fuzzy para o launcher e cheatsheets.
- `btop`: Monitor moderno de recursos do sistema.
- `neovim`: Editor modal.
- `fish`: Shell interativo principal.
- `alacritty` ou `kitty`: Emuladores de terminal GPU/leves recomendados.
- `gum` e/ou `dialog`: Menus TUI interativos para manutenção.
- `ripgrep`, `fd`, `bat`, `jq`: Ferramentas modernas de manipulação de texto.

### Python e Formatação
- `python`, `python-pip`: Interpretador Python 3.
- `python-rich`: Biblioteca de renderização TUI e caixas ASCII.

### Ferramentas de Auditoria e Rede
- `nmap`, `sqlmap`, `iproute2`, `bind`, `curl`, `net-tools`.

---

## 🚀 Como Instalar na VM Arch Linux

> [!CAUTION]
> Execute estes passos **apenas dentro da VM Arch Linux**. Não execute no host CachyOS ou no sandbox de desenvolvimento.

1. **Clonar ou copiar o repositório para a VM**:
   ```bash
   git clone <URL_DO_REPOSITORIO> ~/KillerWhale
   # ou copiar via scp/pasta compartilhada
   cd ~/KillerWhale
   ```

2. **Executar o bootstrap**:
   ```bash
   bash bootstrap/install.sh
   ```

3. **Iniciar a sessão KillerWhale**:
   ```bash
   tmux -f ~/KillerWhale/tmux/tmux.conf new-session -A -s killerwhale
   ```

---

## ⌨️ Atalhos Principais

O prefixo padrão do tmux está configurado para **`Ctrl+a`** (com compatibilidade para `Ctrl+b`):

| Atalho | Ação |
|---|---|
| `Ctrl+a` `Espaço` | Abre o **Command Palette (Launcher)** |
| `Ctrl+a` `0` | Alterna para o **Workspace 00: Dashboard** |
| `Ctrl+a` `1` | Alterna para o **Workspace 01: Recon** |
| `Ctrl+a` `2` | Alterna para o **Workspace 02: Exploit** |
| `Ctrl+a` `c` | Cria nova janela / workspace em tela cheia |
| `Ctrl+a` `k` | Abre o menu de **Limpeza / Manutenção** |
| `Ctrl+a` `?` | Abre o navegador de **Cheatsheets** |
| `Ctrl+a` `e` | Abre o **Neovim** no ambiente isolado |

---

## 🛠️ Como Estender o Projeto

### Adicionando um Novo Workspace
Consulte o guia detalhado em [`workspaces/README.md`](workspaces/README.md).
1. Crie o diretório em `workspaces/XX-nome/`.
2. Adicione os scripts necessários.
3. Cadastre a janela em `tmux/tmux.conf` e no launcher.

### Adicionando um Novo Wrapper
Consulte o guia detalhado em [`wrappers/README.md`](wrappers/README.md).
1. Crie o arquivo `wrappers/<ferramenta>_wrap.py`.
2. Utilize o template baseado na biblioteca `rich` para formatar a saída.
3. Garanta a escrita do log em `$KW_ROOT/logs/`.
4. Cadastre o comando no launcher `launcher/menu.sh`.

---

## ⚖️ Aviso Legal e Ético
Este software foi desenvolvido exclusivamente para fins educacionais, auditorias de segurança defensivas e testes de intrusão autorizados por escrito pelo proprietário dos sistemas avaliados. O autor e os contribuidores não se responsabilizam pelo uso indevido deste ferramental.
