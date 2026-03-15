# 🎓 MentorSpace — Mentor Portal

A redesigned, production-ready mentor portal with a rich dashboard.

\---

## ✨ What's New

* **Beautiful Dashboard** — stat cards, CGPA distribution chart, top performers, recent students
* **Sidebar Navigation** — clean dark sidebar with mobile support
* **Live notifications** — toast alerts for all actions
* **Works standalone** — `mentor\_portal.html` talks directly to Supabase (no Flask needed for most features)
* **Fixed deployment bugs** — proper `host="0.0.0.0"`, `PORT` env var, gunicorn support, fixed RLS token passing

\---

## 🚀 Option A — Standalone HTML (Recommended, No Server Needed)

Just open `mentor\_portal.html` in any browser — or host it on GitHub Pages, Netlify, or Vercel.

* ✅ Auth (Supabase)
* ✅ Dashboard with stats
* ✅ Add / Edit / Delete students
* ✅ CSV export \& profile download
* ⚠️ Email announcements require Flask (see Option B)

\---

## 🚀 Option B — Full Flask Deployment

### Local

```bash
pip install -r requirements.txt
python app.py
```

Visit: http://localhost:5000

### Deploy to Render.com

1. Push this folder to a GitHub repo
2. Go to https://render.com → New Web Service → Connect repo
3. Set:

   * **Build command**: `pip install -r requirements.txt`
   * **Start command**: `gunicorn app:app`
4. Add Environment Variables:

```
   SUPABASE\_URL=https://fdcxktdnuxpoqlkxihuo.supabase.co
   SUPABASE\_ANON\_KEY=eyJ...
   EMAIL=sprithika990@gmail.com
   EMAIL\_PASSWORD=xnzyrgtprnjxndlo
   SECRET\_KEY=mentor-portal-flask-secret-2024
   FLASK\_ENV=production
   ```

### Deploy to Railway.app

```bash
railway login
railway init
railway up
```

\---

## 🔧 File Structure

```
mentor\_portal.html    ← Standalone frontend (works without Flask)
app.py                ← Fixed Flask backend
requirements.txt      ← Python dependencies (includes gunicorn)
Procfile              ← For Render/Heroku deployment
schema.sql            ← Run ONCE in Supabase SQL Editor
.env                  ← Local credentials (don't commit!)
```

\---

## 🛠️ Common Deployment Errors Fixed

|Error|Fix Applied|
|-|-|
|`Connection refused`|Added `host="0.0.0.0"` so the server binds to all interfaces|
|`Port already in use`|Now reads `PORT` from environment variable|
|`gunicorn: not found`|Added `gunicorn` to requirements.txt + Procfile|
|`RLS policy violation`|Fixed token passing with `postgrest.auth(token)`|
|`ModuleNotFoundError`|requirements.txt has compatible pinned versions|
|`SUPABASE\_URL not set`|Added startup check with helpful error message|

\---

## 📧 Email Setup

The email uses Gmail App Password. If emails fail:

1. Google Account → Security → 2-Step Verification → App Passwords
2. Create App Password → paste into `.env` as `EMAIL\_PASSWORD`

