-- ==============================================================================
-- KillerWhale — Neovim: Configuração de LSP (Language Server Protocol)
-- Suporte a Python, Bash, Go, JSON, YAML
-- ==============================================================================

local ok_lsp, lspconfig = pcall(require, "lspconfig")
if not ok_lsp then
    return
end

-- Keymaps anexados a cada buffer com LSP ativo
local on_attach = function(_, bufnr)
    local opts = { buffer = bufnr, remap = false }
    local map = vim.keymap.set

    map("n", "gd", vim.lsp.buf.definition, vim.tbl_extend("force", opts, { desc = "Ir para definição" }))
    map("n", "K", vim.lsp.buf.hover, vim.tbl_extend("force", opts, { desc = "Documentação (Hover)" }))
    map("n", "<Leader>rn", vim.lsp.buf.rename, vim.tbl_extend("force", opts, { desc = "Renomear símbolo" }))
    map("n", "<Leader>ca", vim.lsp.buf.code_action, vim.tbl_extend("force", opts, { desc = "Ação de código" }))
    map("n", "[d", vim.diagnostic.goto_prev, vim.tbl_extend("force", opts, { desc = "Diagnóstico anterior" }))
    map("n", "]d", vim.diagnostic.goto_next, vim.tbl_extend("force", opts, { desc = "Próximo diagnóstico" }))
    map("n", "<Leader>d", vim.diagnostic.open_float, vim.tbl_extend("force", opts, { desc = "Exibir diagnóstico float" }))
end

-- Servidores de Linguagem comuns em auditoria
local servers = { "bashls", "pyright", "gopls", "jsonls", "yamlls" }

for _, server in ipairs(servers) do
    if lspconfig[server] then
        lspconfig[server].setup({
            on_attach = on_attach,
        })
    end
end
