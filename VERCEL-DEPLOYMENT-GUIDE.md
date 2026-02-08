# Vercel Deployment Guide — Fatima Zehra Boutique

## Status
✅ **Files Created**: `vercel.json`, `api/index.py`, `api/requirements.txt` committed and pushed to main.
⏳ **Next Step**: Link repo to Vercel + set environment variables (manual via dashboard).

---

## What Was Deployed

| File | Purpose |
|------|---------|
| `vercel.json` | Vercel build configuration (Next.js + Python function) |
| `api/index.py` | ASGI entry-point that loads unified FastAPI backend |
| `api/requirements.txt` | Python dependencies for Vercel function |
| `learnflow-app/netlify/functions/api.py` | Unified backend (users, products, orders, chat) — unchanged |

**Architecture:**
```
Browser → <site>.vercel.app (Next.js static export)
           ├── /* → frontend pages
           └── /api/* → rewrite to /api/index.py
                          └── FastAPI app (unified backend)
                              ├── Neon PostgreSQL
                              └── OpenAI GPT-4o
```

---

## Step 1: Link GitHub Repo to Vercel

1. Go to **https://vercel.com/dashboard**
2. Click **"Add New"** → **"Project"**
3. Select **"Import Git Repository"**
4. Search for: `FATIMA-ZEHRA-BOUTIQUE-APP`
5. Click **"Import"**
6. Configure project:
   - **Project Name**: `fatima-zehra-boutique` (or your preferred name)
   - **Framework Preset**: `Next.js`
   - **Root Directory**: leave blank (Vercel auto-detects)
7. Click **"Deploy"**

**Note**: The initial deploy will fail because environment variables are missing. That's expected—fix in Step 2.

---

## Step 2: Set Environment Variables

From the Vercel dashboard for your project:

1. Go to **Settings** → **Environment Variables**
2. Add the following **Production** variables:

### Secret Variables (from `.env.backend`)

**⚠️ IMPORTANT**: These are **secrets**. Paste values exactly as shown (watch for leading/trailing spaces).

```
DATABASE_URL
postgresql://[your-neon-user]:[your-neon-password]@[your-neon-host]/neondb?sslmode=require&channel_binding=require
```

```
OPENAI_API_KEY
sk-proj-[your-actual-openai-api-key]
```

```
JWT_SECRET
your-random-32-character-secret-key-fatima-zehra-2026
```

### Non-Secret Variables

```
ENVIRONMENT
production
```

(Optional but recommended for debugging):
```
LOG_LEVEL
INFO
```

---

## Step 3: Redeploy

After setting env vars:

1. Go to **Deployments** tab
2. Click the failed deployment (top of list)
3. Click **"Redeploy"**
4. Wait for build to complete (2–3 minutes)

---

## Step 4: Verify Deployment

Once deployment succeeds, test these endpoints:

### Health Check
```bash
curl https://<your-site>.vercel.app/api/health
# Expected: {"status":"ok"}
```

### Categories
```bash
curl https://<your-site>.vercel.app/api/categories
# Expected: JSON array with 4 categories
```

### Products
```bash
curl https://<your-site>.vercel.app/api/products?limit=3
# Expected: JSON with 3 products + total count
```

### Frontend
Open in browser: `https://<your-site>.vercel.app/`
- Page should render with 40 products
- ChatWidget button visible bottom-right

### Test Full Flow

1. **Register**: `/auth/register`
   - Name: John Doe
   - Email: john@example.com
   - Password: password123
   - Submit → success message

2. **Login**: `/auth/login`
   - Email: john@example.com
   - Password: password123
   - Submit → redirects to `/`

3. **Profile**: `/profile`
   - User data should render (confirms JWT working)

4. **Chat**: Click ChatWidget
   - Type: "Hello"
   - Expect AI response from OpenAI (confirms database + chat_messages table)

---

## What's Different from Netlify?

| Feature | Netlify | Vercel | Notes |
|---------|---------|--------|-------|
| **Streaming SSE** | Works (chunked response) | Buffered (arrives all at once) | ChatWidget handles both gracefully |
| **Cold Start** | ~1–2s | ~500ms–1s | Vercel is slightly faster |
| **Max Timeout** | 10s (Hobby) → 60s (Pro) | 10s (Hobby) → 60s (Pro) | Same |
| **Function Size** | 50MB | 50MB | Same |

The unified backend works identically on both—only response buffering differs (cosmetic).

---

## Troubleshooting

### Build Fails with "Python builder not found"
- **Cause**: Vercel might not detect `api/` as a Python function.
- **Fix**: Ensure `api/index.py` + `api/requirements.txt` both exist (they do).

### "ModuleNotFoundError: No module named 'learnflow_app'"
- **Cause**: `api/index.py` path resolves to wrong location.
- **Fix**: Verify absolute path in `api/index.py` line 11:
  ```python
  os.path.join(_here, "..", "learnflow-app", "netlify", "functions", "api.py")
  ```

### Database Connection Failed
- **Cause**: `DATABASE_URL` env var not set or incorrect.
- **Fix**: Re-check value in Vercel Settings → Environment Variables. Paste from `.env.backend`, watch for spaces.

### "OPENAI_API_KEY not set"
- **Cause**: Secret not passed to function.
- **Fix**: Go to Vercel Settings → Environment Variables, verify `OPENAI_API_KEY` is set.

### Chat Responses Slow (5–10s delay)
- **Cause**: Cold function start + OpenAI latency.
- **Fix**: First request warms up the function. Subsequent requests are faster. Normal for serverless.

### Next.js Build Fails
- **Cause**: Missing `next.config.js` or broken config.
- **Fix**: Verify `learnflow-app/app/frontend/next.config.js` exists and has:
  ```js
  output: 'export'
  ```

---

## Rollback (If Something Goes Wrong)

1. Go to **Deployments** in Vercel dashboard
2. Find the last known good deployment
3. Click **"..."** → **"Promote to Production"**
4. Vercel reverts instantly

---

## What Happens Automatically

- **Push to `main`** → Vercel CI/CD triggers auto-deploy
- **Pull request** → Preview deployment created (testable before merge)
- **Any error** → Rollback to last good deployment (if promoted)

---

## Next Steps After Verification

1. ✅ Verify all endpoints respond correctly
2. ✅ Test user registration / login / profile
3. ✅ Test chat (AI responses)
4. ✅ Test product browsing + filtering
5. ✅ Share `https://<your-site>.vercel.app` with team/client

---

## Cost Notes

**Vercel Free Tier**:
- ✅ Unlimited deployments
- ✅ Unlimited bandwidth
- ✅ 12 concurrent serverless functions
- ✅ 60 requests/minute (most use cases OK)
- ❌ No support for long-running tasks (10s timeout)

**If you need longer timeouts or more concurrency**, upgrade to **Pro** ($20/month).

---

## Quick Reference: Env Var Names

These are **case-sensitive**. Use exactly as shown:

```
DATABASE_URL
OPENAI_API_KEY
JWT_SECRET
ENVIRONMENT
LOG_LEVEL (optional)
```

NOT:
- `database_url` ❌
- `openai_key` ❌
- `jwt` ❌

---

## Support

If deployment fails:
1. Check **Vercel Logs** (Deployments tab → click deployment → Logs)
2. Check **Function Logs** (if Python function fails)
3. Verify env vars are set in Settings → Environment Variables
4. Verify database is reachable from public internet (check Neon settings)

---

**Deployment Status**: Ready for manual setup via Vercel dashboard.
**Est. Time**: 5–10 minutes (including verification).

