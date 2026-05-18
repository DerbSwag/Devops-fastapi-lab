# Level 9 — WireGuard Site-to-Site VPN

Connect Home Lab ↔ Company Lab through an encrypted tunnel so k3s nodes can communicate across sites.

## Architecture

```
┌─── Home Lab ─────────────────┐         ┌─── Company Lab (Proxmox) ──────┐
│                               │         │                                 │
│  k3s node                     │         │  WireGuard VM (Ubuntu)          │
│  WireGuard client             │         │  LAN IP: 192.168.1.x           │
│  Tunnel IP: 10.0.0.2/24      │◄───────►│  Tunnel IP: 10.0.0.1/24        │
│                               │  UDP    │                                 │
│  Home subnet: 192.168.0.0/24 │  51820  │  Company subnets:               │
│                               │         │  - 192.168.1.0/24 (Office)      │
└───────────────────────────────┘         │  - 192.168.2.0/24 (Production) │
                                          │                                 │
                                          │  FortiGate: port forward        │
                                          │  UDP 51820 → WireGuard VM       │
                                          └─────────────────────────────────┘
```

## Tunnel Network

| Node | Tunnel IP | Role |
|------|-----------|------|
| Company Lab VM | 10.0.0.1 | Server (listens on :51820) |
| Home Lab node | 10.0.0.2 | Client (connects to server) |

## Setup Steps

### 1. Company Lab (Server)

```bash
# On Ubuntu VM in Proxmox
sudo bash setup-wireguard.sh server
# Follow the printed instructions
```

### 2. Home Lab (Client)

```bash
# On k3s node or dedicated VM
sudo bash setup-wireguard.sh client
# Follow the printed instructions
```

### 3. FortiGate Port Forward

```
config firewall policy
    edit <next-id>
        set srcintf "wan1"
        set dstintf "internal"
        set srcaddr "all"
        set dstaddr "WireGuard-VM"
        set service "UDP-51820"
        set action accept
    next
end

config firewall vip
    edit "WireGuard-VPN"
        set extintf "wan1"
        set mappedip "192.168.1.x"
        set portforward enable
        set extport 51820
        set mappedport 51820
        set protocol udp
    next
end
```

### 4. Verify

```bash
# On either side
wg show

# From Home → Company
ping 10.0.0.1
ping 192.168.1.10  # Access company resources

# From Company → Home
ping 10.0.0.2
```

## Files

| File | Purpose |
|------|---------|
| `wg0-server.conf.example` | Server config template (Company Lab) |
| `wg0-client.conf.example` | Client config template (Home Lab) |
| `setup-wireguard.sh` | Automated setup script |

## Security Notes

- Private keys are generated on each machine, never shared
- Only public keys are exchanged between peers
- All traffic through tunnel is encrypted (ChaCha20)
- FortiGate only exposes UDP 51820 (single port)

## After Setup — What's Possible

- `kubectl` from Home → Company k3s cluster
- ArgoCD cross-site sync
- Prometheus federation (scrape metrics across sites)
- Multi-cluster service discovery (Level 12 prerequisite)
