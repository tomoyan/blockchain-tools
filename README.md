# blockchain-tools (steemit/hive)
https://floating-meadow-28045.herokuapp.com
hive/steemmit tools using beem (python library)

# Getting Started

## Python
Install beem with pip:
pip install -U beem

Create virtual environment<br>
python3 -m venv venv

ACTIVATE venv (Ubuntu command)<br>
source venv/bin/activate

DEACTIVATE venv (Ubuntu command)<br>
deactivate

## FLASK APP
Run flask app on development
<br>
export FLASK_APP=app.py
<br>
export FLASK_ENV=development
<br>
flask run

## Github
Create a new repository on the command line
echo "# blockchain-tools" >> README.md
<br>
git init
<br>
git add README.md
<br>
git commit -m "first commit"
<br>
git remote add origin https://github.com/tomoyan/blockchain-tools.git
<br>
git push -u origin master
<br>

## Heroku (Use windows command prompt)
<br>
Deploy Get Started:
https://devcenter.heroku.com/articles/getting-started-with-python
<br>
heroku login
<br>
heroku create

Create requirements file
pip freeze > requirements.txt
<br>
add gunicorn==20.0.4

touch Procfile and add
"web: gunicorn app:app"

Deploy to Heroku
git push heroku master

Ensure that at least one instance of the app is running:
heroku ps:scale web=1

Open the website: https://floating-meadow-28045.herokuapp.com/
<br>
heroku open
