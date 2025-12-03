@echo off
echo Starting local web server...
echo Server will run at: http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
python -m http.server 8000
