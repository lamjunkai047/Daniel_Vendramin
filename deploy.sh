#!/bin/bash
# Quick deployment script for Sales Forecasting App

echo "🚀 Sales Forecasting App - Deployment Script"
echo "=============================================="
echo ""

# Check if Docker is installed
if command -v docker &> /dev/null; then
    echo "✅ Docker found"
    
    # Build Docker image
    echo "📦 Building Docker image..."
    docker build -t sales-forecasting-app .
    
    if [ $? -eq 0 ]; then
        echo "✅ Docker image built successfully!"
        echo ""
        echo "To run locally:"
        echo "  docker run -p 8501:8501 sales-forecasting-app"
        echo ""
        echo "To test with docker-compose:"
        echo "  docker-compose up"
    else
        echo "❌ Docker build failed"
        exit 1
    fi
else
    echo "⚠️  Docker not found. Install Docker to use this script."
    echo ""
    echo "For Streamlit Cloud deployment:"
    echo "  1. Push code to GitHub"
    echo "  2. Go to share.streamlit.io"
    echo "  3. Deploy from repository"
    exit 0
fi

