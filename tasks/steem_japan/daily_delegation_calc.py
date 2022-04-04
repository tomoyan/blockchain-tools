import collections
from datetime import datetime
import requests
import pyrebase
import base64
import json
import os
import time
import random

from beem import Steem
from beem.account import Account
from beem.nodelist import NodeList
from beem.instance import set_shared_blockchain_instance
from beem.community import Community

# Setup Steem nodes
nodelist = NodeList()
nodelist.update_nodes()
# nodes = nodelist.get_steem_nodes()
nodes = [
    'https://api.steemitdev.com',
    'https://steem.justyy.workers.dev',
    'https://api.steem.fans',
    'https://api.steemit.com',
    'https://cn.steems.top',
    'https://api.steem.buzz',
    'https://steem.61bts.com']
random.shuffle(nodes)
COMMUNITY_ACTIVE_KEY = os.environ.get('COMMUNITY_ACTIVE_KEY')
COMMUNITY_NAME = os.environ.get('COMMUNITY_NAME')
STEEM = Steem(node=nodes, keys=[COMMUNITY_ACTIVE_KEY])
set_shared_blockchain_instance(STEEM)

# Firebase configuration
serviceAccountCredentials = json.loads(
    base64.b64decode(os.environ.get('FB_SERVICEACCOUNT').encode()).decode())

firebase_config_prd = {
    "apiKey": os.environ.get('FB_APIKEY'),
    "authDomain": os.environ.get('FB_AUTHDOMAIN'),
    "databaseURL": os.environ.get('FB_DATABASEURL'),
    "storageBucket": os.environ.get('FB_STORAGEBUCKET'),
    "serviceAccount": serviceAccountCredentials,
}
firebase = pyrebase.initialize_app(firebase_config_prd)

# Get a reference to the database service
db_prd = firebase.database()
db_name = 'sp_delegation_payouts'


def main():
    # Run python tasks/steem_japan/delegator_payout.py
    # Calculate delegation payout daily.
    # Result is saved in Firebase
    delegator_payout_calc()

    # Payout gets executed once a month
    # 1st day of the month
    process_delegation_payout()

    # clean up sp_delegation_payouts data
    payout_data_cleanup()


def delegator_payout_calc():
    today = datetime.now().strftime("%Y-%m-%d")

    account = Account(COMMUNITY_NAME, blockchain_instance=STEEM)
    sp_total = 0.0
    payout_data = []

    # Get curation reward for the last 24 hours
    curation_reward = account.get_curation_reward(days=1)

    # 50% of the curation reward will be divided and distributed
    # to SP delegators
    budget = curation_reward / 2

    # Get a list of SP delegators from justyy
    url = (
        'https://uploadbeta.com/api/steemit/delegators/?'
        'cached&'
        'id=japansteemit&'
        'hash=tomoyajapnesekasjdfahjjkhh23k3k4'
    )
    response = requests.get(url)

    if response:
        json_data = response.json()

        counter = collections.Counter()
        for d in json_data:
            counter.update(d)

        result = dict(counter)
        sp_total = result['sp']

        # Each delegator will get their share based on the delegated SP
        for data in json_data:
            # skip dot users
            # if "." in data['delegator']:
            #     continue

            percentage = data['sp'] / sp_total
            reward = budget * percentage
            # payout_data[data['delegator']] = reward
            payout_data.append({
                'username': data['delegator'],
                'reward': reward,
            })
    else:
        print('JUSTYY REQUEST ERROR:', response.status_code)

    print('PAYOUT_DATA', db_name, today, payout_data)
    db_prd.child(db_name).child(today).set(payout_data)

    return payout_data


def get_muted_members():
    muted = []
    steem_japan = 'hive-161179'
    community = Community(steem_japan, blockchain_instance=STEEM)

    # Get a list of community roles
    roles = community.get_community_roles()

    # Find muted members
    for role in roles:
        if role[1] == 'muted':
            muted.append(role[0])

    return muted


def get_payout_data(payout_month=None):
    payout_data = {}
    muted = get_muted_members()

    # If payout_month is not specified,
    # it is set to current month
    if payout_month is None:
        now = datetime.now()
        payout_month = now.month

    payouts = db_prd.child(db_name).get()

    for payout in payouts.each():
        # key() is a date string 2021-09-01
        date = payout.key()

        # Check month of date string
        date_month = time.strptime(date, "%Y-%m-%d").tm_mon
        if date_month != payout_month:
            continue

        # Sum up all the rewards for each delegator
        # data (dict) {'abby0207': 0.01252727737602502}
        # data (list) [{'reward': 0.01911765616314007, 'username': 'ikhwal23'}]
        data = payout.val()
        if isinstance(data, dict):
            for name in data:
                # Skip muted members
                if name in muted:
                    continue

                if name in payout_data:
                    payout_data[name] += data[name]
                else:
                    payout_data[name] = data[name]
        elif isinstance(data, list):
            for row in data:
                # Skip muted members
                if row['username'] in muted:
                    continue

                if row['username'] in payout_data:
                    payout_data[row['username']] += row['reward']
                else:
                    payout_data[row['username']] = row['reward']

    return payout_data


def process_delegation_payout():
    payout_day = 1
    minimum = 0.001
    now = datetime.now()

    # delegation payout is 1st day of the month
    if now.day != payout_day:
        return

    # get last months payout data
    payout_month = now.month - 1
    payout_data = get_payout_data(payout_month)
    memo = f'Steem Japan SP Delegation Payout Month: {payout_month}'

    for p in payout_data:
        amount = float(f'{payout_data[p]: .3f}')

        # Skip small transactions
        if amount < minimum:
            continue

        try:
            ACCOUNT = Account(COMMUNITY_NAME, blockchain_instance=STEEM)
            ACCOUNT.transfer(p, amount, 'STEEM', memo)
        except Exception as err:
            print(err)


def payout_data_cleanup():
    # Clean up data that is more than 2 months old
    TTL = 60
    today = datetime.now()

    # Get data from sp_delegation_payouts
    payouts = db_prd.child(db_name).get()

    for payout in payouts.each():
        # key() is a date string '2021-09-01'
        date = payout.key()
        date = datetime.strptime(date, '%Y-%m-%d')

        date_diff = int((today - date).days)

        if date_diff > TTL:
            db_prd.child(db_name).child(date).remove()


if __name__ == '__main__':
    main()
