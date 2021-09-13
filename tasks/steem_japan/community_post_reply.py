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


def main():
    community_posts = get_community_posts()

    post_reply(community_posts)


def get_community_posts():
    # Get community posts for the last 24 hour
    duration = 86400  # 1 day in seconds
    discussions = []
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
                discussions.append(post)
        else:
            break

    return discussions


def post_reply(community_posts):
    trail_url = 'https://worldofxpilar.com/dash.php?i=1&trail=japansteemit'
    steemlogin_url = 'https://steemlogin.com/sign/delegateVestingShares'
    delegate_url = '?delegator=&delegatee=japansteemit&vesting_shares'
    title = 'Steem Japan Community Reply'

    # Get thank you gif from giphy
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
## Steem Japan: Power Up Week 👇
https://steemit.com/hive-161179/@japansteemit/steem-japan-power-up-week-starts-now
---

Hi @{post.author},
Thank you for your contribution to the Steem Japan Community.
Your post has been upvoted by our curation trail @japansteemit
![](https://i.imgur.com/iishBJJ.png)
## 💡 For More Curation Support 💡
* Please follow our **Curation Trail** [HERE]({trail_url})
* **Delegate SP** [100 SP]({steemlogin_url}{delegate_url}=100%20SP) \
[500 SP]({steemlogin_url}{delegate_url}=500%20SP) \
[1000 SP]({steemlogin_url}{delegate_url}=1000%20SP) \
[2000 SP]({steemlogin_url}{delegate_url}=2000%20SP)

コミュニティーキュレーションのトレールフォローやSPデレゲーションのご協力お願いします🙇
![]({img_url})
    """

        # Post reply comment
        try:
            STEEM.post(
                author=COMMUNITY_NAME,
                title=title,
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
