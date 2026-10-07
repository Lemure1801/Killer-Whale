-- ==============================================================================
-- KillerWhale — Neovim: Mapeamento de Teclas
-- ==============================================================================

vim.g.mapleader = " "
vim.g.maplocalleader = " "

local map = vim.keymap.set

-- Salvar e Sair rápido
map("n", "<Leader>w", "<cmd>w<CR>", { desc = "Salvar arquivo" })
map("n", "<Leader>q", "<cmd>q<CR>", { desc = "Sair" })
map("n", "<Leader>Q", "<cmd>q!<CR>", { desc = "Forçar saída sem salvar" })

-- Limpar destaque de busca
map("n", "<Leader>h", "<cmd>nohlsearch<CR>", { desc = "Limpar destaque de busca" })

-- Navegação entre janelas
map("n", "<C-h>", "<C-w>h", { desc = "Mover para janela esquerda" })
map("n", "<C-j>", "<C-w>j", { desc = "Mover para janela inferior" })
map("n", "<C-k>", "<C-w>k", { desc = "Mover para janela superior" })
map("n", "<C-l>", "<C-w>l", { desc = "Mover para janela direita" })

-- Navegação entre buffers
map("n", "<Leader>bn", "<cmd>bnext<CR>", { desc = "Próximo buffer" })
map("n", "<Leader>bp", "<cmd>bprevious<CR>", { desc = "Buffer anterior" })
map("n", "<Leader>bd", "<cmd>bdelete<CR>", { desc = "Fechar buffer atual" })

-- Manter seleção ao indentar em modo visual
map("v", "<", "<gv", { desc = "Recuar e manter seleção" })
map("v", ">", ">gv", { desc = "Avançar e manter seleção" })

-- Mover blocos de linhas para cima/baixo
map("v", "J", ":m '>+1<CR>gv=gv", { desc = "Mover bloco selecionado para baixo" })
map("v", "K", ":m '<-2<CR>gv=gv", { desc = "Mover bloco selecionado para cima" })
