import subprocess
import re

# output possiede l'output del comando iptables -t nat -L
output = subprocess.check_output(["iptables", "-t", "nat", "-L"]).decode("utf-8")

# la regex prende solo le porte e gli indirizzi IP delle regole DNAT
# che si interfacciano all'esterno

matches = re.findall(r"DNAT\s+tcp\s+--\s+anywhere\s+anywhere\s+tcp dpt:([a-z-]+|\d+)\s+to:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)", output)


def port_converter(port):
    known_ports = {
        "ftp": "21",
        "ssh": "22",
        "telnet": "23",
        "smtp": "25",
        "http": "80",
        "pop3": "110",
        "imap": "143",
        "https": "443",
        "samba": "445",
        "smtps": "465",
        "imaps": "993",
        "pop3s": "995",
        "mysql": "3306",
        "http-alt": "8080",
        "ssh-alt": "2222",
        "rdp": "3389",
        "tproxy": "8081",

    }

    return known_ports.get(port, port)

for match in matches:
    port = port_converter(match[0])
    ip_address = match[1]
    target_port = port_converter(match[2])
    print(f"{ip_address},{port},{target_port}")
 