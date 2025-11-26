# 🚀 Quick Deployment Guide

## Fastest Way: Streamlit Cloud (5 minutes)

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Sales Forecasting App"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2: Deploy
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set **Main file path:** `app.py`
6. Click "Deploy"

**Done!** Your app is live at `https://YOUR_APP.streamlit.app`

---

## Alternative: Docker (For AWS/Azure/GCP)

### Build and Test Locally
```bash
docker build -t sales-forecast .
docker run -p 8501:8501 sales-forecast
```

### Deploy to Cloud
- **AWS:** Use ECS/Fargate or EC2
- **Azure:** Use Container Instances or App Service
- **GCP:** Use Cloud Run (easiest)

See `DEPLOYMENT_GUIDE.md` for detailed instructions.

---

## What's Included

✅ Dockerfile - For containerized deployment  
✅ docker-compose.yml - For local testing  
✅ Procfile - For Heroku  
✅ .streamlit/config.toml - Production config  
✅ All deployment guides

---

## Need Help?

See `DEPLOYMENT_GUIDE.md` for complete instructions.

