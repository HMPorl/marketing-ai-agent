# Streamlit Cloud Deployment Guide

## Prerequisites
1. GitHub account
2. Streamlit Cloud account (free at share.streamlit.io)

## Step-by-Step Deployment

### 1. Create GitHub Repository
```bash
# Initialize git repository
git init

# Add all files
git add .

# Commit files
git commit -m "Initial commit - Marketing AI Agent"

# Add GitHub remote (replace with your repository URL)
git remote add origin https://github.com/yourusername/marketing-ai-agent.git

# Push to GitHub
git push -u origin main
```

### 2. Deploy to Streamlit Cloud

1. **Go to [share.streamlit.io](https://share.streamlit.io)**
2. **Sign in with GitHub**
3. **Click "New app"**
4. **Configure deployment:**
   - Repository: `yourusername/marketing-ai-agent`
   - Branch: `main`
   - Main file path: `streamlit_app.py`
   - App URL: Choose your preferred URL

### 3. Environment Variables (Optional)

If you want to add API keys, go to your app settings and add:
- `WEATHER_API_KEY` - Your OpenWeatherMap API key
- `OPENAI_API_KEY` - Your OpenAI API key (optional)

### 4. Update Configuration

The app will automatically use the `requirements.txt` file for dependencies.

## Quick Commands for GitHub

```bash
# Navigate to your project directory
cd "c:\Users\paul.scott\OneDrive - The Hireman\Shared Documents - IT Support\Scripts and code\Python\marketing_agent"

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit with message
git commit -m "Marketing AI Agent - Ready for deployment"

# Add your GitHub repository
git remote add origin https://github.com/YOURUSERNAME/YOURREPO.git

# Push to GitHub
git push -u origin main
```

## Post-Deployment Steps

1. **Test the live app** to ensure everything works
2. **Add your weather API key** in Streamlit Cloud settings
3. **Upload your business data** through the Settings page
4. **Share the URL** with your team

## Features Available in Cloud Version

✅ **Full functionality** - All features work in the cloud
✅ **No local dependencies** - Runs entirely in Streamlit Cloud
✅ **Automatic updates** - Push to GitHub to update the live app
✅ **Shareable URL** - Access from anywhere
✅ **Free hosting** - No cost for hosting on Streamlit Cloud

## Updating Your Live App

Whenever you want to update the live app:

```bash
# Make your changes locally
# Test them with: streamlit run streamlit_app.py

# Commit and push changes
git add .
git commit -m "Update: describe your changes"
git push
```

The live app will automatically update within a few minutes!

## Troubleshooting

### Common Issues:
1. **Dependencies not found**: Check `requirements.txt` format
2. **App won't start**: Check for syntax errors in `streamlit_app.py`
3. **Missing data**: Ensure all required folders exist in the repository

### Getting Help:
- Streamlit Cloud logs show detailed error information
- Test locally first: `streamlit run streamlit_app.py`
- Check GitHub repository has all necessary files

---

**Your app will be live at:** `https://YOURAPPNAME.streamlit.app`