# Megascript

Nella cartella megascript c'è tutto il necessario per inizializzare e mantenere tulip, il capture dei pacchetti e il firewall suricata. puoi usarlo come lista per capire e localizzare eventuali problemi di infrastruttura

Copiamo da remoto i file necessari e runniamo il megascript

> ATTENZIONE! nel megascript dovrai modificare manualmente l'IP di gioco perchè non è stato automatizzato il parsing dell'indirizzo IP

**in locale:**
```bash
scp ./megascript/* root@<vulnbox_IP>:/
```

**nella vulnbox**
```bash
zip -r services.zip *
chmod +x /megascript.sh
./megascript.sh
```

---
Fatto questo potete verificare manualmente che 5 cose siano correttamente configurate:

## 1. regole FORWARD iptables

```bash
## dovrete verificare la presenza di un numero di rules NFQUEUE pari al numero dei servizi docker esposti

iptables -L FORWARD 

## ogni rule avrà un target con `dpt:<port>` 
## dove la porta è la porta INTERNA del servizio docker, NON quella esposta su 0.0.0.0
## puoi verificare le porte dei servizi docker con `iptables -t nat -L` nella Chain Docker 
```

## 2. capture.py attivo

```bash
# andate nella cartella ./tulip/servces/test_pcap e controllate
# che siano presenti file pcap e un file chiamato eve.json

# SE NON C'E' NESSUN FILE ESEGUI `screen -ls` dovresti ottenere 
# uno screen chiamato capture. Puoi entrarvi con `screen -r capture`

# altrimenti esegui di nuovo il capture controllando che non ci siano processi attivi ripetuti con 
ps aux | grep capture.py
```
## 3. regole suricata (NON AUTOMATIZZATO)
```bash
# arrivati a questo punto siete sicuri che suricata IPS e tulip TRAFFIC MONITOR funzioneranno correttamente

# aggiungete le regole suricata nella cartella ./ipsrules/local.rules e fate un reload

# sudo suricatasc -c reload-rules
Spegni e riaccendi
```


## 4. TULIP services (NON AUTOMATIZZATO)
```bash
# andate nella cartella ./tulip e modificate services/configuration.py

cd tulip
nano ./services/configuration.py

## in questo file modificate l'ip mettendo l'ip della vulnbox "10.60.39.1", e modificate 
## i servizi aggiungendo le porte esposte dei servizi vulnerabili, ed il loro nome. 

## adesso fare un reload con il seguente comando

docker-compose up --build -d api
```
## 5. IP & PORT conversion eve.json 
```bash
## se avete effettuato tutti i passaggi correttamente, adesso le regole suricata 
## andranno a taggare i pacchetti per alert, ma verranno taggati i pacchetti interni di docker. 
## Ho creato uno script che prende come argomenti i gli IP docker e relative porte,
## e modifica il file eve.json esattamente come serve a noi.

screen -dmS evemod python3 /evemod.py --docker_ips $dockerip --docker_ports $dockerport --vulnbox_ports $vulnboxport --vulnbox_ip $VULNBOX_SELF_IP

screen -r evemod
## puoi verificare le porte dei servizi docker con `iptables -t nat -L` nella Chain Docker
```
---

fatto questo connettiamo la nostra porta 3333 a quella interna della vulnbox in modo da accedere al frontend di tulip

```bash
ssh -L 3333:127.0.0.1:3333 root@<vulnbox_IP>
```

ora possiamo vedere la schermata del traffic monitor tulip connettendoci a http://localhost:3333
se avete configurato correttamente i servizi in configuration.py potrete filtrare il traffico per servizio, per regex, per flag e anche per alert

# TODO
1. modify megascript to use OUR tulip, remove 'sed' commands
2. add source port forward `sudo iptables -I FORWARD -s 172.23.0.2 -p tcp --sport 8000 -j NFQUEUE --queue-bypass`
3. add suricata tag to distinguish incoming/outgoing traffic 
4. add comments to every 'sed' command
5. add code to automatically start suricata in IPS and restart it when needed, or find a command that updates rules without restarting.
