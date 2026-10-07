-- ==============================================================================
-- KillerWhale — Neovim: Opções Globais
-- ==============================================================================

local opt = vim.opt

-- Numeração de linhas
opt.number = true
opt.relativenumber = true

-- Tabulação e recuo (4 espaços padrão)
opt.tabstop = 4
opt.shiftwidth = 4
opt.expandtab = true
opt.smartindent = true
opt.autoindent = true

-- Busca
opt.ignorecase = true
opt.smartcase = true
opt.hlsearch = true
opt.incsearch = true

-- Interface e Cores
opt.termguicolors = true
opt.cursorline = true
opt.signcolumn = "yes"
opt.scrolloff = 8
opt.sidescrolloff = 8
opt.wrap = false

-- Comportamento de arquivos e buffers
opt.hidden = true
opt.undofile = true
opt.swapfile = false
opt.backup = false
opt.updatetime = 250
opt.timeoutlen = 300

-- Divisões intuitivas
opt.splitright = true
opt.splitbelow = true

-- Desativa som de alerta
opt.visualbell = false
