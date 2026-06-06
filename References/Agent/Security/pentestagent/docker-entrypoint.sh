#!/bin/bash
# PentestAgent Docker Entrypoint

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🔧 PentestAgent Container Starting...${NC}"

# Start VPN if config provided and openvpn is available
if [ -f "/vpn/config.ovpn" ] && command -v openvpn >/dev/null 2>&1; then
    echo -e "${YELLOW}📡 Starting VPN connection...${NC}"
    openvpn --config /vpn/config.ovpn --daemon || echo "openvpn failed to start"
    sleep 5

    # Check VPN connection
    if ip a show tun0 &>/dev/null; then
        echo -e "${GREEN}✅ VPN connected${NC}"
    else
        echo -e "${RED}⚠️ VPN connection may have failed${NC}"
    fi
fi

# Start Tor if enabled and if a service command is available
if [ "$ENABLE_TOR" = "true" ] && command -v service >/dev/null 2>&1; then
    echo -e "${YELLOW}🧅 Starting Tor...${NC}"
    service tor start || echo "tor service not available"
    sleep 3
fi

# Initialize any databases (guarded)
if [ "$INIT_METASPLOIT" = "true" ] && command -v msfdb >/dev/null 2>&1; then
    echo -e "${YELLOW}🗄️ Initializing Metasploit database...${NC}"
    msfdb init 2>/dev/null || echo "msfdb init failed"
fi

# Ensure persistent output directory lives under /app/loot (mounted by compose)
OUTPUT_DIR="/app/loot/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

# Optionally chown mounted volume on startup (only when running as root and explicitly enabled)
if [ "$(id -u)" = "0" ] && [ "${CHOWN_ON_START,,}" = "true" ]; then
    # If PUID/PGID supplied use them, otherwise keep default permissions
    if [ -n "${PUID:-}" ] && [ -n "${PGID:-}" ]; then
        groupadd -g ${PGID} pentestagent 2>/dev/null || true
        useradd -u ${PUID} -g ${PGID} -m pentestagent 2>/dev/null || true
        chown -R ${PUID}:${PGID} /app/loot || true
    else
        chown -R pentestagent:pentestagent /app/loot 2>/dev/null || true
    fi
fi

export PENTESTAGENT_OUTPUT_DIR="$OUTPUT_DIR"

echo -e "${GREEN}📁 Output directory: $OUTPUT_DIR${NC}"
echo -e "${GREEN}🚀 Starting PentestAgent...${NC}"

# Execute the main command
exec "$@"
