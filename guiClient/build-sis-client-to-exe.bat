cd ../
call venv\Scripts\activate
cd guiClient
pyinstaller --onefile  search-client.py -i SIS_Icon.png
copy SIS_ICON.png dist\
pause