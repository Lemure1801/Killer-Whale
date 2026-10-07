-- ==============================================================================
-- KillerWhale — Neovim Entry Point (Isolado)
-- Executado via XDG_CONFIG_HOME ou atalho kw-edit
-- ==============================================================================

-- Adiciona o diretório lua local ao package.path se necessário
local config_dir = vim.fn.stdpath("config")
package.path = config_dir .. "/lua/?.lua;" .. config_dir .. "/lua/?/init.lua;" .. package.path

-- Carrega os módulos internos do KillerWhale
require("killerwhale.options")
require("killerwhale.keymaps")
require("killerwhale.colorscheme")
require("killerwhale.plugins")
require("killerwhale.lsp")
