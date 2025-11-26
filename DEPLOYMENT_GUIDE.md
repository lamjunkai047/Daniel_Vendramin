# Deployment Guide - Sales Forecasting Application

This guide covers multiple deployment options for the Sales Forecasting application.

## 🚀 Option 1: Streamlit Cloud (RECOMMENDED - Easiest & Free)

Streamlit Cloud is the easiest way to deploy Streamlit apps for free.

### Prerequisites
- GitHub account
- Your code pushed to a GitHub repository

### Steps

1. **Push your code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account
   - Click "New app"
   - Select your repository
   - Set:
     - **Main file path:** `app.py`
     - **Python version:** 3.11 (recommended)
   - Click "Deploy"

3. **Your app will be live at:** `https://YOUR_APP_NAME.streamlit.app`

### Advantages
- ✅ Free
- ✅ Automatic deployments on git push
- ✅ No server management
- ✅ HTTPS included
- ✅ Easy to share

---

## 🐳 Option 2: Docker Deployment

Deploy using Docker on any cloud platform (AWS, Azure, GCP, DigitalOcean, etc.)

### Steps

1. **Build the Docker image**
   ```bash
   docker build -t sales-forecasting-app .
   ```

2. **Run locally to test**
   ```bash
   docker run -p 8501:8501 sales-forecasting-app
   ```

3. **Deploy to cloud**
   - Push to Docker Hub or container registry
   - Deploy on your preferred platform

### Docker Commands for Common Platforms

**AWS ECS/Fargate:**
```bash
aws ecr create-repository --repository-name sales-forecasting
docker tag sales-forecasting-app:latest YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com/sales-forecasting:latest
docker push YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com/sales-forecasting:latest
```

**Azure Container Instances:**
```bash
az container create \
  --resource-group myResourceGroup \
  --name sales-forecasting \
  --image sales-forecasting-app:latest \
  --dns-name-label sales-forecasting \
  --ports 8501
```

**Google Cloud Run:**
```bash
gcloud run deploy sales-forecasting \
  --image gcr.io/YOUR_PROJECT/sales-forecasting-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## ☁️ Option 3: Heroku

### Steps

1. **Install Heroku CLI** from [heroku.com](https://devcenter.heroku.com/articles/heroku-cli)

2. **Login and create app**
   ```bash
   heroku login
   heroku create your-app-name
   ```

3. **Deploy**
   ```bash
   git push heroku main
   ```

4. **Your app will be at:** `https://your-app-name.herokuapp.com`

**Note:** Heroku free tier was discontinued, but paid plans are available.

---

## 🌐 Option 4: AWS EC2 / Azure VM / GCP Compute Engine

Deploy on a virtual machine.

### Steps

1. **Launch a VM instance** (Ubuntu 22.04 recommended)
2. **SSH into the instance**
3. **Install dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3.11 python3-pip -y
   ```

4. **Clone and setup:**
   ```bash
   git clone YOUR_REPO_URL
   cd YOUR_REPO_NAME
   pip3 install -r requirements.txt
   ```

5. **Run with systemd service** (create `/etc/systemd/system/streamlit-app.service`):
   ```ini
   [Unit]
   Description=Streamlit Sales Forecasting App
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/YOUR_REPO_NAME
   ExecStart=/usr/bin/python3 -m streamlit run app.py --server.port=8501 --server.address=0.0.0.0
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

6. **Start the service:**
   ```bash
   sudo systemctl enable streamlit-app
   sudo systemctl start streamlit-app
   ```

7. **Configure firewall** to allow port 8501

8. **Set up reverse proxy** (nginx) for HTTPS

---

## 🔒 Security Considerations

### For Production Deployment:

1. **Add authentication** (Streamlit Cloud has built-in options)
2. **Use HTTPS** (Streamlit Cloud includes this)
3. **Set environment variables** for sensitive data
4. **Limit file upload size** in Streamlit config
5. **Add rate limiting** if needed

### Update `.streamlit/config.toml` for production:
```toml
[server]
maxUploadSize = 200  # MB
maxMessageSize = 200  # MB
enableCORS = false
enableXsrfProtection = true
```

---

## 📝 Environment Variables

If you need to set environment variables:

**Streamlit Cloud:**
- Go to app settings → Secrets
- Add key-value pairs

**Docker:**
```bash
docker run -p 8501:8501 -e ENV_VAR=value sales-forecasting-app
```

**Heroku:**
```bash
heroku config:set ENV_VAR=value
```

---

## 🧪 Testing Before Deployment

1. **Test locally:**
   ```bash
   streamlit run app.py
   ```

2. **Test with Docker:**
   ```bash
   docker build -t test-app .
   docker run -p 8501:8501 test-app
   ```

3. **Check all features work:**
   - File upload
   - Forecast generation
   - Manual forecast editing
   - Download functionality

---

## 📊 Recommended Deployment Options by Use Case

| Use Case | Recommended Option |
|----------|-------------------|
| Quick demo/prototype | Streamlit Cloud |
| Production with custom domain | Docker on AWS/Azure/GCP |
| Internal company tool | Docker on internal server |
| Free hosting needed | Streamlit Cloud |
| High traffic expected | AWS ECS / Azure Container Instances / GCP Cloud Run |

---

## 🆘 Troubleshooting

### Common Issues:

1. **Port already in use:**
   - Change port in config: `server.port = 8502`

2. **Memory issues:**
   - Increase memory limit in deployment platform
   - Optimize data processing

3. **Slow performance:**
   - Use caching: `@st.cache_data` for data loading
   - Optimize Prophet model parameters

4. **File upload errors:**
   - Check `maxUploadSize` in config
   - Verify file format

---

## 📞 Need Help?

- Streamlit Cloud docs: https://docs.streamlit.io/streamlit-community-cloud
- Docker docs: https://docs.docker.com
- Streamlit deployment: https://docs.streamlit.io/deploy

