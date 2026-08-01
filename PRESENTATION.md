
# ABIA MIGRATION OBSERVATORY — PRESENTATION GUIDE

## Public URL (Live During Tunnel)
https://town-wishlist-plugins-sources.trycloudflare.com

## Local URL (Always Works)
http://127.0.0.1:8001/public-dashboard/

## What to Demo (In Order)

### 1. Public Portal (No Login)
- Landing page with 6 cards
- Real Abia State Government logo
- Animated stats + hover effects

### 2. Data Collection Center
- 6 form types: Migration, Trade, Sports, Hotspot, Returnee, General
- Click "Fill Form" → fill sample data → Submit
- Show: "Form submitted successfully. Reference: #1"

### 3. Database Tables (Live Data)
- /api/v1/migrants/ → HTML table with submitted record
- /api/v1/cases/ → Cases table
- /api/v1/referrals/ → Referrals table
- Add ?format=json for API view

### 4. Offline Demo (If time permits)
- Open Chrome DevTools → Network → Offline
- Fill a form → "Form saved offline"
- Go back online → "Syncing queued forms..."
- Refresh table → new record appears

### 5. Admin Dashboard (Login Required)
- /admin/ → admin / admin123
- /dashboard/ → Command Center (after login)
- Show: Infrastructure status, quick actions

### 6. Partner Sync (Background)
- Mention: Celery syncs to NCFRMI & IOM every 6 hours
- Mention: IPFS backup for data permanence
- Mention: AI risk prediction via Ollama

## Key Talking Points

| Stakeholder | Value |
|---|---|
| **Governor's Office** | Real-time migration trends, hotspot alerts, evidence-based budget |
| **NCFRMI (Federal)** | Auto-sync compliance reports, standardized state data |
| **IOM / GIZ** | Single API endpoint, no more Excel email chains |
| **Field Agents** | Offline-capable PWA, works in remote LGA areas |
| **Migrants** | Self-registration, status check, feedback channel |

## Infrastructure Stack
- PostgreSQL + PostGIS (spatial data)
- Redis + Celery (background tasks)
- Django + Bootstrap 5 (web platform)
- IPFS (permanent document storage)
- Ollama AI (risk prediction)
- Cloudflare Tunnel (public access)

## Commands During Presentation
# Restart tunnel if needed:
cloudflared tunnel --url http://127.0.0.1:8001

# Check all endpoints:
curl -s http://127.0.0.1:8001/public-dashboard/ | head -1

# View queued offline forms (in browser console):
# > indexedDB.open('AbiaObservatoryDB').then(db => {
# >   db.transaction('formQueue').objectStore('formQueue').getAll().then(console.log)
# > })
