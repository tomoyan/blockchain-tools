from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def home():
    # return 'Hello, World!'
    return render_template('index.html')


@app.route('/follower')
def follower():
    # return 'Hello, World!'
    return render_template('follower.html')


@app.route('/following')
def following():
    # return 'Hello, World!'
    return render_template('following.html')
