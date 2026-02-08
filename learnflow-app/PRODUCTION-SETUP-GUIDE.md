# 🚀 PRODUCTION SETUP GUIDE
## Fatima Zehra Boutique - Enable Chat & Complete Deployment

**Status**: Frontend code ✅ updated and pushed to GitHub
**Next Step**: Add OpenAI API key to Vercel
**Time Required**: 5 minutes

---

## 📊 CURRENT STATUS

| Component | Status | URL | Action |
|-----------|--------|-----|--------|
| **Frontend** | ✅ LIVE | https://fatima-zehra-boutique.vercel.app/ | Configured ✅ |
| **Backend API** | ✅ LIVE | /api/ | Configured ✅ |
| **Database** | ✅ LIVE | Neon PostgreSQL | Configured ✅ |
| **Chat AI** | ⚠️ Deployed but Missing Key | /api/chat/messages | NEEDS OpenAI Key |

---

## 🔑 WHAT'S MISSING: OpenAI API Key

The chat service is deployed but needs the OpenAI API key in Vercel environment variables.

**Your API Key**:
Get your OpenAI API key from [platform.openai.com](https://platform.openai.com/api-keys)
(Keys starting with `sk-proj-` format)

---

## ⚙️ HOW TO ADD OpenAI KEY TO VERCEL

### **Option 1: Via Vercel Dashboard (Recommended)**

**Step 1**: Go to Vercel Project Settings
```
👉 https://vercel.com/hafiznaveedchuhans-projects/fatima-zehra-boutique/settings/environment-variables
```

**Step 2**: Click "Add New"
```
Name:   OPENAI_API_KEY
Value:  sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
(Paste your actual OpenAI API key from [platform.openai.com](https://platform.openai.com/api-keys))

**Step 3**: Make sure to select:
- ✅ Production
- ✅ Preview (optional)

**Step 4**: Click "Save"

**Step 5**: Go to "Deployments" tab and click "Redeploy"

---

### **Option 2: Via Vercel CLI**

```bash
# Install Vercel CLI (if not already installed)
npm install -g vercel

# Login to Vercel
vercel login

# Set environment variable
vercel env add OPENAI_API_KEY

# Paste your key: sk-proj-...

# Select target: production

# Redeploy
vercel --prod
```

---

### **Option 3: Via Git + Vercel Auto-Deploy**

Create a `.env.production` file (not committed):
```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
(Paste your actual OpenAI API key from [platform.openai.com](https://platform.openai.com/api-keys))

Vercel will read this during build time.

---

## 🧪 TEST CHAT AFTER ADDING KEY

### **Test 1: Via API**
```bash
curl -X POST "https://fatima-zehra-boutique.vercel.app/api/chat/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Show me fancy suits",
    "session_id": "test-session",
    "user_id": 1
  }'
```

**Expected Response**: Streaming AI response from OpenAI

---

### **Test 2: Via Website**
1. Go to: https://fatima-zehra-boutique.vercel.app/
2. Click "Open chat" button (bottom-right)
3. Type: "Show me suits under 10000"
4. Send message
5. Chat should respond with AI recommendations!

---

## 📝 ENVIRONMENT VARIABLES CHECKLIST

Your Vercel project should have these variables set:

### **Required** ✅
- [x] `DATABASE_URL` - Already set
- [x] `JWT_SECRET` - Already set
- [ ] `OPENAI_API_KEY` - **YOU NEED TO ADD THIS**

### **Optional** (Already configured)
- `ENVIRONMENT=production`
- `CORS_ORIGINS=https://fatima-zehra-boutique.vercel.app`

---

## 📋 DEPLOYMENT CHECKLIST

After adding OpenAI key:

- [ ] Copy OpenAI API key from above
- [ ] Go to Vercel project settings
- [ ] Add `OPENAI_API_KEY` environment variable
- [ ] Click "Save"
- [ ] Go to "Deployments" and click "Redeploy"
- [ ] Wait ~2-3 minutes for deployment
- [ ] Visit https://fatima-zehra-boutique.vercel.app/
- [ ] Click "Open chat" button
- [ ] Test chat with: "Show me products"
- [ ] ✅ Confirm AI responds!

---

## 🎯 WHAT HAPPENS AFTER

Once OpenAI key is added:

```
User types: "Show me fancy suits under 10000"
    ↓
Chat widget sends message to /api/chat/messages
    ↓
Backend receives request
    ↓
Backend connects to OpenAI API (using the key)
    ↓
OpenAI returns AI-generated response
    ↓
Backend streams response back to frontend
    ↓
User sees: "Here are some fancy suits within your budget..."
```

---

## 🔍 TROUBLESHOOTING

### Problem: Chat still shows error
**Solution**:
1. Verify API key was added to Vercel (check Environment Variables)
2. Verify "Production" was selected when adding the variable
3. Wait 2-3 minutes after redeploy for changes to take effect
4. Try hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

### Problem: API key is wrong
**Solution**:
1. Your correct key is above - copy it exactly
2. Verify no extra spaces before/after the key
3. Don't share this key publicly - this is a SECRET!

### Problem: Deployment won't redeploy
**Solution**:
1. Go to "Deployments" tab in Vercel
2. Click the three dots menu (...)
3. Click "Redeploy"
4. Wait for build to complete

---

## 🚀 LIVE URLS (After Setup Complete)

```
Frontend:  https://fatima-zehra-boutique.vercel.app/
API Docs:  https://fatima-zehra-boutique.vercel.app/api/docs
Chat API:  https://fatima-zehra-boutique.vercel.app/api/chat/messages
```

---

## 📞 QUICK COMMANDS

### Check Deployment Status
```bash
# Visit Vercel dashboard
https://vercel.com/hafiznaveedchuhans-projects/fatima-zehra-boutique/deployments
```

### View Real-time Logs
```bash
# Via Vercel dashboard > Deployments > Click latest > View Logs
```

### Test Backend Health
```bash
curl https://fatima-zehra-boutique.vercel.app/api/health
# Expected: {"status":"ok"}
```

---

## ✨ SUCCESS METRICS

Once OpenAI key is added, you'll see:

✅ Chat widget opens on homepage
✅ User can type messages
✅ AI responds with product recommendations
✅ Chat history persists
✅ Streaming responses work smoothly

---

## 📝 SUMMARY

**What's Done:**
- ✅ Frontend deployed to Vercel
- ✅ Backend deployed to Vercel
- ✅ Database connected (Neon)
- ✅ API endpoints working
- ✅ Frontend configured to use /api (same-origin)
- ✅ Code committed and pushed to GitHub

**What's Left (5 minutes):**
- ⏳ Add `OPENAI_API_KEY` to Vercel environment variables
- ⏳ Redeploy project
- ⏳ Test chat widget

**That's it!** Your full-stack e-commerce app will be completely ready! 🎉

---

## 🎓 ADDITIONAL RESOURCES

**Learn More:**
- Vercel Env Vars: https://vercel.com/docs/projects/environment-variables
- OpenAI API: https://platform.openai.com/docs/api-reference
- FastAPI Docs: https://fatima-zehra-boutique.vercel.app/api/docs

**Contact:**
- Email: HAFIZNAVEEDCHUHAN@GMAIL.COM
- WhatsApp: +92 300 2385209

---

**Generated**: February 8, 2026
**Status**: Ready for final step!
