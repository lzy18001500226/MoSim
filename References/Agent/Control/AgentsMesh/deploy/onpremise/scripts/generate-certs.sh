#!/bin/bash
# =============================================================================
# Generate SSL Certificates for gRPC mTLS
# =============================================================================
#
# Creates:
# - ca.crt/ca.key: Self-signed CA certificate
# - server.crt/server.key: Server certificate signed by CA
#
# Usage:
#   ./generate-certs.sh [SERVER_IP]
#
# Output directory: ../ssl/
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SSL_DIR="${SCRIPT_DIR}/../ssl"
SERVER_IP="${1:-}"

# Create SSL directory
mkdir -p "${SSL_DIR}"

echo "Generating certificates in ${SSL_DIR}..."

# Check if certificates already exist
if [ -f "${SSL_DIR}/ca.crt" ] && [ -f "${SSL_DIR}/server.crt" ]; then
    echo "Certificates already exist. To regenerate, delete ${SSL_DIR} first."
    exit 0
fi

# Generate CA private key (ECDSA P-256, traditional EC format for Go compatibility)
echo "Generating CA private key..."
openssl ecparam -name prime256v1 -genkey -noout -out "${SSL_DIR}/ca.key"

# Generate CA certificate (10 years validity)
echo "Generating CA certificate..."
openssl req -new -x509 -days 3650 -key "${SSL_DIR}/ca.key" -out "${SSL_DIR}/ca.crt" \
    -subj "/CN=AgentsMesh OnPremise CA/O=AgentsMesh/OU=OnPremise"

# Generate server private key (ECDSA P-256, traditional EC format for Go compatibility)
echo "Generating server private key..."
openssl ecparam -name prime256v1 -genkey -noout -out "${SSL_DIR}/server.key"

# Generate server CSR
echo "Generating server CSR..."
openssl req -new -key "${SSL_DIR}/server.key" -out "${SSL_DIR}/server.csr" \
    -subj "/CN=agentsmesh-backend/O=AgentsMesh/OU=Backend"

# Create server certificate extensions config
# Include SERVER_IP if provided
cat > "${SSL_DIR}/server_ext.cnf" << EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = backend
DNS.3 = traefik
DNS.4 = *.local
IP.1 = 127.0.0.1
IP.2 = ::1
EOF

# Add SERVER_IP to SAN if provided
if [ -n "${SERVER_IP}" ]; then
    echo "IP.3 = ${SERVER_IP}" >> "${SSL_DIR}/server_ext.cnf"
    echo "Adding ${SERVER_IP} to certificate SANs..."
fi

# Sign server certificate with CA (1 year validity)
echo "Signing server certificate with CA..."
openssl x509 -req -days 365 -in "${SSL_DIR}/server.csr" \
    -CA "${SSL_DIR}/ca.crt" -CAkey "${SSL_DIR}/ca.key" -CAcreateserial \
    -out "${SSL_DIR}/server.crt" -extfile "${SSL_DIR}/server_ext.cnf"

# Clean up temporary files
rm -f "${SSL_DIR}/server.csr" "${SSL_DIR}/server_ext.cnf" "${SSL_DIR}/ca.srl"

# Set permissions
chmod 600 "${SSL_DIR}/ca.key" "${SSL_DIR}/server.key"
chmod 644 "${SSL_DIR}/ca.crt" "${SSL_DIR}/server.crt"

echo ""
echo "Certificates generated successfully!"
echo ""
echo "Files created:"
echo "  ${SSL_DIR}/ca.crt     - CA certificate"
echo "  ${SSL_DIR}/ca.key     - CA private key"
echo "  ${SSL_DIR}/server.crt - Server certificate"
echo "  ${SSL_DIR}/server.key - Server private key"
echo ""
