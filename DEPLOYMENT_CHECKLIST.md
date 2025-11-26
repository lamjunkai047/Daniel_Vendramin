# Deployment Checklist

Use this checklist before deploying to production.

## Pre-Deployment

- [ ] Test all features locally
- [ ] Verify file upload works
- [ ] Test forecast generation
- [ ] Test manual forecast editing
- [ ] Test download functionality
- [ ] Check error handling
- [ ] Review security settings

## Code Preparation

- [ ] Remove any hardcoded credentials
- [ ] Update `.streamlit/config.toml` for production
- [ ] Ensure `requirements.txt` is up to date
- [ ] Remove sample data files (if not needed)
- [ ] Add proper error messages

## Deployment Platform Setup

### Streamlit Cloud
- [ ] Push code to GitHub
- [ ] Create Streamlit Cloud account
- [ ] Connect GitHub repository
- [ ] Set main file path: `app.py`
- [ ] Configure Python version (3.11 recommended)
- [ ] Test deployment

### Docker
- [ ] Build Docker image successfully
- [ ] Test Docker image locally
- [ ] Push to container registry
- [ ] Configure cloud platform
- [ ] Set up environment variables
- [ ] Configure networking/ports
- [ ] Set up health checks

### Heroku
- [ ] Install Heroku CLI
- [ ] Login to Heroku
- [ ] Create Heroku app
- [ ] Push code
- [ ] Configure environment variables
- [ ] Test deployment

## Post-Deployment

- [ ] Verify app is accessible
- [ ] Test all features in production
- [ ] Check performance
- [ ] Monitor error logs
- [ ] Set up monitoring/alerts (optional)
- [ ] Document access URL
- [ ] Share with users

## Security Checklist

- [ ] HTTPS enabled (Streamlit Cloud includes this)
- [ ] Authentication configured (if needed)
- [ ] File upload size limits set
- [ ] No sensitive data in code
- [ ] Environment variables for secrets
- [ ] CORS properly configured

## Performance

- [ ] Test with realistic data sizes
- [ ] Verify memory usage is acceptable
- [ ] Check forecast generation time
- [ ] Optimize if needed

## Documentation

- [ ] Update README with deployment info
- [ ] Document access URL
- [ ] Create user guide
- [ ] Document any special configuration

---

## Quick Test Commands

```bash
# Test locally
streamlit run app.py

# Test Docker build
docker build -t test-app .
docker run -p 8501:8501 test-app

# Test docker-compose
docker-compose up
```

---

## Common Issues

- **Port conflicts:** Change port in config
- **Memory errors:** Increase memory limit
- **Slow performance:** Optimize data processing
- **Import errors:** Check requirements.txt

---

✅ Ready to deploy when all items are checked!

