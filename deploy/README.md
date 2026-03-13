# Deploy with Nginx (Public Access)

This project runs FastAPI behind Nginx:
- App: `127.0.0.1:8000` (uvicorn/systemd)
- Public: `:80` and optionally `:443` via Nginx

## 1) Install Nginx (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install -y nginx
```

## 2) Install the systemd service

```bash
sudo cp /home/lenovo/Workspace/Billiardo-ELSHEIKH/deploy/systemd/billiardo.service /etc/systemd/system/billiardo.service
sudo systemctl daemon-reload
sudo systemctl enable --now billiardo
sudo systemctl status billiardo
```

## 3) Install the Nginx site config

```bash
sudo cp /home/lenovo/Workspace/Billiardo-ELSHEIKH/deploy/nginx/billiardo.conf /etc/nginx/sites-available/billiardo
sudo ln -sf /etc/nginx/sites-available/billiardo /etc/nginx/sites-enabled/billiardo
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

## 4) Open firewall ports (if UFW is enabled)

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload
```

## 5) Make it reachable from outside your local network

1. Find your server LAN IP (for example `192.168.1.20`):
   ```bash
   ip a
   ```
2. On your router, set port-forward rules:
   - WAN `80` -> `192.168.1.20:80`
   - WAN `443` -> `192.168.1.20:443` (after SSL setup)
3. Use your public IP to test from mobile data (not Wi-Fi).

## 6) Optional: HTTPS with Let's Encrypt

Requires a domain pointing to your public IP.

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## Useful checks

```bash
curl http://127.0.0.1:8000/docs
curl http://127.0.0.1
journalctl -u billiardo -f
sudo tail -f /var/log/nginx/error.log
```
