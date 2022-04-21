## Python  
Create virtual environment:  
python3 -m venv venv  

ACTIVATE venv (Ubuntu command):  
source venv/bin/activate  

DEACTIVATE venv (Ubuntu command):  
deactivate  

Install all pakcages from requirements file:  
pip install -r requirements.txt  

Create/Update requirements file:  
pip freeze > requirements.txt  

## UPDATE config.py  
Blurt Username and Posting Key:  
UPVOTE_ACCOUNT = os.environ.get('UPVOTE_ACCOUNT') or 'YOUR_USERNAME'  
UPVOTE_KEY = os.environ.get('UPVOTE_KEY') or 'YOUR_PRIVATE_POSTING_KEY'  

Firebase(realtime database) API key (firebase.google.com):  
FB_APIKEY = os.environ.get('FB_APIKEY') or 'YOUR_FB_APIKEY'  
https://github.com/nhorvath/Pyrebase4  

## FLASK APP  
Add flask environment variablea in .flaskenv file:  
touch .flaskenv  

FLASK_APP=app.py  
FLASK_ENV=development  
SECRET_KEY=YOUR_SECRET_KEY  

Run flask app:  
flask run  

## Deploying with Git
* Clone
git clone https://github.com/tomoyan/blockchain-tools.git

* Make changes to codes and commit.
git add .
git commit -m "commit everything"

* Check remote -v
git remote -v
heroku  https://git.heroku.com/floating-meadow-28045.git (fetch)
heroku  https://git.heroku.com/floating-meadow-28045.git (push)
origin  https://github.com/tomoyan/blockchain-tools.git (fetch)
origin  https://github.com/tomoyan/blockchain-tools.git (push)

* Add a remote to local repository
heroku git:remote -a floating-meadow-28045

* Rename a Remote (optional)
git remote rename heroku heroku-staging

* Deploy to heroku
git push heroku master

* Push code changes to git
git push
