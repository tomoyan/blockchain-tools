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
* export FLASK_APP=app.py
* export FLASK_ENV=development
* flask run

## Github
Create a new repository on the command line
* echo "# blockchain-tools" >> README.md
* git init
* git add README.md
* git commit -m "first commit"
* git remote add origin https://github.com/tomoyan/blockchain-tools.git
* git push -u origin master

## Heroku
Deploy: https://devcenter.heroku.com/articles/getting-started-with-python
(command prompt)
heroku login
heroku create

pip freeze > requirements.txt

touch Procfile and add this
"web: gunicorn app:app"

Deploy to Heroku
git push heroku master

Ensure that at least one instance of the app is running:
heroku ps:scale web=1

Open the website:
heroku open
