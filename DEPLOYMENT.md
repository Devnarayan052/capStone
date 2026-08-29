# AutoVal AI — Deployment Guide
## Vercel (Frontend) + Render (Backend) + carval.co.in Domain

---

## What was configured automatically

| File | Purpose |
|---|---|
| `client/vercel.json` | SPA rewrite so React Router works on direct URLs |
| `render.yaml` | Tells Render how to build and start the FastAPI server |
| `server/main.py` CORS | Now allows `carval.co.in`, `www.carval.co.in`, `*.vercel.app` |
| `.gitignore` | Fixed — models, data, and source files all committed and pushed |

Everything is now **pushed to GitHub → `Devnarayan052/capStone`**.

---

## Step 1 — Deploy Backend on Render

1. Go to **[render.com](https://render.com)** → Sign in → **New → Web Service**
2. Connect your **GitHub account** → Select repo **`Devnarayan052/capStone`**
3. Fill in:

   | Field | Value |
   |---|---|
   | **Name** | `autoval-api` (or anything) |
   | **Root Directory** | `server` |
   | **Runtime** | `Python 3` |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
   | **Instance Type** | Free (or Starter for no cold starts) |

4. Click **Create Web Service** → wait ~3 min for first build
5. Once deployed, Render gives you a URL like:
   ```
   https://autoval-api.onrender.com
   ```
   **Copy this URL — you need it in Step 2.**

6. Test it — open this in your browser:
   ```
   https://autoval-api.onrender.com/health
   ```
   Should return:
   ```json
   {"status":"ok","model_loaded":true,"car_specs_brands":34,"car_specs_models":276}
   ```

> **Note on Free tier:** Render free instances sleep after 15 min idle. First request after sleep takes ~30 sec. Upgrade to Starter ($7/mo) to keep it always-on for production.

---

## Step 2 — Deploy Frontend on Vercel

1. Go to **[vercel.com](https://vercel.com)** → Sign in → **Add New → Project**
2. Import **`Devnarayan052/capStone`** from GitHub
3. Configure:

   | Field | Value |
   |---|---|
   | **Root Directory** | `client` |
   | **Framework Preset** | Vite |
   | **Build Command** | `npm run build` |
   | **Output Directory** | `dist` |

4. Under **Environment Variables**, add:

   | Key | Value |
   |---|---|
   | `VITE_API_URL` | Your Render URL from Step 1 (e.g. `https://autoval-api.onrender.com`) |

5. Click **Deploy** → builds in ~30 sec
6. You'll get a preview URL like `https://cap-stone-xyz.vercel.app` — test it works

---

## Step 3 — Connect carval.co.in to Vercel

### In Vercel:
1. Project → **Settings → Domains**
2. **Add Domain** → type `carval.co.in` → Add
3. Also add `www.carval.co.in`
4. Vercel shows DNS records — typically:

   | Type | Name | Value |
   |---|---|---|
   | `A` | `@` | `76.76.21.21` |
   | `CNAME` | `www` | `cname.vercel-dns.com` |

### In your Domain Registrar (GoDaddy / Namecheap / BigRock / etc.):
1. Log in → find **DNS Management** for `carval.co.in`
2. Add/replace with the records Vercel provided (remove any old A records)
3. DNS propagates in **5 min to 24 hours**

### Verify:
- `https://carval.co.in` → AutoVal AI loads
- Valuation form works, API calls reach Render

---

## Step 4 — Auto-deploys from now on

Both services watch your GitHub repo:
- **Push to `main`** → Vercel auto-rebuilds frontend (~30 sec)
- **Push to `main`** → Render auto-rebuilds backend (~2-3 min)

Your deploy workflow forever after:
```bash
git add -A
git commit -m "your message"
git push origin main
```

---

## Quick Checklist

- [ ] Render Web Service created — `/health` returns 200
- [ ] Render URL copied (e.g. `https://autoval-api.onrender.com`)
- [ ] Vercel project deployed with `VITE_API_URL` = Render URL
- [ ] Vercel: Domain `carval.co.in` added
- [ ] Registrar: DNS A + CNAME records updated
- [ ] `https://carval.co.in` loads and returns valuations
