from flask import Flask, render_template, redirect, request, flash, jsonify
from flask import session
from flask_session import Session
from celery import Celery
# from celery.utils.log import get_task_logger
from config import Config
from forms import UserNameForm
from forms import postUrlForm
from markupsafe import escape
import BlurtChain as BC


app = Flask(__name__)
app.config.from_object(Config)
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
Session(app)
# logger = get_task_logger(__name__)


@app.errorhandler(404)
# This handles 404 error
def page_not_found(e):
    return render_template('404.html')


@app.route('/', methods=['GET', 'POST'])
def blurt():
    form = UserNameForm(request.form)

    if request.method == 'POST':
        if form.validate():
            username = request.form['username'].lower()

            return redirect(f'/{username}')
        else:
            flash('Username is Required')

    return render_template('blurt/profile.html', form=form)


@celery.task
def reward_summary_task(username):
    blurt = BC.BlurtChain(username)
    duration = 30

    key_name = username + '_reward_' + str(duration)
    data = blurt.get_reward_summary(duration)
    # data['reward_data'] = reward_data

    # save reward_data in firbase
    blurt.set_data_fb("reward_summary", key_name, data)

    return data


@app.route('/<username>')
@app.route('/<username>/')
def blurt_profile_data(username=None):
    data = {}

    if username:
        username = escape(username).lower()
        blurt = BC.BlurtChain(username)

        # celery background task
        data = reward_summary_task.delay(username)
        print("REWARD_SUMMARY_TASK_DELAY ", data)
        print(vars(data))

        # check session profile_data
        profile_data = username + '_profile_data'
        if session.get(profile_data):
            data = session[profile_data]
        else:
            data = blurt.get_account_info()
            vote_data = blurt.get_vote_history(username)

            data['labels'] = vote_data['labels']
            data['permlinks'] = vote_data['permlinks']
            data['upvotes'] = vote_data['upvotes']
            data['count_data'] = vote_data['count_data']
            data['weight_data'] = vote_data['weight_data']
            data['total_votes'] = vote_data['total_votes']

            session[profile_data] = data

    return render_template('blurt/profile_data.html',
                           username=blurt.username, data=data)


@app.route('/blurt/stats')
@app.route('/blurt/stats/')
def stats():
    blurt = BC.BlurtChain(username=None)
    stats_data = blurt.get_stats()

    return render_template('blurt/stats.html', data=stats_data)


@app.route('/blurt/upvote', methods=['GET', 'POST'])
@app.route('/blurt/upvote/', methods=['GET', 'POST'])
def upvote():
    form = postUrlForm(request.form)

    if request.method == 'POST':
        if form.validate():
            url = request.form['url'].lower()
            blurt = BC.BlurtChain(username=None)
            result = blurt.process_upvote(url)
            flash(result['message'])
        else:
            # check empty url
            flash('Error: URL is required')

    return render_template('blurt/upvote.html', form=form)


# BLURT API
@app.route('/api/blurt/follower/<username>')
@app.route('/api/blurt/follower/<username>/')
def blurt_follower(username=None):
    data = {}
    if username:
        blurt = BC.BlurtChain(username)
        data = blurt.get_follower()

    return jsonify(data)


@app.route('/api/blurt/following/<username>')
@app.route('/api/blurt/following/<username>/')
def blurt_following(username=None):
    data = {}
    if username:
        blurt = BC.BlurtChain(username)
        data = blurt.get_following()

    return jsonify(data)


@app.route('/api/blurt/votes/<username>')
@app.route('/api/blurt/votes/<username>/')
def blurt_votes(username=None):
    data = {}
    if username:
        blurt = BC.BlurtChain(username)
        data = blurt.get_vote_history()

    return jsonify(data)


@app.route('/api/blurt/mute/<username>')
@app.route('/api/blurt/mute/<username>/')
def blurt_mute(username=None):
    data = {}
    if username:
        blurt = BC.BlurtChain(username)
        data = blurt.get_mute()

    return jsonify(data)


@app.route('/api/blurt/delegation/<username>/<option>')
@app.route('/api/blurt/delegation/<username>/<option>/')
def blurt_delegation(username=None, option=None):
    delegation_type = ["in", "out", "exp"]
    data = {}
    if username and option in delegation_type:
        # check session delegation_data
        delegation_data = username + '_delegation_' + option
        if session.get(delegation_data):
            data = session[delegation_data]
        else:
            blurt = BC.BlurtChain(username)
            data = blurt.get_delegation_new(option)
            session[delegation_data] = data

    return jsonify(data)


@app.route('/api/blurt/reward/<username>/<int:duration>')
@app.route('/api/blurt/reward/<username>/<int:duration>/')
@app.route('/api/blurt/reward/<username>/<int:duration>/<option>')
@app.route('/api/blurt/reward/<username>/<int:duration>/<option>/')
def blurt_reward(username=None, duration=1, option=None):
    data = {}
    if username:
        blurt = BC.BlurtChain(username)

        reward_data = username + '_reward_' + str(duration)
        print(reward_data)

        if duration == 30:
            key_data = blurt.get_key_data_fb("reward_summary", reward_data)
            data = key_data.val()
            print("key_data ", data)
            if data:
                session[reward_data] = data
                blurt.remove_key_data_fb("reward_summary", reward_data)

        # check session reward_data
        if session.get(reward_data):
            data = session[reward_data]
            print("SESSION_REWARD_DATA", duration, data)
        else:
            data = blurt.get_reward_summary(duration, option=option)
            session[reward_data] = data
            print("GET_REWARD_SUMMARY", duration, data)

    return jsonify(data)


@app.route('/api/blurt/author_reward/<username>/<int:duration>')
@app.route('/api/blurt/author_reward/<username>/<int:duration>/')
def blurt_author(username=None, duration=1):
    data = None
    if username:
        blurt = BC.BlurtChain(username)

        # check session reward_data
        reward_data = username + '_author_reward_' + str(duration)
        if session.get(reward_data):
            data = session[reward_data]
        else:
            data = blurt.get_author_reward(duration)
            if data != "0.0":
                session[reward_data] = data

    return jsonify(data)


@app.route('/api/blurt/curation_reward/<username>/<int:duration>')
@app.route('/api/blurt/curation_reward/<username>/<int:duration>/')
def blurt_curation(username=None, duration=1):
    data = None
    if username:
        blurt = BC.BlurtChain(username)

        # check session reward_data
        reward_data = username + '_curation_reward_' + str(duration)
        if session.get(reward_data):
            data = session[reward_data]
        else:
            data = blurt.get_curation_reward(duration)
            if data != "0.0":
                session[reward_data] = data

    return jsonify(data)


@app.route('/api/blurt/producer_reward/<username>/<int:duration>')
@app.route('/api/blurt/producer_reward/<username>/<int:duration>/')
def blurt_producer(username=None, duration=1):
    data = None
    if username:
        blurt = BC.BlurtChain(username)

        # check session reward_data
        reward_data = username + '_producer_reward_' + str(duration)
        if session.get(reward_data):
            data = session[reward_data]
        else:
            data = blurt.get_producer_reward(duration)
            if data != "0.0":
                session[reward_data] = data

    return jsonify(data)


if __name__ == "__main__":
    app.run()
