@echo off
cd /d "%~dp0"
echo Publishing Knowbase to GitHub (Netlify deploys from there)...
git add -A
git commit -m "Launch: all chapters free, remove paywall, hide unfinished books"
git push origin HEAD:main
echo.
echo Done. Check https://app.netlify.com for the deploy.
pause
