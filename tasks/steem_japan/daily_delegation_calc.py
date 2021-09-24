import collections
from pprint import pprint
from datetime import datetime
import requests
import pyrebase
import base64
import json
import os
import time

from beem import Steem
from beem.account import Account
from beem.nodelist import NodeList
from beem.instance import set_shared_blockchain_instance

# Setup Steem nodes
nodelist = NodeList()
nodelist.update_nodes()
nodes = nodelist.get_steem_nodes()
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
    print('START DELEGATOR_PAYOUT')
    today = datetime.now().strftime("%Y-%m-%d")

    account = Account(COMMUNITY_NAME, blockchain_instance=STEEM)
    sp_total = 0.0
    payout_data = {}

    # Get curation reward for the last 24 hours
    curation_reward = account.get_curation_reward(days=1)

    # 50% of the curation reward will be divided and distributed
    # to SP delegators
    budget = curation_reward / 2
    # print('REWARD_BUDGET_TODAY', budget, 'SP')

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
        # print('RESPONSE_JSON_DATA', json_data)

        counter = collections.Counter()
        for d in json_data:
            counter.update(d)

        result = dict(counter)
        sp_total = result['sp']

        # Each delegator will get their share based on the delegated SP
        for data in json_data:
            percentage = data['sp'] / sp_total
            reward = budget * percentage
            payout_data[data['delegator']] = reward
    else:
        print('GET REQUEST ERROR:', response.status_code)

    db_prd.child(db_name).child(today).set(payout_data)

    print('END DELEGATOR_PAYOUT')
    return payout_data


def get_payout_data(payout_month=None):
    payout_data = {}

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
        # val() {'abby0207': 0.01252727737602502}
        data = payout.val()
        for name in data:
            if name in payout_data:
                payout_data[name] += data[name]
            else:
                payout_data[name] = data[name]

    return payout_data


def process_delegation_payout():
    payout_day = 1
    minimum = 0.001
    now = datetime.now()

    try:
        ACCOUNT = Account(COMMUNITY_NAME, blockchain_instance=STEEM)
        ACCOUNT.transfer('tomoyan', 1, 'STEEM', 'Payout Test')
    except Exception as err:
        print(err)

    # delegation payout is 1st day of the month
    if now.day != payout_day:
        return

    # get last months payout data
    # payout_month = now.month - 1
    # payout_data = get_payout_data(payout_month)
    # memo = f'Steem Japan SP Delegation Reward: {payout_month}'

    # for p in payout_data:
    #     amount = float(f'{payout_data[p]: .3f}')

    #     # Skip small transactions
    #     if amount < minimum:
    #         continue

    #     try:
    #         ACCOUNT = Account('japansteemit', blockchain_instance=STEEM)
    #         ACCOUNT.transfer(p, amount, 'STEEM', memo)
    #     except Exception as err:
    #         print(err)


def payout_data_cleanup():
    # Clean up data that is more than 2 months old
    now = datetime.now()
    diff_month_2 = now.month - 2

    if diff_month_2 <= 0:
        diff_month_2 += 12

    # Get data from sp_delegation_payouts
    payouts = db_prd.child(db_name).get()

    for payout in payouts.each():
        # key() is a date string '2021-09-01'
        date = payout.key()

        # Check month of date string
        month = time.strptime(date, "%Y-%m-%d").tm_mon

        if month <= diff_month_2:
            # remove data from firebase
            db_prd.child(db_name).child(date).remove()


if __name__ == '__main__':
    main()
