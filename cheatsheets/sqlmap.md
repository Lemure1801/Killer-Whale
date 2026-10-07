# Cheatsheet: Sqlmap (Auditoria de SQL Injection)

## Comandos Rápidos via Wrapper
```bash
# Modo Interativo (Launcher)
python3 wrappers/sqlmap_wrap.py --interactive

# Teste direto de URL em lote
python3 wrappers/sqlmap_wrap.py -u "http://alvo/item?id=1" --batch
```

## Opções Comuns de Diagnóstico
```bash
# Teste com banner e informações do DBMS
sqlmap -u "http://alvo/page?id=1" --batch --banner

# Teste em requisição salva (HTTP Request dump do Burp/ZAP)
sqlmap -r requisicao.req --batch

# Especificar parâmetro alvo exclusivo
sqlmap -u "http://alvo/page?id=1&cat=2" -p id --batch

# Forçar DBMS específico (quando já conhecido)
sqlmap -u "http://alvo/page?id=1" --dbms=PostgreSQL --batch
```

## Níveis e Riscos
- `--level 1` (Padrão: testa parâmetros GET/POST)
- `--level 3` (Testa também cabeçalhos Cookie/User-Agent)
- `--risk 1`  (Inócuo, queries condicionais padrão)
- `--risk 2`  (Testa ataques baseados em tempo / Time-based)

## Logs do KillerWhale
Todas as execuções iniciadas pelo wrapper gravam relatório em `$KW_ROOT/logs/sqlmap_*.log`.
