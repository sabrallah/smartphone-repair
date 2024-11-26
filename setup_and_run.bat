@echo off
echo Installing Python requirements...
pip install -r requirements.txt

echo.
echo Starting the Flask server...
python app.py
