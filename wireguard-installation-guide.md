# WireGuard VPN Installation Guide

WireGuard is a modern, fast, and secure VPN protocol that's designed to be simpler and more efficient than traditional VPN solutions like OpenVPN or IPSec.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Linux Installation](#linux-installation)
- [Windows Installation](#windows-installation)
- [macOS Installation](#macos-installation)
- [Android Installation](#android-installation)
- [iOS Installation](#ios-installation)
- [Server Setup](#server-setup)
- [Client Configuration](#client-configuration)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before installing WireGuard, ensure you have:
- Root/administrator access to your system
- A basic understanding of networking concepts
- Your server's public IP address (for server setup)
- A domain name (optional but recommended)

## Linux Installation

### Ubuntu/Debian

```bash
# Update package list
sudo apt update

# Install WireGuard
sudo apt install wireguard

# Install additional tools (optional)
sudo apt install wireguard-tools
```

### CentOS/RHEL/Fedora

```bash
# For CentOS/RHEL 8+
sudo dnf install wireguard-tools

# For older versions
sudo yum install wireguard-tools

# Enable EPEL repository if needed
sudo dnf install epel-release
```

### Arch Linux

```bash
sudo pacman -S wireguard-tools
```

### Generate Key Pair

```bash
# Create WireGuard directory
sudo mkdir -p /etc/wireguard
cd /etc/wireguard

# Generate private key
wg genkey | sudo tee privatekey

# Generate public key from private key
sudo cat privatekey | wg pubkey | sudo tee publickey

# Set proper permissions
sudo chmod 600 privatekey
sudo chmod 600 publickey
```

## Windows Installation

### Method 1: Official Installer

1. Download the official WireGuard installer from [wireguard.com](https://www.wireguard.com/install/)
2. Run the installer as administrator
3. Follow the installation wizard
4. Restart your computer if prompted

### Method 2: Using Chocolatey

```powershell
# Install Chocolatey first if not installed
# Then install WireGuard
choco install wireguard
```

### Method 3: Using Winget

```powershell
winget install WireGuard.WireGuard
```

## macOS Installation

### Method 1: Official Installer

1. Download the official WireGuard installer from [wireguard.com](https://www.wireguard.com/install/)
2. Open the downloaded `.dmg` file
3. Drag WireGuard to Applications folder
4. Launch WireGuard from Applications

### Method 2: Using Homebrew

```bash
brew install wireguard-tools
```

### Method 3: Using MacPorts

```bash
sudo port install wireguard-tools
```

## Android Installation

1. Open Google Play Store
2. Search for "WireGuard"
3. Install the official WireGuard app by Jason A. Donenfeld
4. Launch the app and follow the setup wizard

## iOS Installation

1. Open App Store
2. Search for "WireGuard"
3. Install the official WireGuard app by Jason A. Donenfeld
4. Launch the app and follow the setup wizard

## Server Setup

### 1. Enable IP Forwarding

```bash
# Edit sysctl configuration
sudo nano /etc/sysctl.conf

# Add or uncomment this line:
net.ipv4.ip_forward=1

# Apply changes
sudo sysctl -p
```

### 2. Create Server Configuration

```bash
sudo nano /etc/wireguard/wg0.conf
```

Add the following configuration:

```ini
[Interface]
PrivateKey = YOUR_SERVER_PRIVATE_KEY
Address = 10.0.0.1/24
ListenPort = 51820
SaveConfig = true
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE
```

**Note:** Replace `YOUR_SERVER_PRIVATE_KEY` with your actual private key and `eth0` with your actual network interface.

### 3. Start WireGuard Service

```bash
# Enable WireGuard service
sudo systemctl enable wg-quick@wg0

# Start WireGuard service
sudo systemctl start wg-quick@wg0

# Check status
sudo systemctl status wg-quick@wg0
```

### 4. Configure Firewall

```bash
# Allow WireGuard port
sudo ufw allow 51820/udp

# Enable UFW if not already enabled
sudo ufw enable
```

## Client Configuration

### 1. Generate Client Keys

```bash
# Generate client private key
wg genkey | tee client_privatekey

# Generate client public key
cat client_privatekey | wg pubkey | tee client_publickey
```

### 2. Add Client to Server

Edit the server configuration:

```bash
sudo nano /etc/wireguard/wg0.conf
```

Add client configuration:

```ini
[Interface]
PrivateKey = YOUR_SERVER_PRIVATE_KEY
Address = 10.0.0.1/24
ListenPort = 51820
SaveConfig = true
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

[Peer]
PublicKey = CLIENT_PUBLIC_KEY
AllowedIPs = 10.0.0.2/32
```

### 3. Create Client Configuration File

Create a file named `client.conf`:

```ini
[Interface]
PrivateKey = CLIENT_PRIVATE_KEY
Address = 10.0.0.2/24
DNS = 8.8.8.8, 8.8.4.4

[Peer]
PublicKey = SERVER_PUBLIC_KEY
Endpoint = YOUR_SERVER_IP:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
```

### 4. Import Configuration

#### Linux
```bash
# Copy configuration to WireGuard directory
sudo cp client.conf /etc/wireguard/

# Start the tunnel
sudo wg-quick up client
```

#### Windows
1. Open WireGuard application
2. Click "Import tunnel(s) from file"
3. Select your `client.conf` file
4. Click "Activate"

#### macOS
1. Open WireGuard application
2. Click "Import tunnel(s) from file"
3. Select your `client.conf` file
4. Click "Activate"

#### Mobile
1. Open WireGuard app
2. Tap the "+" button
3. Select "Create from file"
4. Choose your `client.conf` file
5. Tap "Add tunnel"

## Troubleshooting

### Common Issues

#### 1. Connection Fails
- Check if the server is running: `sudo systemctl status wg-quick@wg0`
- Verify firewall settings
- Check if the port is open: `sudo netstat -tulpn | grep 51820`

#### 2. No Internet Access
- Ensure IP forwarding is enabled
- Check iptables rules
- Verify DNS settings in client configuration

#### 3. High Latency
- Check server location
- Verify network interface configuration
- Consider using a closer server

### Useful Commands

```bash
# Check WireGuard status
sudo wg show

# View WireGuard logs
sudo journalctl -u wg-quick@wg0

# Test connectivity
ping 10.0.0.1

# Check routing table
ip route show
```

### Security Best Practices

1. **Keep private keys secure**: Never share private keys
2. **Use strong keys**: WireGuard generates cryptographically strong keys by default
3. **Regular updates**: Keep WireGuard updated to the latest version
4. **Firewall configuration**: Only allow necessary ports
5. **Monitor logs**: Regularly check for unusual activity

## Additional Resources

- [Official WireGuard Documentation](https://www.wireguard.com/quickstart/)
- [WireGuard Book](https://www.wireguard.com/book/)
- [WireGuard GitHub Repository](https://github.com/WireGuard/WireGuard)

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review WireGuard logs
3. Consult the official documentation
4. Search for solutions in the WireGuard community forums

---

**Note**: This guide provides a basic setup. For production environments, consider additional security measures such as:
- Implementing proper authentication
- Setting up monitoring and logging
- Configuring backup servers
- Implementing access controls 