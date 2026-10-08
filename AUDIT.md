# AUDITORIA TÉCNICA E PLANO DE TRANSIÇÃO DO KILLERWHALE

**Data:** 2026-10-08  
**Autor:** Auditoria do Sistema Antigravity  
**Status do Repositório:** Esqueleto procedural de scripts Bash/Python/Tmux verificado.

---

## 1. Confirmação do Diagnóstico

A inspeção detalhada do código-fonte em `/home/vulture/KillerWhale` confirma integralmente os quatro pontos apontados:

1. **Sem engine de interface real:**
   - `workspaces/00-dashboard/dashboard.sh`: Loop infinito síncrono (`while true; clear; ... read -n 1`). Chamadas pesadas a subprocessos (`top`, `free`, `df`, `ip`, `uptime`) a cada iteração/toque de tecla. Não há event loop assíncrono, widgets desacoplados nem renderização parcial.
   - `workspaces/00-dashboard/cleanup.sh`: Script interativo baseado em prompts `read -r` e `sudo pacman/paccache/journalctl`.
   - `workspaces/00-dashboard/cheatsheet.sh`: Dependência estrita de subshell externa invocando `fzf` e `less`/`bat`.
   - `launcher/menu.sh`: Script disparando comandos externos e alternando janelas tmux via `tmux select-window`.

2. **Neovim isolado, não integrado:**
   - `launcher/edit.sh`, `dashboard.sh:189` e `tmux.conf:69` apenas invocam um novo processo `nvim` configurando `XDG_CONFIG_HOME`.
   - Inexistência de canal IPC/RPC (`/tmp/killerwhale-nvim.sock`), inviabilizando que a interface envie arquivos, posicione cursores ou colete anotações sem fechar ou trocar de contexto.

3. **Wrappers sem orquestração real:**
   - `wrappers/nmap_wrap.py` e `wrappers/sqlmap_wrap.py` possuem boa formatação via `rich`, mas dependem de `sys.stdin.readline()` e `subprocess.Popen` síncrono em terminal cru.
   - Não há controle de histórico de tarefas, cancelamento assíncrono em background, buffer compartilhado nem pipeline integrado ("rodar varredura -> inspecionar tabela -> enviar relatório ao editor").

4. **"Interatividade" limitada a tmux + fzf:**
   - A única troca de estado existente é o arquivo de texto plano `~/.killerwhale/target`.
   - Mudar de workspace é apenas dar `tmux select-window`.

---

## 2. Decisão de Arquitetura: O que Manter vs. O que Substituir

### Manter (Reaproveitáveis sem quebras)
- **`theme/`**:
  - `colors.sh`, `alacritty.toml`, `kitty.conf`, `btop.theme`. A paleta (Fundo `#050a05`, Fósforo Verde `#00ff66`, Bright `#66ff99`, Dim `#006622`, Amber `#ffb000`, Alert `#ff3333`) é preservada como identidade do sistema e refletida nas CSS/estilos Textual.
- **`cheatsheets/*.md`**:
  - `general.md`, `nmap.md`, `sqlmap.md`, `recon.md`. Conteúdo markdown estruturado que será lido e renderizado nativamente dentro do visualizador Textual.
- **`wrappers/*_wrap.py`**:
  - Lógica de parsing de regex de portas e técnicas (`parse_nmap_ports`, `parse_sqlmap_summary`), reaproveitadas por um módulo orquestrador python reutilizável em `killerwhale/core/`.
- **`bootstrap/install.sh`**:
  - Adição de dependências `textual`, `pynvim`, `psutil` ao manifesto e configuração.
- **`tmux/`**:
  - Mantido para multiplexação no nível do SO, mas o workspace 00 passa a hospedar o aplicativo Textual contínuo.

### Substituir / Reconstruir em Python + Textual
- **App Principal KillerWhale (`killerwhale/app.py` & CLI de inicialização)**:
  - Event loop assíncrono centralizado.
  - Navegação entre telas via atalhos e Command Palette nativa integrada.
  - Estética CRT Fósforo Verde, box-drawing ASCII de alto contraste.
- **Telas Reativas Textual**:
  - `DashboardScreen`: Telemetria em tempo real (CPU, RAM, Disco, Rede, Uptime, Alvo Ativo) via `psutil` sem cintilação (`reactive` + `set_interval`).
  - `LauncherScreen / CommandPalette`: Navegação e execução de ações sem depender de shell externa.
  - `CheatsheetScreen`: Navegador com árvore/lista de arquivos markdown e renderizador Textual Markdown nativo com busca rápida.
  - `CleanupScreen`: Central de higienização de caches e logs com diálogos de confirmação nativos e execução assíncrona.
  - `ToolsScreen / AuditRunner`: Orquestrador de auditoria com execução assíncrona de `nmap_wrap` / `sqlmap_wrap`, streaming de logs e ação composta de abertura no Neovim.
- **Camada de Integração Neovim (`killerwhale/core/nvim_client.py`)**:
  - Conexão e controle via socket RPC (`/tmp/killerwhale-nvim.sock`) usando `pynvim`.
  - Comandos para abrir arquivos, criar buffers com extratos de varredura e gerenciar anotações de auditoria sem spawning de janelas extras.

---

## 3. Matriz de Incrementos de Implementação

| Etapa | Meta | Critério de Aceite |
|---|---|---|
| **Etapa 0** | Auditoria e diagnóstico | `AUDIT.md` documentado |
| **Etapa 1** | Prova de vida Textual | App mínimo executável, tela cheia, estética CRT, sai com `q` |
| **Etapa 2** | Dashboard com telemetria real | Métricas `psutil` reativas em tempo real sem cintilação |
| **Etapa 3** | Navegação e telas | Múltiplas telas, Command Palette/Launcher nativo, estado preservado |
| **Etapa 4** | Neovim RPC | Conexão socket `/tmp/killerwhale-nvim.sock` via `pynvim`, abertura de buffer |
| **Etapa 5** | Wrapper Nmap integrado | Execução de scanner, exibição de resultado tabular e abertura no Neovim via RPC |
| **Etapa 6** | Cleanup & Cheatsheet nativos | Portar manutenção e leitor de cheatsheets markdown para Textual |
| **Etapa 7** | Refinamento & Workspaces | Estética polida, atalhos globais, integração com `session.sh` |
