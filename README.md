# Prop Trading Simulator Deployment Guide

## Overview

The deployment consists of three main components:
1. Rust backend service ([prop-simulator](https://github.com/razor389/prop-simulator))
2. Streamlit frontend ([prop-simulator-streamlit](https://github.com/yourusername/prop-simulator-streamlit))
3. Nginx reverse proxy

## Directory Structure
```bash
/var/www/
├── prop-simulator/        # Backend service
│   └── target/
│       └── release/
│           └── prop-simulator
└── prop-simulator-streamlit/  # Frontend application
    ├── app.py
    ├── components/
    ├── config/
    ├── utils/
    ├── requirements.txt
    └── venv/
```

## Prerequisites

- Ubuntu 20.04 or newer
- Python 3.9+
- Rust toolchain
- Nginx
- Domain name with DNS configured
- SSL certificate (Let's Encrypt)

## System Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y build-essential curl nginx python3-pip python3-venv git

# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"

# Verify installations
python3 --version
rustc --version
nginx -v
```

## Backend Setup (prop-simulator)

1. **Clone and Build Backend**
```bash
# Clone repository
cd /var/www
git clone https://github.com/razor389/prop-simulator.git
cd prop-simulator

# Build for production
cargo build --release --no-default-features --features "web"
```

2. **Create Systemd Service**
```bash
sudo nano /etc/systemd/system/prop-simulator.service
```

Add:
```ini
[Unit]
Description=Prop Trading Simulator Backend
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/var/www/prop-simulator
ExecStart=/var/www/prop-simulator/target/release/prop-simulator
Restart=always
RestartSec=1
Environment=RUST_LOG=info

# Security settings
NoNewPrivileges=yes
ProtectSystem=full
ProtectHome=read-only
PrivateTmp=yes
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectControlGroups=yes

[Install]
WantedBy=multi-user.target
```

3. **Enable and Start Backend Service**
```bash
sudo systemctl daemon-reload
sudo systemctl enable prop-simulator
sudo systemctl start prop-simulator
```

## Frontend Setup (prop-simulator-streamlit)

1. **Clone Frontend Repository**
```bash
cd /var/www
git clone https://github.com/yourusername/prop-simulator-streamlit.git
cd prop-simulator-streamlit

# Set proper ownership
sudo chown -R $USER:$USER /var/www/prop-simulator-streamlit
```

2. **Set Up Python Virtual Environment**
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

3. **Create Streamlit Configuration**
```bash
mkdir -p .streamlit
nano .streamlit/config.toml
```

Add:
```toml
[server]
address = "0.0.0.0"
port = 8501
maxUploadSize = 10

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

4. **Create Systemd Service**
```bash
sudo nano /etc/systemd/system/prop-simulator-streamlit.service
```

Add:
```ini
[Unit]
Description=Prop Simulator Streamlit Frontend
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/var/www/prop-simulator-streamlit
Environment="PATH=/var/www/prop-simulator-streamlit/venv/bin"
ExecStart=/var/www/prop-simulator-streamlit/venv/bin/streamlit run app.py
Restart=always
RestartSec=1

# Security settings
NoNewPrivileges=yes
ProtectSystem=full
ProtectHome=read-only
PrivateTmp=yes

[Install]
WantedBy=multi-user.target
```

5. **Enable and Start Frontend Service**
```bash
sudo systemctl daemon-reload
sudo systemctl enable prop-simulator-streamlit
sudo systemctl start prop-simulator-streamlit
```

## Nginx Configuration

1. **Create Nginx Configuration**
```bash
sudo nano /etc/nginx/sites-available/prop-simulator
```

2. **Add Configuration**:
```nginx
server {
    server_name yourdomain.net;

    # Frontend proxy
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    # Backend proxy
    location /simulate {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts for long-running simulations
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;

        # Buffer settings
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;

        # Upload size limit
        client_max_body_size 10M;
    }

    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/yourdomain.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.net/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name yourdomain.net;
    return 301 https://$host$request_uri;
}
```

3. **Enable Site and Restart Nginx**
```bash
sudo ln -s /etc/nginx/sites-available/prop-simulator /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## SSL Setup

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.net

# Verify auto-renewal
sudo systemctl status certbot.timer
```

## Updates and Maintenance

### Backend Updates
```bash
cd /var/www/prop-simulator
git pull
cargo build --release --no-default-features --features "web"
sudo systemctl restart prop-simulator
```

### Frontend Updates
```bash
cd /var/www/prop-simulator-streamlit
source venv/bin/activate
git pull
pip install -r requirements.txt
sudo systemctl restart prop-simulator-streamlit
```

## Monitoring and Troubleshooting

### Service Status
```bash
# Check backend status
sudo systemctl status prop-simulator

# Check frontend status
sudo systemctl status prop-simulator-streamlit

# View backend logs
sudo journalctl -u prop-simulator -n 100

# View frontend logs
sudo journalctl -u prop-simulator-streamlit -n 100
```

### Nginx Logs
```bash
# Access logs
sudo tail -f /var/log/nginx/access.log

# Error logs
sudo tail -f /var/log/nginx/error.log
```

## Security Checklist

1. **Firewall Setup**
```bash
sudo ufw allow 22     # SSH
sudo ufw allow 80     # HTTP
sudo ufw allow 443    # HTTPS
sudo ufw enable
```

2. **File Permissions**
```bash
# Set proper ownership
sudo chown -R ubuntu:ubuntu /var/www/prop-simulator
sudo chown -R ubuntu:ubuntu /var/www/prop-simulator-streamlit
```

---

For questions or issues:
- Backend repository: [prop-simulator](https://github.com/razor389/prop-simulator)
- Frontend repository: [prop-simulator-streamlit](https://github.com/yourusername/prop-simulator-streamlit)
```
