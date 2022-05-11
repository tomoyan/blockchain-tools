import os
import time
import requests
import random
from datetime import datetime, timedelta

from beem import Steem
from beem.account import Account
from beem.nodelist import NodeList
# from beem.discussions import Query, Discussions
from beem.instance import set_shared_blockchain_instance
from beem.community import Community

# Clear Caches
# import beem.instance
# beem.instance.clear_cache()

# Setup Steem nodes
nodelist = NodeList()
nodelist.update_nodes()
# nodes = nodelist.get_steem_nodes()
nodes = [
    # 'https://steem.moonjp.xyz',
    # 'https://api.steemitdev.com',
    # 'https://steem.justyy.workers.dev',
    'https://api.steem.fans',
    'https://api.steemit.com',
    # 'https://cn.steems.top',
    'https://api.steem.buzz',
    'https://steem.61bts.com'
]


def get_node():
    result = nodes[0]
    random.shuffle(nodes)

    for node in nodes:
        try:
            response = requests.get(node, timeout=0.5)
            if response:
                result = node
                break
        except requests.exceptions.RequestException as e:
            print(f'GET_NODE_ERR:{node} {e}')

    return result


COMMUNITY_POST_KEY = os.environ.get('COMMUNITY_POST_KEY')
COMMUNITY_NAME = os.environ.get('COMMUNITY_NAME')

STEEM = Steem(node=get_node(), keys=[COMMUNITY_POST_KEY])
set_shared_blockchain_instance(STEEM)
ACCOUNT = Account(COMMUNITY_NAME, blockchain_instance=STEEM)

# Clear BlockchainObject Caching
# ACCOUNT.clear_cache()

TRAIL_URL = 'https://tinyurl.com/curation-trail'
STEEMLOGIN_URL = 'https://steemlogin.com/sign/delegateVestingShares'
DELEGATE_URL = '?delegator=&delegatee=japansteemit&vesting_shares'
TITLE = 'Steem Japan Community Reply'


def main():
    print('START COMMENT')
    community_posts = get_community_posts()

    # comment reply for voted posts
    post_reply(community_posts['voted'])

    # comment reply for unvoted posts
    post_comment(community_posts['unvoted'])

    print('END COMMENT')


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


def get_community_roles(role):
    # get role members and return list
    print('get_community_roles', role)
    members = []
    steem_japan = 'hive-161179'

    url = (
        'https://sds.steemworld.org'
        '/communities_api'
        '/getCommunityRoles'
        f'/{steem_japan}'
    )
    response = requests.get(url)
    json_data = response.json()
    community_roles = json_data['result']['rows']
    # {"cols":{"created":0,"account":1,"title":2,"role":3}

    for row in community_roles:
        if row[3] == role:
            members.append(row[1])

    return members


def get_community_posts():
    # Get community posts for the last 24 hour
    # duration = 86400  # 1 day in seconds
    voted_discussions = []
    unvoted_discussions = []
    steem_japan = 'hive-161179'
    # muted = get_muted_members()
    muted = get_community_roles('muted')

    # last 24h data
    start_epoch = datetime.now() - timedelta(days=1)
    start_epoch = start_epoch.timestamp()

    url = (
        'https://sds.steemworld.org'
        '/feeds_api'
        '/getCommunityPostsByCreated'
        f'/{steem_japan}'
    )

    response = requests.get(url)
    json_data = response.json()
    community_data = json_data['result']['rows']

    for data in community_data:
        if data[18] in muted:
            continue

        if data[3] > start_epoch:
            has_voted = ACCOUNT.has_voted(f'{data[18]}/{data[19]}')
            if has_voted:
                voted_discussions.append({
                    'author': data[18],
                    'identifier': f'{data[18]}/{data[19]}'
                })
            else:
                unvoted_discussions.append({
                    'author': data[18],
                    'identifier': f'{data[18]}/{data[19]}'
                })
        else:
            break

    # Query community posts
    # query = Query(tag=steem_japan)
    # d = Discussions()
    # posts = d.get_discussions('created', query, limit=100)

    # # Store posts that are less than 1 hour old
    # for post in posts:
    #     # Skip muted members
    #     if post.author in muted:
    #         continue

    #     if post.time_elapsed().total_seconds() < duration:
    #         has_voted = ACCOUNT.has_voted(post)
    #         if has_voted:
    #             voted_discussions.append(post)
    #         else:
    #             unvoted_discussions.append(post)
    #     else:
    #         break

    return {
        'voted': voted_discussions,
        'unvoted': unvoted_discussions
    }


def post_reply(community_posts):
    # post a comment for voted posts

    # Get 'thank you' gif from giphy
    url = (
        'http://api.giphy.com/v1/gifs/search?'
        'q=arigato thanks appreciation&'
        'api_key=b2w5nCHfqrGt6tbXBD7BCcfw11plV5b1&'
        'limit=100'
    )
    response = requests.get(url)
    json_data = response.json()

    # Pick one random image data from json response
    default_img = 'https://i.imgur.com/6qvr7sJ.jpg'
    image_data = random.choice(json_data['data'])
    gif_img = image_data['images']['original']['url']
    gif_img = gif_img.split('?', 1)[0]
    img_url = gif_img or default_img

    for post in community_posts:
        body = f"""
![]({img_url})
@{post['author']} さん、こんにちは。
@japansteemitがこの記事を**アップボート**しました。

![](https://cdn.steemitimages.com/DQmTqjyUPHQynfivV8eREroJhUfcSCvFJ4krct5KgTedAQt/image.png)
#steemexclusiveのタグを使うとSteemitチームがアップボートしてくれるかも。

Steemitの証人(witness)になったので投票お願いします！
[![](https://i.imgur.com/UJIIIWO.png)](https://steemlogin.com/sign/account-witness-vote?witness=tomoyan.witness&approve=1)

### 💡 アップボートガイド 💡
* SPデレゲーション [500 SP]({STEEMLOGIN_URL}{DELEGATE_URL}=500%20SP) \
[1000 SP]({STEEMLOGIN_URL}{DELEGATE_URL}=1000%20SP) \
[2000 SP]({STEEMLOGIN_URL}{DELEGATE_URL}=2000%20SP) \
[3000 SP]({STEEMLOGIN_URL}{DELEGATE_URL}=3000%20SP) \
[5000 SP]({STEEMLOGIN_URL}{DELEGATE_URL}=5000%20SP)
* Set 10-30% beneficiary to @japansteemit
* コミュニティーキュレーショントレールをフォロー [ここ]({TRAIL_URL})

コミュニティーキュレーションのフォローやSPデレゲーションのご協力お願いします🙇
[![](https://i.imgur.com/jT2loCz.png)](https://tinyurl.com/steemit-guide)
[![](https://i.imgur.com/Fk8AhOW.png)](https://discord.gg/pE5fuktSAt)
    """

        # Post reply comment
        try:
            STEEM.post(
                author=COMMUNITY_NAME,
                title=TITLE,
                body=body,
                reply_identifier=post['identifier'],
                self_vote=False)
        except Exception:
            continue
        finally:
            # Posting is allowed every 3 seconds
            # Sleep 5 secs
            time.sleep(5)


def post_comment(unvoted_posts):
    # post a comment for unvoted posts
    for post in unvoted_posts:
        body = f"""
@{post['author']} さん、こんにちは。
![image.png](https://cdn.steemitimages.com/DQmTqjyUPHQynfivV8eREroJhUfcSCvFJ4krct5KgTedAQt/image.png)
### 💡 アップボートガイド 💡
* SPデレゲーション [500 SP]({STEEMLOGIN_URL}{DELEGATE_URL}=500%20SP) \
[1000 SP]({STEEMLOGIN_URL}{DELEGATE_URL}=1000%20SP) \
[2000 SP]({STEEMLOGIN_URL}{DELEGATE_URL}=2000%20SP) \
[3000 SP]({STEEMLOGIN_URL}{DELEGATE_URL}=3000%20SP) \
[5000 SP]({STEEMLOGIN_URL}{DELEGATE_URL}=5000%20SP)
* Set 10-30% beneficiary to @japansteemit
* コミュニティーキュレーショントレールをフォロー [ここ]({TRAIL_URL})

#steemexclusiveのタグを使うとSteemitチームがアップボートしてくれるかも。

Steemitの証人(witness)になったので投票お願いします！
[![](https://i.imgur.com/UJIIIWO.png)](https://steemlogin.com/sign/account-witness-vote?witness=tomoyan.witness&approve=1)


コミュニティーキュレーションのフォローやSPデレゲーションのご協力お願いします🙇
[![](https://i.imgur.com/jT2loCz.png)](https://tinyurl.com/steemit-guide)
[![](https://i.imgur.com/Fk8AhOW.png)](https://discord.gg/pE5fuktSAt)
        """

        # Post reply comment
        try:
            STEEM.post(
                author=COMMUNITY_NAME,
                title=TITLE,
                body=body,
                reply_identifier=post['identifier'],
                self_vote=False)
        except Exception:
            continue
        finally:
            # Posting is allowed every 3 seconds
            # Sleep 5 secs
            time.sleep(5)


if __name__ == '__main__':
    main()
