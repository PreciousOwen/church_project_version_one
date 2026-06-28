# KKKT DMP Server Setup (Ubuntu 24.04)

Follow these commands on the server (ubuntu@ip-172-31-25-149). Run them in order.

## 1) System packages
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip build-essential pkg-config \
  libmysqlclient-dev mysql-server nginx unzip
```

## 2) Unzip project
```bash
cd ~
unzip -o church_project.zip
cd church_project
```

## 3) Create MySQL DB + import SQL dump
```bash
sudo mysql -u root <<'SQL'
CREATE DATABASE IF NOT EXISTS kkkt_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
SQL

sudo mysql -u root kkkt_db < sql_dump_dmp.sql
```

## 4) Create venv + install deps
here is the venv {source /home/ubuntu/.venv/bin/activate}

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 5) Environment variables
```bash
cat > .env <<'EOF'
DJANGO_SECRET_KEY=replace_with_strong_secret
DB_NAME=kkkt_db
DB_USER=kkkt_user
DB_PASSWORD=strongpassword
DB_HOST=127.0.0.1
DB_PORT=3306
EOF

set -a; source .env; set +a
```

## 6) Migrate + collectstatic
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

## 7) (Optional) Load data
```bash
python manage.py loaddata data-migration.json
```

## 8) Gunicorn systemd service
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

## 9) Nginx config
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

## 10) Firewall (optional)
```bash
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

## 11) SSL (optional, if DNS is ready)
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d kkktdmp.com -d www.kkktdmp.com
```
