# KKKT DMP Production Setup (Gunicorn + Nginx)

Use these commands on the Ubuntu server.

## 1) Install Gunicorn
```bash
cd ~/church_project
source .venv/bin/activate
pip install gunicorn
```

## 2) Install Nginx
```bash
sudo apt update
sudo apt install -y nginx
```

## 3) Gunicorn systemd service (port 8000)
```bash
sudo tee /etc/systemd/system/kkktdmp.service > /dev/null <<'EOF'
[Unit]
Description=KKKT DMP Gunicorn
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/church_project
EnvironmentFile=/home/ubuntu/church_project/.env
ExecStart=/home/ubuntu/church_project/.venv/bin/gunicorn digital_msharika.wsgi:application \
  --bind 127.0.0.1:8000 \
  --workers 3

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now kkktdmp
sudo systemctl status kkktdmp
```

## 4) Nginx site mapping to port 8000
```bash
sudo tee /etc/nginx/sites-available/kkktdmp > /dev/null <<'EOF'
server {
    listen 80;
    server_name kkktdmp.com www.kkktdmp.com;

    client_max_body_size 20M;

    location /static/ {
        alias /home/ubuntu/church_project/staticfiles/;
    }

    location /media/ {
        alias /home/ubuntu/church_project/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/kkktdmp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 5) (Optional) Open firewall
```bash
sudo ufw allow 'Nginx Full'
sudo ufw enable
```
