cd ../
call venv\Scripts\activate
cd guiClient
pyinstaller --onefile  search-client.py -i "Icon/SIS_Icon.png"
copy Icon\SIS_ICON.png dist\
pause