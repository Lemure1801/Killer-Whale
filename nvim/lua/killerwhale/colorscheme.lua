-- ==============================================================================
-- KillerWhale — Neovim: Esquema de Cores CRT Fósforo Verde Nativo
-- Não depende de plugins externos — funciona imediatamente
-- ==============================================================================

local function apply_theme()
    vim.cmd("highlight clear")
    if vim.fn.exists("syntax_on") == 1 then
        vim.cmd("syntax reset")
    end

    vim.o.background = "dark"
    vim.g.colors_name = "killerwhale"

    local bg_dark   = "#050a05"
    local bg_hl     = "#0a170a"
    local fg_main   = "#00ff66"
    local fg_bright = "#66ff99"
    local fg_dim    = "#006622"
    local fg_amber  = "#ffb000"
    local fg_red    = "#ff3333"
    local fg_cyan   = "#33ffee"
    local fg_white  = "#f0fff0"

    local hl = function(group, opts)
        vim.api.nvim_set_hl(0, group, opts)
    end

    -- Editor Base
    hl("Normal",       { fg = fg_main, bg = bg_dark })
    hl("NormalFloat",  { fg = fg_white, bg = bg_hl })
    hl("FloatBorder",  { fg = fg_main, bg = bg_hl })
    hl("Cursor",       { fg = bg_dark, bg = fg_bright })
    hl("CursorLine",   { bg = bg_hl })
    hl("CursorLineNr", { fg = fg_bright, bg = bg_hl, bold = true })
    hl("LineNr",       { fg = fg_dim, bg = bg_dark })
    hl("SignColumn",   { bg = bg_dark })
    hl("VertSplit",    { fg = fg_dim, bg = bg_dark })
    hl("StatusLine",   { fg = bg_dark, bg = fg_main, bold = true })
    hl("StatusLineNC", { fg = fg_dim, bg = bg_hl })

    -- Busca e Seleção
    hl("Visual",       { fg = bg_dark, bg = fg_main })
    hl("Search",       { fg = bg_dark, bg = fg_amber, bold = true })
    hl("IncSearch",    { fg = bg_dark, bg = fg_bright, bold = true })

    -- Sintaxe de Código
    hl("Comment",      { fg = fg_dim, italic = true })
    hl("Constant",     { fg = fg_amber })
    hl("String",       { fg = fg_cyan })
    hl("Character",    { fg = fg_cyan })
    hl("Number",       { fg = fg_amber })
    hl("Boolean",      { fg = fg_amber, bold = true })
    hl("Identifier",   { fg = fg_white })
    hl("Function",     { fg = fg_bright, bold = true })
    hl("Statement",    { fg = fg_bright, bold = true })
    hl("Keyword",      { fg = fg_bright, bold = true })
    hl("PreProc",      { fg = fg_main })
    hl("Type",         { fg = fg_white, bold = true })
    hl("Special",      { fg = fg_bright })
    hl("Underlined",   { underline = true })
    hl("Error",        { fg = fg_red, bold = true })
    hl("Todo",         { fg = bg_dark, bg = fg_amber, bold = true })

    -- Diagnósticos (LSP)
    hl("DiagnosticError", { fg = fg_red })
    hl("DiagnosticWarn",  { fg = fg_amber })
    hl("DiagnosticInfo",  { fg = fg_cyan })
    hl("DiagnosticHint",  { fg = fg_bright })
end

apply_theme()
