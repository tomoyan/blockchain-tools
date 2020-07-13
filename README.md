# blockchain-tools

# Getting Started

## Python
Create virtual environment
python3 -m venv venv

ACTIVATE venv (Ubuntu command)
source venv/bin/activate

DEACTIVATE venv (Ubuntu command)
deactivate

## FLASK APP
Run flask app on development
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

Open the website:
heroku open
