#!/bin/bash

# ===========================================
# Server Setup Script (run on GCP instance)
# ===========================================

set -e

echo "=== Updating system ==="
sudo apt update && sudo apt upgrade -y

echo "=== Creating swap (important for e2-micro!) ==="
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

echo "=== Installing Docker ==="
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

echo "=== Installing Docker Compose ==="
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

echo "=== Installing Git ==="
sudo apt install -y git

echo "=== Setup complete! ==="
echo ""
echo "IMPORTANT: Log out and log back in for Docker permissions to take effect"
echo ""
echo "Next steps:"
echo "1. Log out: exit"
echo "2. SSH back in"
echo "3. Clone your repo: git clone <your-repo-url> app"
echo "4. cd app"
echo "5. cp .env.example .env && nano .env"
echo "6. docker-compose -f docker-compose.prod.yml up -d --build"
