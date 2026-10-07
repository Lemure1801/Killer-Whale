# KillerWhale — Workspaces

O KillerWhale organiza as atividades de auditoria e testes de segurança em **workspaces lógicos**, gerenciados pelo `tmux`. Cada workspace opera sob o princípio de **uma tarefa em tela cheia por janela** (sem splits permanentes acumulando ruído visual).

---

## Estrutura Atual de Workspaces

| Workspace | Diretório | Finalidade |
|---|---|---|
| `00-dashboard` | `workspaces/00-dashboard/` | Painel central de recursos, limpeza do sistema e navegação de comandos |
| `01-recon` | `workspaces/01-recon/` | Reconhecimento de rede, enumeração de serviços e varreduras |
| `02-exploit` | `workspaces/02-exploit/` | Verificação direcionada de vulnerabilidades e testes controlados |

---

## Como Adicionar um Novo Workspace

1. **Criar o diretório**:
   ```bash
   mkdir -p workspaces/03-reporting
   ```

2. **Criar o script de inicialização do workspace**:
   Crie `workspaces/03-reporting/workspace.sh` contendo o ambiente inicial desejado:
   ```bash
   #!/usr/bin/env bash
   set -euo pipefail
   
   # Carrega o tema do KillerWhale
   KW_ROOT="${KW_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
   source "$KW_ROOT/theme/colors.sh"
   
   echo -e "${KW_FG_GREEN}Iniciando Workspace 03-reporting...${KW_RESET}"
   # Exemplo: abrir editor ou ferramenta do workspace
   exec nvim "$KW_ROOT/notes/"
   ```
   Conceda permissão de execução:
   ```bash
   chmod +x workspaces/03-reporting/workspace.sh
   ```

3. **Registrar na inicialização do tmux (opcional)**:
   Em `tmux/tmux.conf`, você pode definir a criação automática da janela durante o boot da sessão:
   ```tmux
   new-window -t killerwhale:3 -n '03-reporting' 'bash /caminho/para/workspaces/03-reporting/workspace.sh'
   ```

4. **Integrar ao Launcher (`launcher/menu.sh`)**:
   Adicione uma entrada na tabela de ações do launcher com a tag `[WS]` para acesso via `fzf`.

---

## Filosofia Operacional
- **Foco único**: Cada janela executa um programa por vez. Se precisar executar outra tarefa, abra uma nova janela ou use o launcher.
- **Teclas de atalho**: Alterne entre workspaces usando o prefixo do tmux (`Ctrl+a` ou `Ctrl+b`) seguido do número do workspace (`0` a `9`).
- **Nenhum X11/Wayland**: Todos os fluxos operam estritamente no terminal (TTY / Alacritty / Kitty).
