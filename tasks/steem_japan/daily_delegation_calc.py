import collections
from pprint import pprint
from datetime import datetime
import requests
import pyrebase
import base64
import json
import os

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

    # get_payout_data()


# def get_payout_data():
#     payouts = db_prd.child(db_name).get()
#     for payout in payouts.each():
#         print('key', payout.key())  # key 2021-09-01
#         print('val', payout.val())  # val {'abby0207': 0.01252727737602502}


def delegator_payout_calc():
    print('START DELEGATOR_PAYOUT')
    today = datetime.now().strftime("%Y-%m-%d")

    username = 'japansteemit'
    print('Account:', username)
    account = Account(username, blockchain_instance=STEEM)
    sp_total = 0.0
    payout_data = {}

    # Get curation reward for the last 24 hours
    curation_reward = account.get_curation_reward(days=1)

    # 50% of the curation reward will be divided and distributed
    # to SP delegators
    budget = curation_reward / 2
    print('REWARD_BUDGET_TODAY', budget, 'SP')

    # Get a list of SP delegators from justyy
    url = (
        'https://api.justyy.workers.dev/api/steemit/delegators/?'
        'cached&'
        'id=japansteemit&'
        'hash=fc4349f09bb701c1d410dd92af367473&_=1630443351251'
    )
    response = requests.get(url)

    if response:
        json_data = response.json()

        counter = collections.Counter()
        for d in json_data:
            counter.update(d)

        result = dict(counter)
        sp_total = result['sp']
        print('DELEGATION_TOTAL', sp_total, 'SP')

        # Each delegator will get their share based on the delegated SP
        for data in json_data:
            percentage = data['sp'] / sp_total
            reward = budget * percentage
            payout_data[data['delegator']] = reward
    else:
        print('Get request error:', response.status_code)

    db_prd.child(db_name).child(today).set(payout_data)

    return payout_data


if __name__ == '__main__':
    main()
