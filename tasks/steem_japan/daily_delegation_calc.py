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

DELEGATOR_LIST = """
    [
        {
            "delegator":"crowsaint",
            "delegatee":"japansteemit",
            "sp":20.000874819086032,
            "vesting":37188.202343,
            "time":"2021-09-02 04:45:00"
        },
        {
            "delegator":"kyrie1234",
            "delegatee":"japansteemit",
            "sp":50.0394600679226,
            "vesting":93039.808657,
            "time":"2021-08-25 00:49:21"
        },
        {
            "delegator":"abby0207",
            "delegatee":"japansteemit",
            "sp":100.08019218843472,
            "vesting":186081.982478,
            "time":"2021-08-24 21:20:04"
        },
        {
            "delegator":"malihafarhan",
            "delegatee":"japansteemit",
            "sp":15.015661101557795,
            "vesting":27919.050962,
            "time":"2021-08-22 06:38:33"
        },
        {
            "delegator":"keighostsashiro",
            "delegatee":"japansteemit",
            "sp":10.01642047057367,
            "vesting":18623.818937,
            "time":"2021-08-15 20:24:18"
        },
        {
            "delegator":"maikuraki",
            "delegatee":"japansteemit",
            "sp":40.06710857240815,
            "vesting":74497.928434,
            "time":"2021-08-15 10:55:57"
        },
        {
            "delegator":"angma",
            "delegatee":"japansteemit",
            "sp":862.0000975366572,
            "vesting":1602741.596897,
            "time":"2021-08-08 13:50:42"
        },
        {
            "delegator":"sakura-sakura",
            "delegatee":"japansteemit",
            "sp":10.025155781456771,
            "vesting":18640.060752,
            "time":"2021-08-06 13:29:48"
        },
        {
            "delegator":"fabio2614",
            "delegatee":"japansteemit",
            "sp":100.28139835667523,
            "vesting":186456.090899,
            "time":"2021-08-03 10:30:10"
        },
        {
            "delegator":"junebride",
            "delegatee":"japansteemit",
            "sp":100.32343126741718,
            "vesting":186534.2439,
            "time":"2021-07-30 01:34:20"
        },
        {
            "delegator":"darkcrow",
            "delegatee":"japansteemit",
            "sp":100.44881695254327,
            "vesting":186767.377114,
            "time":"2021-07-17 05:09:43"
        },
        {
            "delegator":"saneunji",
            "delegatee":"japansteemit",
            "sp":100.62738604859724,
            "vesting":187099.395775,
            "time":"2021-06-29 04:45:41"
        },
        {
            "delegator":"kan6034",
            "delegatee":"japansteemit",
            "sp":1006.2957662980351,
            "vesting":1871034.687857,
            "time":"2021-06-28 23:23:09"
        },
        {
            "delegator":"hae-ra",
            "delegatee":"japansteemit",
            "sp":100.6847961089748,
            "vesting":187206.139953,
            "time":"2021-06-23 14:01:18"
        },
        {
            "delegator":"rt395",
            "delegatee":"japansteemit",
            "sp":100.69415986922486,
            "vesting":187223.550262,
            "time":"2021-06-22 16:20:25"
        },
        {
            "delegator":"maxinpower",
            "delegatee":"japansteemit",
            "sp":503.4770336071505,
            "vesting":936129.342851,
            "time":"2021-06-22 13:35:57"
        },
        {
            "delegator":"juichi",
            "delegatee":"japansteemit",
            "sp":504.1599565312544,
            "vesting":937399.121104,
            "time":"2021-06-09 08:29:32"
        },
        {
            "delegator":"tyrnannoght",
            "delegatee":"japansteemit",
            "sp":100.91767666120239,
            "vesting":187639.141468,
            "time":"2021-06-01 03:27:23"
        },
        {
            "delegator":"dasomee",
            "delegatee":"japansteemit",
            "sp":10.092624094101128,
            "vesting":18765.506528,
            "time":"2021-05-31 07:54:31"
        },
        {
            "delegator":"jobreyes24",
            "delegatee":"japansteemit",
            "sp":100.96797300501568,
            "vesting":187732.658908,
            "time":"2021-05-27 08:32:14"
        },
        {
            "delegator":"cryptokannon",
            "delegatee":"japansteemit",
            "sp":2019.7265258453726,
            "vesting":3755335.674067,
            "time":"2021-05-25 14:52:06"
        },
        {
            "delegator":"maris75",
            "delegatee":"japansteemit",
            "sp":10.102885902082432,
            "vesting":18784.586603,
            "time":"2021-05-21 13:45:30"
        },
        {
            "delegator":"liamnov",
            "delegatee":"japansteemit",
            "sp":10.11146086692998,
            "vesting":18800.530282,
            "time":"2021-05-13 09:46:01"
        },
        {
            "delegator":"yasu",
            "delegatee":"japansteemit",
            "sp":2023.9355483808708,
            "vesting":3763161.630838,
            "time":"2021-05-05 14:51:57"
        },
        {
            "delegator":"tomoyan",
            "delegatee":"japansteemit",
            "sp":2031.0362127963488,
            "vesting":3776364.100602,
            "time":"2021-04-10 16:05:00"
        },
    ]"""


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
        'hash=bd7ba17ff62b8d47daa1fb21fd57b321&_=1630601157000'
    )
    response = requests.get(url)

    if response:
        json_data = response.json()
        print('RESPONSE_JSON_DATA', json_data)
        json_data = DELEGATOR_LIST
        print('RESPONSE_JSON_DATA', json_data)

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
