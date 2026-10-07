# Cheatsheet: Nmap (Network Mapper)

## Comandos Rápidos via Wrapper
```bash
# Modo Interativo (Launcher)
python3 wrappers/nmap_wrap.py --interactive

# Varredura Rápida (Top 100 portas)
python3 wrappers/nmap_wrap.py 192.168.1.1 -F -T4

# Detecção Completa de Versões e Scripts
python3 wrappers/nmap_wrap.py 192.168.1.1 -sV -sC -T4
```

## Modos de Varredura Frequentes
```bash
# Varredura TCP SYN (Requer privilégio root/sudo)
nmap -sS -T4 <alvo>

# Varredura TCP Connect (Sem privilégio root)
nmap -sT -T4 <alvo>

# Varredura de Portas UDP
nmap -sU --top-ports 50 <alvo>

# Varredura de todas as 65.535 portas TCP
nmap -p- -T4 --min-rate 1000 <alvo>
```

## Scripts NSE Úteis (Enumeração)
```bash
# Banner Grabbing
nmap -sV --script=banner <alvo>

# Enumeração SMB (Windows/Samba)
nmap -p 139,445 --script=smb-enum-shares,smb-enum-users <alvo>

# Enumeração HTTP básica
nmap -p 80,443 --script=http-title,http-headers <alvo>
```

## Formatos de Saída Padrão
- `-oN <arquivo>.txt` : Formato texto legível
- `-oX <arquivo>.xml` : Formato XML estruturado
- `-oG <arquivo>.grep`: Formato grepável
- `-oA <prefixo>`     : Salva em todos os 3 formatos simultaneamente
