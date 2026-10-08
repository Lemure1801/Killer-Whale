"""
KillerWhale — Theme & Design System
CRT Green Phosphor Monochrome High-Contrast Aesthetic
"""

HEX_BG = "#000000"          # Fundo preto absoluto
HEX_FG = "#00ffd1"          # Ciano/verde-água fosforescente primário
HEX_FG_BRIGHT = "#4dffef"   # Ciano brilhante para destaques
HEX_FG_DIM = "#00594d"      # Ciano escuro / bordas atenuadas
HEX_WHITE = "#e6ffff"       # Branco ciano luminoso para texto de alto contraste
HEX_ACCENT = "#00b398"      # Ciano intermediário para telemetria
HEX_ALERT = "#ff3355"       # Alerta / erros críticos
HEX_GRAY = "#002620"        # Linhas divisórias e caixas secundárias
HEX_SURFACE = "#050e0c"     # Superfície de cards e painéis
HEX_SELECTION = "#00332b"   # Fundo de seleção ativa


APP_CSS = f"""
Screen {{
    background: {HEX_BG};
    color: {HEX_FG};
}}

Header {{
    background: {HEX_BG};
    color: {HEX_FG};
    dock: top;
    height: 1;
}}

Footer {{
    background: {HEX_SURFACE};
    color: {HEX_FG_BRIGHT};
    dock: bottom;
    height: 1;
}}

/* Top ASCII Header Banner */
.ascii-banner {{
    color: {HEX_FG};
    text-style: bold;
    height: auto;
    width: 100%;
    content-align: center middle;
    margin-bottom: 1;
}}

/* Top Status Bar */
.status-bar {{
    height: 3;
    background: {HEX_SURFACE};
    border: heavy {HEX_FG_DIM};
    padding: 0 1;
    margin-bottom: 1;
    color: {HEX_WHITE};
}}

/* General Panels */
.box-panel {{
    background: {HEX_SURFACE};
    border: solid {HEX_FG_DIM};
    padding: 1;
    margin: 0 1 1 1;
}}

.box-panel:focus-within {{
    border: double {HEX_FG};
}}

.title-label {{
    color: {HEX_FG_BRIGHT};
    text-style: bold;
    margin-bottom: 1;
}}

.metric-row {{
    height: 1;
    margin-bottom: 1;
}}

.metric-label {{
    width: 18;
    color: {HEX_WHITE};
    text-style: bold;
}}

.metric-value {{
    color: {HEX_FG_BRIGHT};
}}

.metric-amber {{
    color: {HEX_ACCENT};
    text-style: bold;
}}

.metric-alert {{
    color: {HEX_ALERT};
    text-style: bold;
}}

/* Buttons & Inputs */
Button {{
    background: {HEX_SELECTION};
    color: {HEX_FG_BRIGHT};
    border: tall {HEX_FG_DIM};
    height: 3;
    min-width: 16;
}}

Button:hover {{
    background: {HEX_FG_DIM};
    color: {HEX_WHITE};
}}

Button:focus {{
    background: {HEX_FG};
    color: {HEX_BG};
    text-style: bold;
    border: tall {HEX_WHITE};
}}

Button.-primary {{
    border: tall {HEX_FG};
    text-style: bold;
}}

Button.-danger {{
    border: tall {HEX_ALERT};
    color: {HEX_ALERT};
}}

#nav-buttons-grid {{
    grid-size: 4 2;
    grid-gutter: 1 1;
    height: auto;
    margin-top: 1;
}}

Input {{
    background: {HEX_SURFACE};
    color: {HEX_WHITE};
    border: tall {HEX_FG_DIM};
    padding: 0 1;
}}

Input:focus {{
    border: tall {HEX_FG};
    color: {HEX_FG_BRIGHT};
}}

/* Data Tables */
DataTable {{
    background: {HEX_SURFACE};
    color: {HEX_WHITE};
    border: solid {HEX_FG_DIM};
    height: 100%;
}}

DataTable > .datatable--header {{
    background: {HEX_SELECTION};
    color: {HEX_FG};
    text-style: bold;
}}

DataTable > .datatable--cursor {{
    background: {HEX_FG};
    color: {HEX_BG};
    text-style: bold;
}}

/* Option List & Lists */
OptionList {{
    background: {HEX_SURFACE};
    color: {HEX_WHITE};
    border: solid {HEX_FG_DIM};
}}

OptionList:focus {{
    border: double {HEX_FG};
}}

OptionList > .option-list--option-highlighted {{
    background: {HEX_SELECTION};
    color: {HEX_FG_BRIGHT};
    text-style: bold;
}}

/* Log & Output Views */
RichLog, Log {{
    background: {HEX_BG};
    color: {HEX_WHITE};
    border: solid {HEX_FG_DIM};
}}

/* Markdown Viewer */
MarkdownViewer, Markdown {{
    background: {HEX_BG};
    color: {HEX_WHITE};
}}

MarkdownH1 {{
    color: {HEX_FG_BRIGHT};
    text-style: bold underline;
    margin-top: 1;
    margin-bottom: 1;
}}

MarkdownH2 {{
    color: {HEX_FG};
    text-style: bold;
    margin-top: 1;
    margin-bottom: 1;
}}

MarkdownH3 {{
    color: {HEX_ACCENT};
    text-style: bold;
}}

MarkdownCodeBlock {{
    background: {HEX_SURFACE};
    border: solid {HEX_FG_DIM};
    color: {HEX_FG_BRIGHT};
    padding: 1;
    margin: 1 0;
}}

/* Progress Bar */
ProgressBar {{
    padding: 0 1;
}}

Bar > .bar--bar {{
    color: {HEX_FG};
    background: {HEX_SELECTION};
}}

Bar > .bar--complete {{
    color: {HEX_FG_BRIGHT};
}}
"""
