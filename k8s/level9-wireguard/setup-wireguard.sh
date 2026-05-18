#!/bin/bash
# WireGuard Setup Script — Run on both Server and Client (Ubuntu)
# Usage: sudo bash setup-wireguard.sh [server|client]

set -e

ROLE=${1:-"server"}

echo "=== WireGuard Setup ($ROLE) ==="

# 1. Install WireGuard
apt update && apt install -y wireguard

# 2. Generate keys
cd /etc/wireguard
umask 077
wg genkey | tee privatekey | wg pubkey > publickey

echo ""
echo "=== Keys Generated ==="
echo "Private Key: $(cat privatekey)"
echo "Public Key:  $(cat publickey)"
echo ""
echo "=== Next Steps ==="

if [ "$ROLE" = "server" ]; then
    echo "1. Copy wg0-server.conf.example → /etc/wireguard/wg0.conf"
    echo "2. Replace <SERVER_PRIVATE_KEY> with: $(cat privatekey)"
    echo "3. Replace <HOME_PUBLIC_KEY> with the public key from Home Lab"
    echo "4. Enable: systemctl enable --now wg-quick@wg0"
    echo "5. FortiGate: NAT UDP 51820 → this VM's IP"
    echo ""
    echo "Enable IP forwarding:"
    echo "  echo 'net.ipv4.ip_forward=1' >> /etc/sysctl.conf && sysctl -p"
else
    echo "1. Copy wg0-client.conf.example → /etc/wireguard/wg0.conf"
    echo "2. Replace <HOME_PRIVATE_KEY> with: $(cat privatekey)"
    echo "3. Replace <SERVER_PUBLIC_KEY> with the public key from Company Lab"
    echo "4. Replace <COMPANY_PUBLIC_IP> with your company's public IP"
    echo "5. Enable: systemctl enable --now wg-quick@wg0"
fi

echo ""
echo "=== Verify ==="
echo "  wg show"
echo "  ping 10.0.0.1  (from client)"
echo "  ping 10.0.0.2  (from server)"
