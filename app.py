from beem.account import Account
from beem.amount import Amount
from beem.instance import set_shared_blockchain_instance

from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, request, flash, jsonify
from config import Config
from forms import UserNameForm
from markupsafe import escape

import SteemChain
import HiveChain
import BlurtChain as BC

import logging

app = Flask(__name__)
app.config.from_object(Config)


# This handles 404 error
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/harvest')
@app.route('/harvest/')
def harvest():
    return render_template('/harvest/harvest.html')


@app.route('/harvest/simple')
@app.route('/harvest/simple/')
def harvest_simple():
    return render_template('/harvest/simple.html')


@app.route('/harvest/dark')
@app.route('/harvest/dark/')
def harvest_dark():
    return render_template('/harvest/dark.html')


@app.route('/blurt', methods=['GET', 'POST'])
@app.route('/blurt/', methods=['GET', 'POST'])
def blurt():
    form = UserNameForm(request.form)

    if request.method == 'POST':
        if form.validate():
            username = request.form['username'].lower()

            return redirect(f'/blurt/{username}')
        else:
            flash('Username is Required')

    return render_template('blurt/profile.html', form=form)


@app.route('/blurt/<username>')
@app.route('/blurt/<username>/')
def blurt_profile_data(username=None):
    # print(f'BLURT_PROFILE_DATA USERNAME: {username}')
    data = {}
    if username:
        username = escape(username).lower()
        blurt = BC.BlurtChain(username)
        # print(dir(blurt))
        # print(vars(blurt))
        # print(blurt.username)

        data = blurt.get_account_info()
        vote_data = blurt.get_vote_history()
        data['labels'] = vote_data['labels']
        data['permlinks'] = vote_data['permlinks']
        data['count_data'] = vote_data['count_data']
        data['weight_data'] = vote_data['weight_data']
        data['total_votes'] = vote_data['total_votes']
        # print(f'GET_ACCOUNT_INFO: {data}')
    return render_template('blurt/profile_data.html',
                           username=blurt.username, data=data)


# BLURT API
@app.route('/api/blurt/follower/<username>')
@app.route('/api/blurt/follower/<username>/')
def blurt_follower(username=None):
    # print('BLURT_FOLLOWER_DEF')
    data = {}
    if username:
        blurt = BC.BlurtChain(username)
        data = blurt.get_follower()
        # print('BLURT_FOLLOWER', vars(blurt))
    return jsonify(data)


@app.route('/api/blurt/following/<username>')
@app.route('/api/blurt/following/<username>/')
def blurt_following(username=None):
    # print('BLURT_FOLLOWING_DEF')
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


@app.route('/api/blurt/delegation/<username>')
@app.route('/api/blurt/delegation/<username>/')
def blurt_delegation(username=None):
    data = {}
    if username:
        blurt = BC.BlurtChain(username)
        data = blurt.get_delegation()

    return jsonify(data)


@app.route('/api/blurt/reward/<username>')
@app.route('/api/blurt/reward/<username>/')
def blurt_reward(username=None):
    data = {}
    if username:
        blurt = BC.BlurtChain(username)
        data = blurt.get_reward_summary()

    return jsonify(data)


@app.route('/swap')
@app.route('/swap/')
def swap():
    return render_template('swap.html')


@app.route('/hive/follower', methods=['GET', 'POST'])
def hive_follower():
    form = UserNameForm(request.form)

    if request.method == 'POST':
        if form.validate():
            username = request.form['username'].lower()

            return redirect('/hive/follower/' + username)
        else:
            flash('Username is Required')

    return render_template('hive/follower.html', form=form)


@app.route('/hive/follower/<username>')
@app.route('/hive/follower/<username>/')
def hive_follower_list(username=None):
    data = []
    if username:
        username = escape(username).lower()
        data = get_hive_friends(username, 'follower')
    logging.warning(data)

    return render_template('hive/follower_list.html',
                           username=username, data=data)


@app.route('/hive/following', methods=['GET', 'POST'])
def hive_following():
    form = UserNameForm(request.form)

    if request.method == 'POST':
        if form.validate():
            username = request.form['username'].lower()

            return redirect('/hive/following/' + username)
        else:
            flash('Username is Required')

    return render_template('hive/following.html', form=form)


@app.route('/hive/following/<username>')
@app.route('/hive/following/<username>/')
def hive_following_list(username=None):
    data = []
    if username:
        username = escape(username).lower()
        data = get_hive_friends(username, 'following')
    logging.warning(data)

    return render_template('hive/following_list.html',
                           username=username, data=data)


@app.route('/hive/profile', methods=['GET', 'POST'])
def hive_profile():
    form = UserNameForm(request.form)

    if request.method == 'POST':
        if form.validate():
            username = request.form['username'].lower()

            return redirect('/hive/profile/' + username)
        else:
            flash('Username is Required')

    return render_template('hive/profile.html', form=form)


@app.route('/hive/profile/<username>')
@app.route('/hive/profile/<username>/')
def hive_profile_data(username=None):
    data = {}
    if username:
        username = escape(username).lower()
        data = get_user_profile('hive', username)

    logging.warning('get_user_profile')
    logging.warning(data)
    if data:
        return render_template('hive/profile_data.html',
                               username=username, data=data)
    else:
        return render_template('hive/profile_data.html',
                               username=None, data=data)


@app.route('/steemit/profile', methods=['GET', 'POST'])
def steemit_profile():
    form = UserNameForm(request.form)

    if request.method == 'POST':
        if form.validate():
            username = request.form['username'].lower()

            return redirect('/steemit/profile/' + username)
        else:
            flash('Username is Required')

    return render_template('steemit/profile.html', form=form)


@app.route('/steemit/profile/<username>')
@app.route('/steemit/profile/<username>/')
def steemit_profile_data(username=None):
    data = {}
    if username:
        username = escape(username).lower()
        data = get_user_profile('steemit', username)

    logging.warning('get_user_profile')
    logging.warning(data)
    if data:
        return render_template('steemit/profile_data.html',
                               username=username, data=data)
    else:
        return render_template('steemit/profile_data.html',
                               username=None, data=data)


@app.route('/steemit/follower', methods=['GET', 'POST'])
def steemit_follower():
    form = UserNameForm(request.form)

    if request.method == 'POST':
        if form.validate():
            username = request.form['username'].lower()

            return redirect('/steemit/follower/' + username)
        else:
            flash('Username is Required')

    return render_template('steemit/follower.html', form=form)


@app.route('/steemit/follower/<username>')
@app.route('/steemit/follower/<username>/')
def steemit_follower_list(username=None):
    data = []
    if username:
        username = escape(username).lower()
        data = get_steemit_friends(username, 'follower')
    logging.warning(data)

    return render_template('steemit/follower_list.html',
                           username=username, data=data)


@app.route('/steemit/following', methods=['GET', 'POST'])
def steemit_following():
    form = UserNameForm(request.form)

    if request.method == 'POST':
        if form.validate():
            username = request.form['username'].lower()

            return redirect('/steemit/following/' + username)
        else:
            flash('Username is Required')

    return render_template('steemit/following.html', form=form)


@app.route('/steemit/following/<username>')
@app.route('/steemit/following/<username>/')
def steemit_following_list(username=None):
    data = []
    if username:
        username = escape(username).lower()
        data = get_steemit_friends(username, 'following')
    logging.warning(data)

    return render_template('steemit/following_list.html',
                           username=username, data=data)


def get_user_profile(chain_type, username):
    chain = None
    if chain_type == 'hive':
        chain = set_node_list(chain_type='hive')
        chain.is_hive
    elif chain_type == 'steemit':
        chain = set_node_list(chain_type='steemit')
    else:
        return None

    # Create account object
    try:
        account = Account(username)
    except Exception as e:
        logging.warning(e)
        return None

    profile = account.profile

    profile['balances'] = account.get_balances()
    profile['voting_power'] = f"{account.vp: .2f}"
    profile['reputation'] = f"{account.get_reputation(): .1f}"

    token_power = account.get_token_power()
    profile['token_power'] = f"{token_power:.3f}"

    profile['curation_reward_30'] = account.get_curation_reward(days=30)
    profile['curation_reward_30'] = f"{profile['curation_reward_30']:.3f}"

    profile['author_reward_30'] = get_author_reward(chain, account)

    # Get delegations
    delegations = account.get_vesting_delegations()
    if delegations:
        profile['delegations'] = get_user_delegations(
            chain, username, delegations)
    else:
        profile['delegations'] = []

    return profile


def get_author_reward(chain, account, days=30):
    stop = datetime.utcnow() - timedelta(days=days)
    reward_vests = Amount('0 VESTS')

    rewards = 0.000
    for reward in account.history_reverse(
            stop=stop, only_ops=['author_reward']):
        reward_vests += Amount(reward['vesting_payout'])
        if chain.is_steem:
            rewards = chain.vests_to_sp(reward_vests.amount)
        elif chain.is_hive:
            rewards = chain.vests_to_hp(reward_vests.amount)
    return f"{rewards:.3f}"


def get_user_delegations(chain, username, delegations):
    # Convert vest to power
    delegation_list = []
    for d in delegations:
        amount = d['vesting_shares']['amount']
        precision = d['vesting_shares']['precision']
        precision = 10 ** precision
        delegatee = d['delegatee']
        vest_amount = float(int(amount) / precision)
        if chain.is_hive:
            delegation_power = f"{chain.vests_to_hp(vest_amount):.3f}"
        elif chain.is_steem:
            delegation_power = f"{chain.vests_to_sp(vest_amount):.3f}"

        delegation_list.append(
            {'delegatee': delegatee, 'amount': delegation_power})

    return delegation_list


def get_friends(username, follow_type):
    # Create account object
    try:
        account = Account(username)
        logging.warning(account)
    except Exception as e:
        logging.warning(e)
        return {}

    followers = account.get_followers()
    following = account.get_following()

    if follow_type == 'follower':
        return make_dict(followers, following)
    elif follow_type == 'following':
        return make_dict(following, followers)
    else:
        return {}


def get_hive_friends(username, follow_type):
    set_node_list(chain_type='hive')

    return get_friends(username, follow_type)


def get_steemit_friends(username, follow_type):
    set_node_list(chain_type='steemit')

    return get_friends(username, follow_type)


def set_node_list(chain_type=None):
    # Setup node list for hive/steemit
    # depending on the chain_type

    chain = None
    if chain_type == 'steemit':
        sc = SteemChain.SteemChain()
        chain = sc.chain
    elif chain_type == 'hive':
        hc = HiveChain.HiveChain()
        chain = hc.chain

    set_shared_blockchain_instance(chain)
    return chain


def make_dict(data_list, find_list):
    # Create a dictionary from follower, following lists
    # Add a flag for who follows and following
    my_dict = {}

    for data in data_list:
        if data in find_list:
            my_dict[data] = 1
        else:
            my_dict[data] = 0
    return my_dict


if __name__ == "__main__":
    # app.run()
    app.run(debug=True)
