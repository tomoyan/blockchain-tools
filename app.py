from beem import Hive
from beem.nodelist import NodeList
from beem.account import Account

from flask import Flask, render_template, redirect, request, flash
from config import Config
from forms import UserNameForm
from markupsafe import escape

import logging

app = Flask(__name__)
app.config.from_object(Config)


# This handles 404 error
@app.errorhandler(404)
def not_found(e):
    return redirect('/')
    # Need to make 404 page
    # return render_template('index.html')


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/follower', methods=['GET', 'POST'])
def follower():
    form = UserNameForm(request.form)

    if request.method == 'POST':
        if form.validate():
            username = request.form['username'].lower()
            logging.warning(username)

            return redirect('/follower/' + username)
        else:
            flash('Error: Username is Required')

    return render_template('follower.html', form=form)


@app.route('/follower/<username>')
@app.route('/follower/<username>/')
def follower_list(username=None):
    data = []
    if username:
        username = escape(username).lower()
        data = get_friends_data(username, 'followers')
    logging.warning(data)

    return render_template('follower_list.html', username=username, data=data)


@app.route('/following', methods=['GET', 'POST'])
def following():
    form = UserNameForm(request.form)

    if request.method == 'POST':
        if form.validate():
            username = request.form['username'].lower()
            logging.warning(username)

            return redirect('/following/' + username)
        else:
            flash('Error: Username is Required')

    return render_template('following.html', form=form)


@app.route('/following/<username>')
@app.route('/following/<username>/')
def following_list(username=None):
    # flash('USERNAME: ' + username)
    data = []
    if username:
        username = escape(username).lower()
        data = get_friends_data(username, 'following')
    logging.warning(data)

    return render_template('following_list.html', username=username, data=data)


def get_friends_data(username, follow_type):
    # Setup node list
    nodelist = NodeList()
    nodelist.update_nodes()
    nodes = nodelist.get_hive_nodes()
    hive = Hive(node=nodes)
    hive.set_default_nodes(nodes)

    # Create account object
    try:
        account = Account(username)
        logging.warning(account)
    except Exception as e:
        logging.warning(e)
        return {}

    followers = account.get_followers()
    following = account.get_following()

    if follow_type == 'followers':
        return make_dict(followers, following)
    else:
        return make_dict(following, followers)


def make_dict(data_list, find_list):
    my_dict = {}

    for data in data_list:
        if data in find_list:
            my_dict[data] = 1
        else:
            my_dict[data] = 0
    return my_dict
