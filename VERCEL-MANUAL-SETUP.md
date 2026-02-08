# Vercel Manual Setup — Step by Step

## ⚡ Quick Links

- **Vercel Dashboard**: https://vercel.com/dashboard
- **Your Projects**: https://vercel.com/hn1693244-sources-projects
- **GitHub Repo**: https://github.com/hn1693244-source/FATIMA-ZEHRA-BOUTIQUE-APP

---

## 📋 Step 1: Import GitHub Repository

1. Go to **https://vercel.com/new**
2. Click **"Import Git Repository"**
3. Paste: `https://github.com/hn1693244-source/FATIMA-ZEHRA-BOUTIQUE-APP`
4. Click **"Continue"**

### Configure Project

- **Project Name**: `fatima-zehra-boutique` (or your choice)
- **Framework Preset**: Select **"Next.js"** (Vercel will auto-detect)
- **Root Directory**: Leave empty
- **Environment Variables**: We'll add these next

5. Click **"Deploy"**

**Note**: Build will fail initially because env vars are missing. That's OK—continue to Step 2.

---

## 🔒 Step 2: Add Environment Variables

1. Go to your project on Vercel
2. Click **"Settings"** tab
3. Click **"Environment Variables"** (left sidebar)
4. Add these **for Production** environment:

### Variable 1: DATABASE_URL
- **Name**: `DATABASE_URL`
- **Value**: *(From `learnflow-app/.env.backend` — full PostgreSQL connection string)*
- **Environments**: Check `Production`, `Preview`, `Development`
- Click **"Save"**

### Variable 2: OPENAI_API_KEY
- **Name**: `OPENAI_API_KEY`
- **Value**: *(From `learnflow-app/.env.backend` — your OpenAI API key)*
- **Environments**: Check `Production`, `Preview`, `Development`
- Click **"Save"**

### Variable 3: JWT_SECRET
- **Name**: `JWT_SECRET`
- **Value**: `your-random-32-character-secret-key-fatima-zehra-2026`
- **Environments**: Check `Production`, `Preview`, `Development`
- Click **"Save"**

### Variable 4: ENVIRONMENT
- **Name**: `ENVIRONMENT`
- **Value**: `production`
- **Environments**: Check `Production`
- Click **"Save"**

---

## 🚀 Step 3: Redeploy

1. Go to **"Deployments"** tab
2. Click on the failed deployment (top of list)
3. Click **"Redeploy"** button
4. Wait 2–3 minutes for build to complete

You should see:
- ✅ `vercel.json` analyzed
- ✅ Next.js frontend built
- ✅ Python function built
- ✅ Deployment complete

---

## 🧪 Step 4: Verify Deployment

### Get Your Vercel URL

On the deployment success screen, you'll see something like:
```
✓ Preview: https://fatima-zehra-boutique-abc123.vercel.app
✓ Production: https://fatima-zehra-boutique.vercel.app
```

### Test Endpoints

Replace `<YOUR_URL>` with your actual Vercel URL:

```bash
# Test 1: Health check
curl https://<YOUR_URL>/api/health
# Expected: {"status":"ok"}

# Test 2: Categories (4 categories)
curl https://<YOUR_URL>/api/categories
# Expected: JSON array with 4 items

# Test 3: Products (40 seeded products)
curl https://<YOUR_URL>/api/products?limit=5
# Expected: {"data": [...], "total": 40}

# Test 4: Frontend renders
curl https://<YOUR_URL>/ | grep -o "Fatima Zehra" | head -1
# Expected: Fatima Zehra
```

---

## 🌐 Step 5: Full UI Testing

Open browser and visit: `https://<YOUR_URL>`

### Homepage
- [ ] Page loads with products grid
- [ ] 40 products visible
- [ ] Product images load
- [ ] Prices display correctly
- [ ] ChatWidget button visible (bottom-right)

### Navigation
- [ ] Click product → details page
- [ ] Click "Register" → registration form
- [ ] Click "Login" → login form
- [ ] Click "Profile" → profile page (only if logged in)

### User Registration
```
URL: https://<YOUR_URL>/auth/register

1. Fill form:
   - Full Name: John Doe
   - Email: john@example.com
   - Password: Password123!
   - Confirm Password: Password123!

2. Click "Register"
3. Expected: Success message
4. You should be redirected to home
```

### User Login
```
URL: https://<YOUR_URL>/auth/login

1. Fill form:
   - Email: john@example.com
   - Password: Password123!

2. Click "Login"
3. Expected: Redirects to /
4. Your name should appear in navbar
```

### View Profile
```
URL: https://<YOUR_URL>/profile

After login, you should see:
- Your name: John Doe
- Your email: john@example.com
- Edit button (for future use)
```

### Test Chat Widget
```
1. Click ChatWidget button (bottom-right)
2. Type: "Hello"
3. Expected: AI response from OpenAI
4. Type: "Show me dresses"
5. Expected: Product recommendations
6. Chat history should persist
```

### Test Product Filtering
```
URL: https://<YOUR_URL>/products

1. Click category filter (e.g., "Dresses")
2. Products should update
3. Click "Search" and type product name
4. Results should filter in real-time
```

### Test Cart & Checkout
```
1. Browse products
2. Click "Add to Cart" on any product
3. Click cart icon → view items
4. Click "Checkout"
5. Fill shipping info
6. Complete checkout
```

---

## 📊 Example Successful Test Output

```bash
$ curl https://fatima-zehra-boutique.vercel.app/api/health
{"status":"ok"}

$ curl https://fatima-zehra-boutique.vercel.app/api/categories
[
  {"id": 1, "name": "Dresses", ...},
  {"id": 2, "name": "Shoes", ...},
  ...
]

$ curl https://fatima-zehra-boutique.vercel.app/api/products?limit=2
{
  "data": [
    {"id": 1, "name": "Red Summer Dress", "price": "2500.00", ...},
    {"id": 2, "name": "Black Evening Gown", "price": "4500.00", ...}
  ],
  "total": 40
}
```

---

## 🐛 Troubleshooting

### Build Failed: "Python builder not found"
**Solution**: Check that `api/requirements.txt` exists (it should)

### Build Failed: "ModuleNotFoundError"
**Solution**: Verify paths in `api/index.py` are correct

### API Returns 502 Bad Gateway
**Solution**:
1. Check env vars are set in Vercel Settings
2. Check DATABASE_URL is correct
3. Wait 2 minutes (cold start might be slow)
4. Redeploy with fresh build

### Chat Not Working (API Error)
**Solution**: Check OPENAI_API_KEY is set correctly in Vercel Settings

### Frontend Shows "Cannot GET /api/..."
**Solution**: The rewrite in `vercel.json` didn't work. Check:
1. `vercel.json` exists in repo root
2. `api/index.py` exists
3. Redeploy

### Database Connection Failed
**Solution**:
1. Verify DATABASE_URL in `.env.backend` is correct
2. Go to Neon dashboard (https://console.neon.tech)
3. Copy full connection string from there
4. Update in Vercel Settings
5. Redeploy

---

## 📝 Environment Variables Reference

| Var | Source | Example |
|-----|--------|---------|
| `DATABASE_URL` | Neon Dashboard | `postgresql://...` |
| `OPENAI_API_KEY` | OpenAI Dashboard | `sk-proj-...` |
| `JWT_SECRET` | Any 32+ char string | `your-random-32-...` |
| `ENVIRONMENT` | Literal | `production` |

---

## 🔗 Quick Links

- Vercel Dashboard: https://vercel.com/dashboard
- Project Settings: https://vercel.com/hn1693244-sources-projects
- GitHub Repo: https://github.com/hn1693244-source/FATIMA-ZEHRA-BOUTIQUE-APP
- Neon Database: https://console.neon.tech
- OpenAI API Keys: https://platform.openai.com/account/api-keys

---

## ✅ Completion Checklist

- [ ] Repo imported to Vercel
- [ ] DATABASE_URL set in Vercel Settings
- [ ] OPENAI_API_KEY set in Vercel Settings
- [ ] JWT_SECRET set in Vercel Settings
- [ ] ENVIRONMENT set to "production"
- [ ] Redeployed successfully
- [ ] Health check passes (`/api/health`)
- [ ] Categories endpoint works
- [ ] Products endpoint works
- [ ] Frontend loads and renders
- [ ] User can register
- [ ] User can login
- [ ] Chat widget works
- [ ] Product filtering works

---

**Once all checks pass, your app is ready for production! 🎉**

