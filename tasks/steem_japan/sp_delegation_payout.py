# import collections
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


def get_node():
    random.shuffle(nodes)
    for node in nodes:
        try:
            response = requests.get(node, timeout=1)
            if response:
                return node
        except requests.exceptions.RequestException as e:
            print(f'GET_NODE_ERR:{node} {e}')


COMMUNITY_ACTIVE_KEY = os.environ.get('COMMUNITY_ACTIVE_KEY')
COMMUNITY_NAME = os.environ.get('COMMUNITY_NAME')
STEEM = Steem(node=get_node(), keys=[COMMUNITY_ACTIVE_KEY])
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
    # Run python tasks/steem_japan/sp_delegation_payout.py
    print('SP_DELEGATION_PAYOUT_START')

    # Payout gets executed once a month
    process_delegation_payout()

    print('SP_DELEGATION_PAYOUT_END')


def get_muted_members():
    print('GET_MUTED_MEMBERS')
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
    print('GET_PAYOUT_DATA')
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
    print('process_delegation_payout')
    minimum = 0.001
    now = datetime.now()

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
            print('TRANSFER:', p, amount, memo)
        except Exception as err:
            print(err, p, amount, memo)


if __name__ == '__main__':
    main()
