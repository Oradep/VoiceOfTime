@echo off
:restart
echo Starting the website...
py app.py < NUL
echo The website crashed or was closed. Restarting...
timeout /t 3 >nul
goto restart
