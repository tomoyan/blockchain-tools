# blockchain-tools

# Create virtual environment
python3 -m venv venv

# Ubuntu Activate venv
source venv/bin/activate

# Ubuntu Deactivate venv
deactivate

# create a new repository on the command line
* echo "# blockchain-tools" >> README.md
* git init
* git add README.md
* git commit -m "first commit"
* git remote add origin https://github.com/tomoyan/blockchain-tools.git
* git push -u origin master

# RUN FLASK APP
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
