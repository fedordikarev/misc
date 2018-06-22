#!/bin/sh

pass=dock123
org=Innova
HOST=$(hostname -f)
CA_SUBJ="/C=RU/ST=Moscow/L=Moscow/O=$org/OU=$org Docker Swarm/CN=$HOST"

openssl genrsa -aes256 -passout pass:$pass -out ca-key.pem 4096

openssl req -new -x509 -days 3650 -key ca-key.pem -passin pass:$pass -sha256 -out ca.pem\
	-subj "$CA_SUBJ"

openssl genrsa -out server-key.pem 4096
openssl req -subj "/CN=$HOST" -sha256 -new -key server-key.pem -out server.csr

ip4=$(/sbin/ip -o -4 addr  | awk '{print $4}' | cut -d/ -f1)
ip_list=$(echo "$ip4" | egrep -v '172.18.0|172.19.0' | xargs -n1 -I {} echo "IP:"{} | paste -sd, -)

echo subjectAltName = DNS:$HOST,${ip_list} > extfile.cnf
echo extendedKeyUsage = serverAuth >> extfile.cnf

openssl x509 -req -days 3650 -sha256 -in server.csr -CA ca.pem -CAkey ca-key.pem \
  -passin pass:$pass \
  -CAcreateserial -out server-cert.pem -extfile extfile.cnf

mkdir -p /etc/systemd/system/docker.service.d
echo "[Service]
ExecStart=
ExecStart=/usr/bin/dockerd -H fd:// --tlscacert=/etc/docker/ca.pem --tlscert=/etc/docker/server-cert.pem --tlskey=/etc/docker/server-key.pem -H=0.0.0.0:2376" > /etc/systemd/system/docker.service.d/override.conf
