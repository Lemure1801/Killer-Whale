# Cheatsheet: Reconhecimento & Descoberta Ativa/Passiva

## Resolução DNS e WHOIS
```bash
# Busca de servidores de nomes e MX
dig <dominio> NS +short
dig <dominio> MX +short

# Transferência de zona AXFR (caso desprotegido)
dig axfr @ns1.<dominio> <dominio>

# Consulta WHOIS resumida
whois <dominio> | grep -E "Registrar|Creation Date|Name Server"
```

## Inspeção HTTP/HTTPS via Terminal
```bash
# Obter apenas os cabeçalhos de resposta HTTP
curl -sI -k "https://<alvo>"

# Identificar servidores e tecnologias em resposta
curl -sI "https://<alvo>" | grep -iE "server|x-powered-by|set-cookie|strict-transport"

# Seguir redirecionamentos e exibir código final
curl -s -L -o /dev/null -w "%{http_code} (%{url_effective})\n" "http://<alvo>"
```

## Enumeração de Certificado SSL/TLS
```bash
# Extrair Subject e SANs do certificado
openssl s_client -connect <alvo>:443 -servername <alvo> </dev/null 2>/dev/null | \
  openssl x509 -noout -text | grep -A1 "Subject Alternative Name"
```
