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
STEEM = Steem(node=nodes)
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

    # clean up sp_delegation_payouts data
    payout_data_cleanup()


def delegator_payout_calc():
    print('START DELEGATOR_PAYOUT')
    today = datetime.now().strftime("%Y-%m-%d")

    username = 'japansteemit'
    account = Account(username, blockchain_instance=STEEM)
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
