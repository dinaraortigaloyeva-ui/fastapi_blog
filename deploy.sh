#!/bin/bash
set -e

cd /home/ubuntu/fastapi_blog

git pull
.venv/bin/pip install -r requirements.txt

sudo systemctl restart gunicorn
sudo systemctl reload nginx

echo "Deploy muvaffaqiyatli yakunlandi!"
