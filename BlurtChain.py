from beem.instance import set_shared_blockchain_instance
from beem.account import Account
from beem.amount import Amount
# from beem.nodelist import NodeList
from beem import Blurt

from datetime import datetime, timedelta
from statistics import mean
import random
from functools import lru_cache
# import logging
# from dumper import dump


class BlurtChain:
    """docstring for Chain"""
    # Setup node list for Blurt
    # Create Blurt chain object

    def __init__(self, username):
        self.username = username
        self.account = None
        self.nodes = [
            # 'https://api.blurt.blog',
            'https://rpc.blurt.buzz',
            'https://rpc.blurt.world',
            'https://blurtd.privex.io']
        random.shuffle(self.nodes)

        self.blurt = Blurt(node=self.nodes)
        # dump(self.blurt)
        self.blockchain = set_shared_blockchain_instance(self.blurt)

        # Create account object
        try:
            self.account = Account(self.username, full=False, lazy=False)
        except Exception as e:
            self.username = None
            self.account = None
            print(f'AccountDoesNotExistsException : {e}')

    # @lru_cache
    def get_account_info(self):
        self.account_info = {}

        if self.username:
            # GET BLURT AMOUNT
            available_balances = self.account.available_balances
            blurt = available_balances[0]
            blurt = str(blurt).split()[0]
            self.account_info['blurt'] = f'{float(blurt):,.3f}'

            # GET BLURT POWER
            blurt_power = self.account.get_steem_power()
            self.account_info['bp'] = f'{blurt_power:,.3f}'

            # GET VOTING POWER %
            voting_power = self.account.get_voting_power()
            self.account_info['voting_power'] = f'{voting_power:.2f}'

        return self.account_info

    # @lru_cache
    def get_follower(self):
        self.follower_data = {}
        follower = []
        following = []
        common = []

        if self.username:
            follower = self.account.get_followers(self.username)
            following = self.account.get_following(self.username)
            common = set(follower) & set(following)

        for username in follower:
            if username in common:
                self.follower_data[username] = 1
            else:
                self.follower_data[username] = 0

        return self.follower_data

    # @lru_cache
    def get_following(self):
        self.following_data = {}
        follower = []
        following = []
        common = []

        if self.username:
            follower = self.account.get_followers(self.username)
            following = self.account.get_following(self.username)
            common = set(follower) & set(following)

        for username in following:
            if username in common:
                self.following_data[username] = 1
            else:
                self.following_data[username] = 0

        return self.following_data

    @lru_cache(maxsize=32)
    def get_vote_history(self):
        votes = {}
        result = {}
        labels = []
        permlinks = []
        count_data = []
        weight_data = []
        total_votes = 0
        stop = datetime.utcnow() - timedelta(days=7)

        if self.username:
            history = self.account.history_reverse(
                stop=stop, only_ops=['vote'])

            # Count how many times voted in 7 days
            for data in history:
                if self.username == data["voter"]:
                    permlink = f'@{data["author"]}/{data["permlink"]}'
                    permlinks.append(permlink)

                    if data["author"] in votes.keys():
                        votes[data["author"]]['count'] += 1
                        votes[data["author"]
                              ]['weight'].append(data["weight"])
                    else:
                        votes[data["author"]] = {
                            'count': 1,
                            'weight': [data["weight"]],
                        }
                else:
                    next

            for key, value in votes.items():
                labels.append(key)
                count_data.append(value['count'])
                weight_data.append(mean(value['weight']) * 0.01)

                total_votes += value['count']
                value['weight'] = mean(value['weight']) * 0.01

        result['total_votes'] = total_votes

        result['labels'] = labels
        result['permlinks'] = sorted(permlinks)
        result['count_data'] = count_data
        result['weight_data'] = weight_data

        return result

    @lru_cache(maxsize=32)
    def get_mute(self):
        data = {}

        if self.username:
            data['muter'] = self.account.get_muters()
            data['muting'] = self.account.get_mutings()

        return data

    # @lru_cache(maxsize=32)
    def get_delegation(self):
        # find delegations for username
        data = {}

        if self.username:
            # find outgoing delegatons
            data['outgoing'] = self.account.get_vesting_delegations()
            for value in data['outgoing']:
                # vests to BP conversion
                # vests = Amount(value['vesting_shares'])
                # bp = self.blurt.vests_to_bp(vests.amount)
                # value['bp'] = f'{bp:.3f}'
                value['bp'] = self.vests_to_bp(value['vesting_shares'])

            # find expiring delegatons
            data['expiring'] = self.account.get_expiring_vesting_delegations()
            for value in data['expiring']:
                # vests to BP conversion
                # vests = Amount(value['vesting_shares'])
                # bp = self.blurt.vests_to_bp(vests.amount)
                # value['bp'] = f'{bp:.3f}'
                value['bp'] = self.vests_to_bp(value['vesting_shares'])

            # find incoming delegatons
            data['incoming'] = []
            incoming_temp = dict()
            for operation in self.account.history(
                    only_ops=["delegate_vesting_shares"]):

                if self.username == operation["delegator"]:
                    continue

                if operation["vesting_shares"] == '0.000000 VESTS':
                    incoming_temp.pop(operation["delegator"])
                    continue
                else:
                    incoming_temp[operation["delegator"]] = operation

            for key, value in incoming_temp.items():
                value['bp'] = self.vests_to_bp(value['vesting_shares'])
                data['incoming'].append(value)

        return data

    def vests_to_bp(self, vests):
        # VESTS to BP conversion
        bp = 0.000
        v = Amount(vests)
        bp = self.blurt.vests_to_bp(v.amount)
        bp = f'{bp:.3f}'

        return bp
