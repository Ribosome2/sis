cd static/img/svn
svn update
cd ../../../
call venv\Scripts\activate
python offline.py
python server.py
