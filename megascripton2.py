# inspired by megascript.sh
import os
import sys
import subprocess 
import argparse


def iptables_rules(ports, ip):
    for port in ports:
        print(f"Adding rule for port {port}")
        subprocess.run(f"sudo iptables -A INPUT -p tcp -s {ip} --dport {port} -j NFQUEUE --queue-num 1 --queue-bypass", shell=True)
        subprocess.run(f"sudo iptables -A OUTPUT -p tcp -d {ip} --sport {port} -j NFQUEUE --queue-num 1 --queue-bypass", shell=True)
        print(f"sudo iptables -A INPUT -p tcp -s {ip} --dport {port} -j NFQUEUE --queue-num 1 --queue-bypass")
        print(f"sudo iptables -A OUTPUT -p tcp -d {ip} --sport {port} -j NFQUEUE --queue-num 1 --queue-bypass")


def install_services():
    services = ["suricata", "git", "screen", "tcpdump","sshfs"]
    for service in services:
        print(f"Installing {service}")
        subprocess.run(f"apt install {service} -y", shell=True)
        print(f"Installed {service}")


def start_capture(interface):
    subprocess.run("cd /", shell=True)
    subprocess.run("git clone https://github.com/mcap0/AttackDefenseCTF /AttackDefenseCTF", shell=True)
    subprocess.run("cd /AttackDefenseCTF", shell=True)
    subprocess.run("cp /AttackDefenseCTF/suricata.yaml /", shell=True)
    subprocess.run("cp /AttackDefenseCTF/capture.py /", shell=True)
    
    ## create /ctf directory and cd in it
    subprocess.run("mkdir -p /ctf", shell=True)
    subprocess.run("cd /ctf", shell=True)

    ## start capture
    subprocess.run(f"cp /capture.py /ctf/", shell=True)
    subprocess.run(f"mkdir -p /ctf/pcaps", shell=True)
    subprocess.run(f"sudo screen -dmS capture python3 /ctf/capture.py {interface} root", shell=True)




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
    start_capture(interface)

    ## start sshfs
    print("Starting sshfs...")

    ## start suricata
    print("Starting suricata")
    start_suricata()

    print("Done! Enjoy your CTF")

main()