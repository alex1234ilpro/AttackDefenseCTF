# inspired by megascript.sh
import os
import sys
import subprocess 
import argparse


def iptables_rules(ports, ip):
    for port in ports:
        print(f"Adding rule for port {port}")
        subprocess.run(f"sudo iptables -A INPUT -p tcp --dport {port} -j NFQUEUE --queue-num 1 --queue-bypass", shell=True)
        subprocess.run(f"sudo iptables -A OUTPUT -p tcp -s {ip} --sport {port} -j NFQUEUE --queue-num 1 --queue-bypass", shell=True)
        print(f"sudo iptables -A INPUT -p tcp -s {ip} --dport {port} -j NFQUEUE --queue-num 1 --queue-bypass")
        print(f"sudo iptables -A OUTPUT -p tcp -d {ip} --sport {port} -j NFQUEUE --queue-num 1 --queue-bypass")


def install_services():
    services = ["suricata", "docker", "docker-compose", "git", "screen", "tcpdump"]
    for service in services:
        print(f"Installing {service}")
        subprocess.run(f"apt install {service} -y", shell=True)
        print(f"Installed {service}")


def setup_tulip(ip, services, ports, interface):
    subprocess.run("cd /", shell=True)
    subprocess.run("git clone https://github.com/mcap0/AttackDefenseCTF /AttackDefenseCTF", shell=True)
    subprocess.run("cd /AttackDefenseCTF", shell=True)
    subprocess.run("cp /AttackDefenseCTF/suricata.yaml /", shell=True)
    subprocess.run("cp /AttackDefenseCTF/capture.py /", shell=True)
    subprocess.run("cp /AttackDefenseCTF/docker-compose.yml /", shell=True)
    
    ## create /ctf directory and cd in it
    subprocess.run("mkdir -p /ctf", shell=True)
    subprocess.run("cd /ctf", shell=True)

    ## clone tulip
    subprocess.run("git clone https://github.com/OpenAttackDefenseTools/tulip /ctf/tulip", shell=True)
    subprocess.run("cd /ctf/tulip", shell=True)

    ## start capture
    subprocess.run(f"cp /capture.py /ctf/tulip/services", shell=True)
    subprocess.run(f"mkdir -p /ctf/tulip/services/pcaps", shell=True)
    subprocess.run(f"sudo screen -dmS capture python3 /ctf/tulip/services/capture.py {interface} root", shell=True)


    ## change configs
    subprocess.run(f"cd /ctf/tulip/services/api", shell=True)

    ## modify file configuration.py with ip and ports
    file = open("/ctf/tulip/services/api/configurations.py", "a")
    ## cancel all the file from line 33 and on
    file.truncate(1217)
    ## write the new configuration
    file.write(f"vm_ip = {ip}\n")
    file.write(f"services = [")
    for i, service in enumerate(services):
        file.write('{')
        file.write(f'"ip": vm_ip, "port": {ports[i]}, "name": "{services[i]}"')
        if i == len(services) - 1:
            file.write('}')
        else:
            file.write('},')
    
    file.write(f"]\n")
    file.close()

    ## modify file env
    subprocess.run(f"cd /ctf/tulip", shell=True)
    # copy .env.example to .env
    subprocess.run(f"touch /ctf/tulip/.env", shell=True)
    # modify .env
    file = open("/ctf/tulip/.env", "wb")
    # svuota il file
    file.truncate(0)
    ## put FLAG_REGEX -> The regex of the flag (e.g. [A-Z0-9]{31}=)
    #TULIP_MONGO -> IP and PORT of MongoDB (since it's in a docker container you can just use the default value of mongo:27017).
    #TRAFFIC_DIR_HOST -> The host directory (without trailing slash) where Tulip reads the .pcap files. (e.g. /var/log/pcaps).
    #TRAFFIC_DIR_DOCKER -> The containter directory (without trailing slash) where Tulip reads the .pcap files. (e.g. /traffic).
    #TICK_START -> An ISO 8601 date representing when the CTF started (YYYY-MM-DDTHH:MM+HH:MM) (e.g. 2023-11-18T18:00+01:00, means 18 november 2023 at 18:00 with +1 timezone, if it was UTC timezone it would be at 17:00).
    #TICK_LENGTH -> Frequency of ticks. (e.g. 18000 means a tick every 18000 ms) 

    file.write('FLAG_REGEX="SAAR\{[A-Za-z0-9-_]{32}\}"\n'.encode())
    file.write('TULIP_MONGO="mongo:27017"\n'.encode())
    file.write('TRAFFIC_DIR_HOST="./services/test_pcap"\n'.encode())
    file.write('TRAFFIC_DIR_DOCKER="/traffic"\n'.encode())
    file.write('TICK_START="2023-11-18T18:00+01:00"\n'.encode())
    file.write('TICK_LENGTH="18000"\n'.encode())
    file.close()

    ## modify file docker-compose.yml
    subprocess.run(f"cd /ctf/tulip", shell=True)
    subprocess.run(f"mv /docker-compose.yml /ctf/tulip/docker-compose.yml", shell=True)
    subprocess.run(f"docker-compose up --build -d", shell=True)


def start_suricata():
    ## substitute line 1862 of /etc/suricata/suricata.yaml with the following 
    subprocess.run("cp /suricata.yaml /etc/suricata/suricata.yaml", shell=True)
    subprocess.run("mkdir -p /ctf/ipsrules", shell=True)
    subprocess.run("touch /ctf/ipsrules/local.rules", shell=True)
    file = open("/ctf/ipsrules/local.rules", "wb")
    file.write('alert tcp any any -> any any (msg: "Path Traversal-../"; content: "../"; metadata: tag path_traversal; sid:2; rev: 2;)'.encode())
    file.close()
    subprocess.run("sudo screen -dmS surica suricata -c /etc/suricata/suricata.yaml -q 1", shell=True)




def main():

    parser = argparse.ArgumentParser(description='Megascriptone: start your infra without too many problems\n Usage: python3 megascriptone.py -p [services ports] -s [services names] -ip 10.32.2.2 -d eth0 ')
    parser.add_argument('-p', '--ports', help='ports of services', required=True)
    parser.add_argument('-s', '--services', help='name of services, using ports order', required=True)
    parser.add_argument('-ip', '--ip_address', help='ipv4 of your machine', required=True)
    parser.add_argument('-d', '--net_interface', help='network interface for packet capture', required=True)

    args = parser.parse_args()
    ports = args.ports.split(',')
    services = args.services.split(',')
    ip = args.ip_address
    interface = args.net_interface
    ## hai inserito le porte e i nomi dei servizi. Ottimo! ora installiamo un po' di roba
    print("Checking:")
    print(f"{ports=}")
    print(f"{services=}")
    print(f"{ip=}")
    print(f"{interface=}")

    subprocess.run("set -x", shell=True)
    subprocess.run("apt update", shell=True)

    ## adding iptables rules
    print("Adding iptables rules")
    iptables_rules(ports, ip)

    ## installing services
    print("Installing services")
    install_services()

    ## setupping tulip
    print("Setup tulip")
    setup_tulip(ip, services, ports, interface)

    ## start suricata
    print("Starting suricata")
    start_suricata()

    print("Done! Enjoy your CTF")

main()