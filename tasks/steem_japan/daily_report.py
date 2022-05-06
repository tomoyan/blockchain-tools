from beem import Steem
import os
import random
import requests
from datetime import datetime, timedelta


NODES = [
    'https://steem.moonjp.xyz',
    'https://api.steemitdev.com',
    'https://steem.justyy.workers.dev',
    'https://api.steem.fans',
    'https://api.steemit.com',
    'https://cn.steems.top',
    'https://api.steem.buzz',
    'https://steem.61bts.com'
]


def get_node():
    random.shuffle(NODES)
    result = NODES[0]

    for node in NODES:
        try:
            response = requests.get(node, timeout=1)
            if response:
                result = node
                break
        except requests.exceptions.RequestException as e:
            print(f'GET_NODE_ERR:{node} {e}')

    return result


POST_KEY = os.environ.get('POST_KEY')
USERNAME = os.environ.get('USERNAME')

STEEM = Steem(node=get_node(), keys=[POST_KEY])
NEWS_API_KEY = '1d6a61e9f7e6482f8d909cb4988cf577'

# Steem Japan
COMMUNITY_ID = 'hive-161179'


def main():
    print('START_DAILY_REPORT')
    post_data = {}

    members = get_community_members()
    post_data['members'] = get_account_info(members)
    post_data['news'] = get_headline_news()
    post_body = make_post_body(post_data)
    publish_post(post_body)

    print('END_DAILY_REPORT')


def get_sds_data(url):
    # get request to sds.steemworld.org
    json_data = {}

    response = requests.get(url)
    json_data = response.json()

    return json_data


def get_community_roles(role):
    # get role members and return list
    print('get_community_roles', role)
    members = []

    url = (
        'https://sds.steemworld.org'
        '/communities_api'
        '/getCommunityRoles'
        f'/{COMMUNITY_ID}'
    )
    json_data = get_sds_data(url)
    community_roles = json_data['result']['rows']
    # {"cols":{"created":0,"account":1,"title":2,"role":3}

    for row in community_roles:
        if row[3] == role:
            print(row[1])
            members.append(row[1])

    return members


def get_community_members():
    # get community members who posted in the last 24 hours
    # return members list
    print('get_community_data')
    members = []

    # get muted members
    muted_members = get_community_roles('muted')

    # last 24h data
    start_epoch = datetime.now() - timedelta(days=1)
    start_epoch = start_epoch.timestamp()

    url = (
        'https://sds.steemworld.org'
        '/feeds_api'
        '/getCommunityPostsByCreated'
        f'/{COMMUNITY_ID}'
    )
    json_data = get_sds_data(url)

    # {"link_id":0,"link_status":1,"author_status":2,"created":3,"payout":4,
    # "payout_comments":5,"net_rshares":6,"reply_count":7,"resteem_count":8,
    # "upvote_count":9,"downvote_count":10,"downvote_weight":11,"word_count":12,
    # "is_muted":13,"is_pinned":14,"last_reply":15,"category":16,"community":17,
    # "author":18,"permlink":19,"title":20,"json_metadata":21,"body":22}
    community_data = json_data['result']['rows']

    for data in community_data:
        # skip muted members
        if data[18] in muted_members:
            continue

        # skip muted posts ("is_muted":13)
        if data[13]:
            continue

        # last 24h posts ("author":18)
        if data[3] > start_epoch:
            if data[18] not in members:
                members.append(data[18])
        else:
            break

    return members


def get_account_info(members):
    # get members account details
    # return list
    print('get_account_info')
    members_str = ','.join(members)
    url = (
        'https://sds.steemworld.org'
        '/accounts_api'
        '/getAccountsFields'
        '/balance_steem,balance_sbd,vests_own,powerdown'
        f'/{members_str}'
    )
    json_data = get_sds_data(url)

    # {'name': 0, 'balance_steem': 1,
    # 'balance_sbd': 2, 'vests_own': 3,
    # 'powerdown': 4, 'balance_sp': 5}
    account_data = json_data['result']['rows']

    for data in account_data:
        # convert vests to sp
        sp = f'{STEEM.vests_to_sp(data[3]):,.2f}'
        data.append(sp)

    return account_data


def get_headline_news():
    print('get_headline_news')
    headline = {
        'topic': '',
        'author': '',
        'content': '',
        'description': '',
        'publishedAt': '',
        'source': '',
        'title': '',
        'url': '',
        'urlToImage': ''
    }

    category = [
        'business', 'entertainment',
        'general', 'health',
        'science', 'sports',
        'technology'
    ]
    # Pick a random category
    topic = random.choice(category)

    url = (
        'https://newsapi.org/v2/top-headlines?'
        'country=jp&'
        f'category={topic}&'
        'pageSize=100&'
        f'apiKey={NEWS_API_KEY}')

    response = requests.get(url)
    json_data = response.json()

    # Pick a random article
    headline = random.choice(json_data['articles'])
    headline['topic'] = topic

    return headline


def make_post_body(data):
    print('get_post_body')

    delegation_url = 'https://steemlogin.com'
    delegation_url += '/sign'
    delegation_url += '/delegateVestingShares'
    delegation_url += '?delegatee=japansteemit'
    delegation_url += '&vesting_shares'

    urltoimage = ''
    if data['news']['urlToImage']:
        urltoimage = f"<img src='{data['news']['urlToImage']}'> <br/>"

    description = ''
    if data['news']['description']:
        description = f"{data['news']['description']} <br/>"

    content = ''
    if data['news']['content']:
        content = f"{data['news']['content']} <br/>"

    member_table = f"""
| | ユーザー名 | STEEM | SBD | SP | PowerDown |
| --- | --- | --- | --- | --- | --- |
"""
    for member in data['members']:
        avatar = \
            f"<img src='https://steemitimages.com/u/{member[0]}/avatar/'>"
        pd = '-'
        if member[4] > 0:
            pd = '⬇️'

        member_table += \
            f"|{avatar}|{member[0]}|{member[1]}\
            |{member[2]}|{member[5]}|{pd}|\n"

    body = f"""
## 今日のニュースAPIから ({data['news']['topic']}) <br/>
{data['news']['title']} <br/>
{urltoimage}
{description}
{content}
[続きはこちら]({data['news']['url']})

![](https://i.imgur.com/o8lNJ68.gif)

### Steemitの仕組みや使い方などを日本語で説明しています
[![](https://i.imgur.com/jT2loCz.png)](https://tinyurl.com/steemit-guide)
### Witness(証人)の投票お願いします
[![](https://i.imgur.com/UJIIIWO.png)](https://steemlogin.com/sign/account-witness-vote?witness=tomoyan.witness&approve=1)

---

## 今日コミュニティー投稿してくれたメンバー (24h)
https://steemit.com/created/hive-161179

{member_table}


---

### Steem Japanのキュレーショントレールをフォローしよう
[![](https://i.imgur.com/Kowo3wZ.png)](https://tinyurl.com/curation-trail)
[![](https://i.imgur.com/AmarQ5N.png)](https://tinyurl.com/twitter-tomoyan)
#### SPをデレゲートするとコミュニティーからUpvoteされます
[100 SP]({delegation_url}=100%20SP) [300 SP]({delegation_url}=300%20SP) [500 SP]({delegation_url}=500%20SP) [1000 SP]({delegation_url}=1000%20SP) [3000 SP]({delegation_url}=3000%20SP) [5000 SP]({delegation_url}=5000%20SP)
"""

    return body


def publish_post(post_body):
    print('publish_post')
    today = datetime.utcnow().strftime("%Y-%m-%d")

    title = f'Steem Japan コミュティーレポート {today}'
    tags = ['hive-161179', 'steem', 'japanese', 'community', 'krsuccess']
    body = post_body

    STEEM.post(
        author=USERNAME,
        title=title,
        body=body,
        tags=tags,
        self_vote=True)


if __name__ == '__main__':
    main()
