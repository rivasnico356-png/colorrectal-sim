#!/usr/bin/env bash
# Descarga Kvasir-SEG desde su fuente oficial a la carpeta indicada (por defecto data/), verificando TLS con la cadena
# completa: el servidor no envía el certificado intermedio, así que se toma de la dirección AIA del propio certificado.
set -euo pipefail
destino="${1:-data}"
mkdir -p "$destino" && cd "$destino"
aia=$(echo | openssl s_client -connect datasets.simula.no:443 -servername datasets.simula.no 2>/dev/null \
      | openssl x509 -noout -ext authorityInfoAccess | grep -o 'CA Issuers - URI:[^ ]*' | sed 's/CA Issuers - URI://')
echo "Intermedio: $aia"
curl -fsSL "$aia" -o intermedio.crt
(openssl x509 -inform DER -in intermedio.crt 2>/dev/null || openssl x509 -in intermedio.crt) > intermedio.pem
cat /etc/ssl/certs/ca-certificates.crt intermedio.pem > cadena.pem
curl -fsSL --retry 3 --cacert cadena.pem -o kvasir-seg.zip https://datasets.simula.no/downloads/kvasir-seg.zip
sha256sum kvasir-seg.zip | tee kvasir-seg.sha256
unzip -qo kvasir-seg.zip
echo "Imágenes: $(ls Kvasir-SEG/images | wc -l) · Máscaras: $(ls Kvasir-SEG/masks | wc -l)"
