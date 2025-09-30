@echo off
echo Marketing AI Agent - GitHub Deployment Script
echo.

echo Step 1: Checking git status...
git status

echo.
echo Step 2: Adding any new changes...
git add .

echo.
echo Step 3: Committing changes...
set /p commit_message="Enter commit message (or press Enter for default): "
if "%commit_message%"=="" set commit_message=Update Marketing AI Agent

git commit -m "%commit_message%"

echo.
echo Step 4: Ready to push to GitHub!
echo.
echo To complete deployment:
echo 1. Create a new repository on GitHub
echo 2. Copy the repository URL
echo 3. Run: git remote add origin [YOUR_REPO_URL]
echo 4. Run: git push -u origin master
echo.
echo Then deploy to Streamlit Cloud:
echo 1. Go to https://share.streamlit.io
echo 2. Sign in with GitHub
echo 3. Click "New app" 
echo 4. Select your repository
echo 5. Set main file to: streamlit_app.py
echo.

pause