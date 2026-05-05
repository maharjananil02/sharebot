# NEPSE Trading Bot - Deployment Guide

## Current Situation
Your app is running on **Streamlit Cloud** (indicated by the `/mount/src/` path in the database info). The database file exists and is writable, but it's stored in an **ephemeral (temporary) mount** that gets completely wiped on each restart.

**Result:** Your database file gets recreated fresh every restart, so all positions are lost.

---

## Deployment Options & Solutions

### 1. **Streamlit Cloud + External Database** ⭐ RECOMMENDED
Use Streamlit Cloud for the web UI, but store data in a managed database service.

**Setup:**
```bash
# Install database client
pip install supabase  # or psycopg2 for PostgreSQL

# Create account at:
# - Supabase (PostgreSQL): https://supabase.com (free tier available)
# - Firebase: https://firebase.google.com
# - Railway: https://railway.app (PostgreSQL hosting)

# Add to .env or Streamlit Secrets:
DATABASE_URL=postgresql://user:pass@host/dbname
```

**Benefits:**
- ✅ Data persists across restarts
- ✅ Scalable and reliable
- ✅ Can access from anywhere
- ✅ Streamlit Cloud free tier compatible

**Implementation:** Modify `position_store.py` and `trade_history.py` to use SQLAlchemy + external DB instead of local SQLite.

---

### 2. **Streamlit Cloud + Persistent Directory (Limited)**
Try using `~/.streamlit/` which *sometimes* survives restarts on Streamlit Cloud.

**Setup:**
```bash
# Set in .env or Streamlit Secrets:
POSITIONS_DB_PATH=~/.streamlit/positions.db
TRADES_DB_PATH=~/.streamlit/trades.db
```

**Limitations:**
- ⚠️ May still lose data on redeployment
- ⚠️ No backup or recovery
- ⚠️ Limited to small databases

**Try this first** if you want a quick workaround before setting up external DB.

---

### 3. **Self-Hosted Docker** (For non-Streamlit Cloud)
If you own/rent a server, use Docker with persistent volumes.

**Setup:**
```bash
# 1. Build image
docker build -t nepse-trading .

# 2. Run with persistent volume
docker run -d \
  -p 8501:8501 \
  -v /data/nepse-trading:/app/data \
  --env-file .env \
  nepse-trading

# 3. Set in .env:
POSITIONS_DB_PATH=/app/data/positions.db
TRADES_DB_PATH=/app/data/trades.db
```

**Benefits:**
- ✅ Full control over data
- ✅ Local database performance
- ✅ No external service dependencies

**Requirements:**
- VPS/server (AWS EC2, DigitalOcean, Linode, etc.)
- Docker installed
- Persistent volume or mounted storage

---

### 4. **Google Cloud Run + Cloud SQL** (Advanced)
Use Google Cloud Platform for both app and database.

```bash
# Create Cloud SQL PostgreSQL instance
gcloud sql instances create nepse-db --database-version=POSTGRES_15

# Deploy to Cloud Run with Cloud SQL proxy
gcloud run deploy nepse-trading \
  --source . \
  --add-cloudsql-instances PROJECT_ID:REGION:nepse-db
```

**Benefits:**
- ✅ Fully managed, serverless
- ✅ Auto-scaling
- ✅ Google-grade reliability

---

## Current Status & Next Steps

### ✅ What's Ready
- Code supports `~/.streamlit/` paths (tilde expansion)
- Fallback logic if primary path fails
- Better error messages for permission issues

### 📋 Recommended Action Plan

**Option A: Quick Workaround (5 minutes)**
```bash
# Use ~/.streamlit/ directory
# Edit .env on Streamlit Cloud:
POSITIONS_DB_PATH=~/.streamlit/positions.db
TRADES_DB_PATH=~/.streamlit/trades.db

# Deploy and test
# Note: This is temporary—may still lose data on redeployment
```

**Option B: Proper Solution (30-60 minutes)**
```bash
# 1. Create free Supabase account: https://supabase.com
# 2. Create PostgreSQL database
# 3. Get connection string
# 4. Add to .env or Streamlit Secrets
# 5. Update position_store.py and trade_history.py to use SQLAlchemy
# 6. Deploy and test

# Full example will be in EXTERNAL_DB.md (coming soon)
```

**Option C: Self-Hosted (No recurring monthly cost)**
```bash
# 1. Rent a VPS ($5-10/month on DigitalOcean, Linode, etc.)
# 2. Install Docker
# 3. Use docker-compose.yml with volume mounts
# 4. Point .env to /app/data/

# Full example will be in DOCKER_COMPOSE.md (coming soon)
```

---

## How to Deploy Latest Code

### On Streamlit Cloud:
```bash
# 1. Pull latest changes
git pull origin main

# 2. Streamlit Cloud auto-redeploys on git push
git push origin main

# 3. Check sidebar: "Database Info" should show path
```

### Testing Persistence:
1. **Add a position** through the UI
2. **Screenshot the "Database Info"** in sidebar (shows path, size, symbols)
3. **Restart the app** (redeploy or manual restart)
4. **Check if position is still there**
5. **Screenshot database info again** (compare size/count)

---

## Troubleshooting

### "Database exists but 0 positions loaded"
- This is the ephemeral filesystem issue described above
- Positions are being saved, but to a temp location that gets wiped
- **Solution:** Use external database or `~/.streamlit/` directory

### "PermissionError: Permission denied"
- App user doesn't have write access to the directory
- **Solution:** Use `~/.streamlit/` or `/tmp/`

### "Database file size is 12288 bytes but no data"
- SQLite database was created but immediately wiped on next restart
- All prior positions were lost to ephemeral filesystem
- **Solution:** Migrate to external database to prevent future loss

---

## External Database Examples (Coming Soon)

Will add:
- `EXTERNAL_DB.md` — Supabase + SQLAlchemy setup
- `DOCKER_COMPOSE.md` — Self-hosted Docker + volumes
- `MIGRATION.md` — How to migrate from SQLite to PostgreSQL

For now, use Option A (quick workaround) or reach out for help with Option B/C.

---

## Questions?

If the `~/.streamlit/` path still doesn't persist, you'll need to:
1. Confirm you're on Streamlit Cloud (you are—the path proves it)
2. Set up external PostgreSQL database (see Option B above)
3. Update data models to use SQLAlchemy ORM

**Current Status:** Updated to support `~/.streamlit/` paths with fallback. Test by restarting the app and checking sidebar.
