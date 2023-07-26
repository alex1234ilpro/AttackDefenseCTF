
### BENVENUTO IN MEGASCRIPT ###
# Questo script è stato creato per automatizzare il processo di configurazione dell'infrastruttura.

####### CAMBIAMI #######
VULNBOX_SELF_IP="10.60.18.1"
#######          #######

## interfaccia di rete
INTERFACE="game"




## non working IP
# VULNBOX_SELF_IP=$(ip addr show $INTERFACE | grep "inet\b" | awk '{print $2}' | cut -d/ -f1) 

## non working Interface
#INTERFACE=$(ip route | grep default | awk '{print $5}')

## GetDockerIPs python script fa in modo di leggere gli indirizzi ip dei container docker e di inserirli in 
## un file temporaneo ci serviranno per creare le regole iptables ad hoc per suricata + passare gli indirizzi a evemod.py

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



set -x

## cartella di destinazione per tulip e regole suricata
sudo mkdir -p /ctf
sudo apt update -y



## GIT INSTALL
sudo apt install git -y



## SURICATA INSTALL
sudo add-apt-repository ppa:oisf/suricata-stable -y
sudo apt install suricata jq -y

cp /suricata.yaml /etc/suricata/suricata.yaml


## TULIP INSTALL    
cd /ctf
git clone https://github.com/OpenAttackDefenseTools/tulip.git

# copia .env file
cd tulip
cp /envfile .env

## modifica la regex per il file .env
#FLAG_REGEX="[A-Z0-9]{31}(?:%3D|=)?"
#sudo sh -c "sed -i 's/FLAG_REGEX=.*/FLAG_REGEX=\""$FLAG_REGEX"\"/' .env"


## rimuovi file di esempio + crea cartella del capture
sudo rm -f services/test_pcap/*
mkdir -p services/pcaps

## modifica docker-compose
cp /docker-compose.yml /ctf/tulip/docker-compose.yml

#sudo sh -c "sed -i '4 s/5/4.4.18/' ./docker-compose.yml"
#sudo sh -c "sed -i '17 s/- \"3000/- \"127.0.0.1:3333/' ./docker-compose.yml"
#sudo sh -c "sed -i '31 s/      - \"127.0.0.1:5000/      - \"127.0.0.1:5005/' ./docker-compose.yml"
#sudo sh -c "sed -i '34 s/^/    restart: always\n/' ./docker-compose.yml"
#sudo sh -c "sed -i '69 s/^/    restart: always\n/' ./docker-compose.yml"
#sudo sh -c "sed -i '74 s/-eve/-t 8 -eve/' ./docker-compose.yml"




## install screen if not present
sudo apt install screen -y


## CARTELLA PER LE REGOLE SURICATA
cd /ctf
mkdir -p ipsrules
cd ipsrules
touch local.rules
cd /ctf

## example rule
# alert tcp any any -> any any (msg: "Path Traversal-../"; flow:to_server; content: "../"; metadata: tag path_traversal; sid:1; rev: 1;)
### INSERT HERE RULES FOR SURICATA


## START SURICATA IPS
sudo systemctl stop suricata
screen -X -S surica quit
screen -X -S evemod quit
screen -X -S capture quit
sudo screen -dmS surica suricata -c /etc/suricata/suricata.yaml -q 0

## START CAPTURE
cd /ctf
cp /capture.py /ctf/tulip/services/
sudo screen -dmS capture python3 /ctf/tulip/services/capture.py $INTERFACE $USER

## START EVEMOD
#sudo screen -dmS evemod python3 /evemod.py --docker_ips $dockerip --docker_ports $dockerport --vulnbox_ports $vulnboxport
sudo screen -dmS evemod python3 /evemod.py --docker_ips $dockerip --docker_ports $dockerport --vulnbox_ports $vulnboxport --vulnbox_ip $VULNBOX_SELF_IP

## per verificare che funzioni 'screen' esegui il comando `screen -ls` dovresti ottenere 
## uno screen chiamato capture. Puoi entrarvi con `screen -r capture`


## START WEB MONITOR
cd /ctf/tulip
sudo usermod -aG docker $USER
sudo docker-compose up -d
