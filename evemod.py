import json
import os
import time
import argparse

# specifica gli indirizzi IP e le porte di destinazione da sostituire
# fai il parse di docker_ips, docker_ports e vulnbox_ports da argparse
parser = argparse.ArgumentParser(description="insert docker ips and ports, vulnbox ports and ip")
parser.add_argument("--docker_ips", nargs="+", type=str, help="IPs of docker containers", default=[])
parser.add_argument("--docker_ports", nargs="+", type=int, help="Ports of docker containers", default=[])
parser.add_argument("--vulnbox_ports", nargs="+", type=int, help="Ports of vulnbox", default=[])
parser.add_argument("--vulnbox_ip", type=str, help="IP of vulnbox")

args = parser.parse_args()
docker_ips = args.docker_ips
docker_ports = args.docker_ports
vulnbox_ports = args.vulnbox_ports
vulnbox_ip = args.vulnbox_ip

assert len(docker_ips) == len(docker_ports) == len(vulnbox_ports), "docker_ips, docker_ports e vulnbox_ports deve avere la stessa lunghezza"

# specifica il path del file eve.json
EVE_DIR = "/var/log/suricata/eve.json"
SEEK_FROM_START = 0
SEEK_FROM_CURRENT = 1
SEEK_FROM_END = 2

# ottieni il timestamp dell'ultima modifica del file
last_modified = os.path.getmtime(EVE_DIR)
# Offset del file. Indica il punto in cui è avvenuta l'ultima modifica
file_offset = 0

while True:
    # controlla il timestamp dell'ultima modifica del file
    current_modified = os.path.getmtime(EVE_DIR)
    if current_modified != last_modified:
        # se il file è stato modificato, esegui lo script di sostituzione
        with open(EVE_DIR, "r") as f:
            # ci si sposta subito all'offset dove è avvenuta l'ultima modifica
            f.seek(file_offset, SEEK_FROM_START)
            lines = f.readlines()

        for i, line in enumerate(lines):
            line = line.strip()
            if line:
                try:
                    data = json.loads(line)
                except:
                    continue
                try:
                    for docker_ip, docker_port, vulnbox_port in zip(docker_ips, docker_ports, vulnbox_ports):
                        if data["dest_ip"] == docker_ip and data["dest_port"] == docker_port:
                            data["dest_ip"] = vulnbox_ip
                            data["dest_port"] = vulnbox_port
                            lines[i] = f"{json.dumps(data)}\n"
                except:
                    continue

        with open(EVE_DIR, "r+") as f:
            # si tronca il file eliminando tutto ciò che c'è dopo l'offset
            f.truncate(file_offset)
            # ci si sposta alla fine del file
            f.seek(0, SEEK_FROM_END)
            # si scrivono le righe modificate
            f.writelines(lines)
            # aggiorna l'offset del file con l'ultima modifica
            file_offset = f.tell()

        # aggiorna il timestamp dell'ultima modifica del file
        last_modified = current_modified

    time.sleep(1)
