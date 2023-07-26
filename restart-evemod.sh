screen -X -S evemod quit

VULNBOX_SELF_IP="10.60.18.1"
INTERFACE="game"

python3 /GetDockerIPs.py > /tmp/ips.txt

dockerip=""
dockerport=""
vulnboxport=""

while IFS=',' read -r ip port dp
do
    # display $line or do something with $line
    echo "$ip"
    echo "$port"
    echo "$dp"
    # iptables rules
    sudo iptables -I FORWARD -d "$ip" -p tcp --dport "$dp" -j NFQUEUE --queue-bypass

    # aggiungi alla lista di evemod.py indirizzi e porte per la traduzione co>

    dockerip+="$ip "
    vulnboxport+="$port "
    dockerport+="$dp "

done < "/tmp/ips.txt"

# rimuovi l'ultima virgola
dockerip="${dockerip%?}"
dockerport="${dockerport%?}"
vulnboxport="${vulnboxport%?}"

echo "DOCKER_IPS = [$dockerip]"
echo "DOCKER_PORTS = [$dockerport]"
echo "VULNBOX_PORTS = [$vulnboxport]"

sudo screen -dmS evemod python3 /evemod.py --docker_ips $dockerip --docker_ports $dockerport --vulnbox_ports $vulnboxport --vulnbox_ip $VULNBOX_SELF_IP
