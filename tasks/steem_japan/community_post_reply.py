import os
import time
import requests
import random

from beem import Steem
from beem.account import Account
from beem.nodelist import NodeList
from beem.discussions import Query, Discussions
from beem.instance import set_shared_blockchain_instance

# Setup Steem nodes
nodelist = NodeList()
nodelist.update_nodes()
nodes = nodelist.get_steem_nodes()

COMMUNITY_POST_KEY = os.environ.get('COMMUNITY_POST_KEY')
COMMUNITY_NAME = os.environ.get('COMMUNITY_NAME')

STEEM = Steem(node=nodes, keys=[COMMUNITY_POST_KEY])
set_shared_blockchain_instance(STEEM)
ACCOUNT = Account(COMMUNITY_NAME, blockchain_instance=STEEM)

TRAIL_URL = 'https://tinyurl.com/curation-trail'
STEEMLOGIN_URL = 'https://steemlogin.com/sign/delegateVestingShares'
DELEGATE_URL = '?delegator=&delegatee=japansteemit&vesting_shares'
TITLE = 'Steem Japan Community Reply'


def main():
    community_posts = get_community_posts()

    # comment reply for voted posts
    post_reply(community_posts['voted'])

    # comment reply for unvoted posts
    post_comment(community_posts['unvoted'])


def get_community_posts():
    # Get community posts for the last 24 hour
    duration = 86400  # 1 day in seconds
    voted_discussions = []
    unvoted_discussions = []
    steem_japan = 'hive-161179'

    # Query community posts
    query = Query(tag=steem_japan)
    d = Discussions()
    posts = d.get_discussions('created', query, limit=100)

    # Store posts that are less than 1 hour old
    for post in posts:
        if post.time_elapsed().total_seconds() < duration:
            has_voted = ACCOUNT.has_voted(post)
            if has_voted:
                voted_discussions.append(post)
            else:
                unvoted_discussions.append(post)
        else:
            break

    return {
        'voted': voted_discussions,
        'unvoted': unvoted_discussions
    }


def post_reply(community_posts):
    # post a comment for voted posts

    # Get 'thank you' gif from giphy
    url = (
        'http://api.giphy.com/v1/gifs/search?'
        'q=arigato thanks heart&'
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
@{post.author} さん、こんにちは。
@japansteemitがこの記事をアップボートしました。
This post has been upvoted by @japansteemit

![image.png](https://cdn.steemitimages.com/DQmTqjyUPHQynfivV8eREroJhUfcSCvFJ4krct5KgTedAQt/image.png)
Steemitチームがコミュニティー記事をアップボートしてくれるので、 #club5050 #steemexclusive のタグを使いましょう。
Use #club5050 #steemexclusive tags for more upvotes from Steemit team.
[Information - #steemexclusiveについて](https://tinyurl.com/steemexclusive)
[Information - #club5050について](https://tinyurl.com/club5050)
---

### 💡 Curation Guide (アップボートガイド) 💡
* Post about Japan (Japanese or English)
* Set 10~30% reward to japansteemit
* Follow our **Curation Trail** [HERE]({TRAIL_URL})
* **Delegate SP** [100 SP]({STEEMLOGIN_URL}{DELEGATE_URL}=100%20SP) \
[500 SP]({STEEMLOGIN_URL}{DELEGATE_URL}=500%20SP) \
[1000 SP]({STEEMLOGIN_URL}{DELEGATE_URL}=1000%20SP) \
[2000 SP]({STEEMLOGIN_URL}{DELEGATE_URL}=2000%20SP)

コミュニティーキュレーションのトレールフォローやSPデレゲーションのご協力お願いします🙇
![]({img_url})
    """

        # Post reply comment
        try:
            STEEM.post(
                author=COMMUNITY_NAME,
                title=TITLE,
                body=body,
                reply_identifier=post.identifier,
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
@{post.author} さん、こんにちは。

![image.png](https://cdn.steemitimages.com/DQmTqjyUPHQynfivV8eREroJhUfcSCvFJ4krct5KgTedAQt/image.png)
Steemitチームがコミュニティー記事をアップボートしてくれるので、 #club5050 #steemexclusive のタグを使いましょう。
Use #club5050 #steemexclusive tags for more upvotes from Steemit team.
[Information - #steemexclusiveについて](https://tinyurl.com/steemexclusive)
[Information - #club5050について](https://tinyurl.com/club5050)

---

### 💡 Curation Guide (アップボートガイド) 💡
* Post about Japan (Japanese or English)
* Set 10~30% reward to japansteemit
* No upvote if you power down
* Upvote other members
* Follow our **Curation Trail** [HERE]({TRAIL_URL})
* **Delegate SP** [100 SP]({STEEMLOGIN_URL}{DELEGATE_URL}=100%20SP) \
[500 SP]({STEEMLOGIN_URL}{DELEGATE_URL}=500%20SP) \
[1000 SP]({STEEMLOGIN_URL}{DELEGATE_URL}=1000%20SP) \
[2000 SP]({STEEMLOGIN_URL}{DELEGATE_URL}=2000%20SP)

[![](https://i.imgur.com/Fk8AhOW.png)](https://discord.gg/pE5fuktSAt)
        """

        # Post reply comment
        try:
            STEEM.post(
                author=COMMUNITY_NAME,
                title=TITLE,
                body=body,
                reply_identifier=post.identifier,
                self_vote=False)
        except Exception:
            continue
        finally:
            # Posting is allowed every 3 seconds
            # Sleep 5 secs
            time.sleep(5)


if __name__ == '__main__':
    main()
