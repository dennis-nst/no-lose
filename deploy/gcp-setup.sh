#!/bin/bash

# ===========================================
# Google Cloud e2-micro Setup Script
# ===========================================

set -e

# Configuration
PROJECT_ID="your-project-id"
ZONE="us-west1-b"  # Free tier zones: us-west1, us-central1, us-east1
INSTANCE_NAME="wa-app"

echo "=== Creating GCP e2-micro instance ==="

# Create VM instance
gcloud compute instances create $INSTANCE_NAME \
    --project=$PROJECT_ID \
    --zone=$ZONE \
    --machine-type=e2-micro \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=30GB \
    --boot-disk-type=pd-standard \
    --tags=http-server,https-server

# Create firewall rules
echo "=== Setting up firewall rules ==="

gcloud compute firewall-rules create allow-http \
    --project=$PROJECT_ID \
    --allow=tcp:80 \
    --target-tags=http-server \
    --description="Allow HTTP" || true

gcloud compute firewall-rules create allow-https \
    --project=$PROJECT_ID \
    --allow=tcp:443 \
    --target-tags=https-server \
    --description="Allow HTTPS" || true

echo "=== Instance created! ==="
echo ""
echo "Next steps:"
echo "1. Get external IP:"
echo "   gcloud compute instances describe $INSTANCE_NAME --zone=$ZONE --format='get(networkInterfaces[0].accessConfigs[0].natIP)'"
echo ""
echo "2. SSH into instance:"
echo "   gcloud compute ssh $INSTANCE_NAME --zone=$ZONE"
echo ""
echo "3. Run server-setup.sh on the server"
