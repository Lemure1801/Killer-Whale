-- ==============================================================================
-- KillerWhale — Neovim: Gerenciador de Plugins (Lazy.nvim)
-- ==============================================================================

local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.loop.fs_stat(lazypath) then
    -- Tenta clonar se git estiver disponível na VM
    if vim.fn.executable("git") == 1 then
        vim.fn.system({
            "git",
            "clone",
            "--filter=blob:none",
            "https://github.com/folke/lazy.nvim.git",
            "--branch=stable",
            lazypath,
        })
    end
end

if vim.loop.fs_stat(lazypath) then
    vim.opt.rtp:prepend(lazypath)

    local ok, lazy = pcall(require, "lazy")
    if ok then
        lazy.setup({
            -- Telescope: Fuzzy Finder
            {
                "nvim-telescope/telescope.nvim",
                dependencies = { "nvim-lua/plenary.nvim" },
                cmd = "Telescope",
                keys = {
                    { "<Leader>ff", "<cmd>Telescope find_files<CR>", desc = "Buscar Arquivos" },
                    { "<Leader>fg", "<cmd>Telescope live_grep<CR>", desc = "Buscar Texto (Grep)" },
                    { "<Leader>fb", "<cmd>Telescope buffers<CR>", desc = "Listar Buffers" },
                },
                config = function()
                    local telescope = require("telescope")
                    telescope.setup({
                        defaults = {
                            prompt_prefix = "kw::find > ",
                            selection_caret = "► ",
                            sorting_strategy = "ascending",
                            layout_config = {
                                horizontal = { mirror = false },
                            },
                        },
                    })
                end,
            },

            -- Syntax Highlighting moderno (Treesitter)
            {
                "nvim-treesitter/nvim-treesitter",
                build = ":TSUpdate",
                event = { "BufReadPost", "BufNewFile" },
                config = function()
                    local ok_ts, ts = pcall(require, "nvim-treesitter.configs")
                    if ok_ts then
                        ts.setup({
                            ensure_installed = { "bash", "python", "go", "json", "yaml", "markdown", "lua" },
                            highlight = { enable = true },
                            indent = { enable = true },
                        })
                    end
                end,
            },

            -- LSP Config
            {
                "neovim/nvim-lspconfig",
                event = { "BufReadPre", "BufNewFile" },
            },
        }, {
            ui = {
                border = "single",
                title = " KillerWhale Plugins ",
            },
        })
    end
end
