#!/bin/bash
pkill -9 -f "manage.py runserver" 2>/dev/null
pkill -9 -f "cloudflared tunnel" 2>/dev/null
echo "[STOPPED] Django server and Cloudflare tunnel"
