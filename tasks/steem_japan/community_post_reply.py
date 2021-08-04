import os
import time

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

    for post in community_posts:
        body = f"""
Hi @{post.author},
Thank you for your contribution to the Steem Japan Community.
Your post has been upvoted by our curation trail @japansteemit
---
For More Curation Support❕
コミュニティーキュレーションのトレールフォローやSPデレゲーションのご協力お願いします🙇
If you haven't, please follow our curation trail [here]({trail_url})
Delegate SP [100 SP]({steemlogin_url}{delegate_url}=100%20SP) \
[500 SP]({steemlogin_url}{delegate_url}=500%20SP) \
[1000 SP]({steemlogin_url}{delegate_url}=1000%20SP) \
[2000 SP]({steemlogin_url}{delegate_url}=2000%20SP)
![](https://i.imgur.com/l1ll711.png)
ありがとう🙂
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
