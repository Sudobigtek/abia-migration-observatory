#!/bin/bash
cd ~/abia-migration-observatory/abia-app
source ../.venv/bin/activate

# Kill old
pkill -9 -f "manage.py runserver" 2>/dev/null
pkill -9 -f "cloudflared tunnel" 2>/dev/null
sleep 2

# Start Django with nohup (survives terminal close)
nohup python3 -B manage.py runserver 0.0.0.0:8001 > /tmp/django.log 2>&1 &
sleep 4

# Start Cloudflare tunnel with nohup
nohup cloudflared tunnel --url http://127.0.0.1:8001 > /tmp/cloudflare.log 2>&1 &
sleep 10

# Extract and display URL
URL=$(grep -oP 'https://[a-zA-Z0-9-]+\.trycloudflare\.com' /tmp/cloudflare.log | head -1)
if [ -n "$URL" ]; then
    echo "$URL" > /tmp/tunnel_url.txt
    echo ""
    echo "=========================================="
    echo " PLATFORM LIVE: $URL"
    echo "=========================================="
    echo " $URL/           ← Observatory"
    echo " $URL/japa/      ← Japa for Development"
    echo " $URL/institute/ ← Institute for Migration Governance and Policy"
    echo " $URL/corps/     ← Migration Volunteer Corps"
    echo " $URL/admin/     ← Django Admin"
    echo "=========================================="
else
    echo "[ERROR] Tunnel failed. Check /tmp/cloudflare.log"
fi
