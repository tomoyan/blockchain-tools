from datetime import datetime
import os
import urllib.request
from PIL import Image
import random
from pexels_api import API
import requests

from beem import Steem
from beem.account import Account
from beem.nodelist import NodeList
from beem.discussions import Query, Discussions
from beem.imageuploader import ImageUploader
from beem.instance import set_shared_blockchain_instance
from beem.community import Community

# Setup Steem nodes
nodelist = NodeList()
nodelist.update_nodes()
# nodes = nodelist.get_steem_nodes()
nodes = [
    'https://api.steemitdev.com',
    'https://steem.justyy.workers.dev',
    'https://api.steem.fans',
    'https://api.steemit.com',
    'https://cn.steems.top',
    'https://api.steem.buzz',
    'https://steem.61bts.com']


def get_node():
    random.shuffle(nodes)
    for node in nodes:
        try:
            response = requests.get(node, timeout=1)
            if response:
                return node
        except requests.exceptions.RequestException as e:
            print(f'GET_NODE_ERR:{node} {e}')


POST_KEY = os.environ.get('POST_KEY')
USERNAME = os.environ.get('USERNAME')

STEEM = Steem(node=get_node(), keys=[POST_KEY])
set_shared_blockchain_instance(STEEM)
IU = ImageUploader(blockchain_instance=STEEM)

PEXELS_API_KEY = '563492ad6f917000010000016acbeee6e44d432392217f9f901098f4'
NEWS_API_KEY = '1d6a61e9f7e6482f8d909cb4988cf577'


def main():
    # Run this script
    # python tasks/steem_japan/steem_japan_report.py
    # Post daily report to my own blog
    print('Start steem_japan_report')

    discussions = get_community_posts()

    # Community activity stats
    post_data = get_stats(discussions)

    # Get today's news from newsapi.org
    post_data['news'] = get_headline_news()

    # Get main image for report
    post_data['main_image'] = get_main_image()

    post_body = get_post_body(post_data)

    publish_post(post_body)
    print('End steem_japan_report')


def get_headline_news():
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


def get_community_posts(duration=86400, community_tag='hive-161179'):
    # Get community posts
    discussions = []
    # steem_japan = 'hive-161179'
    # duration = 90000  # 25 hours in seconds

    # Get community posts
    query = Query(tag=community_tag)
    d = Discussions()
    posts = d.get_discussions('created', query, limit=1000)

    # Save posts that are less than the duration
    for post in posts:
        if post.time_elapsed().total_seconds() < duration:
            discussions.append(post)
        else:
            break

    return discussions


def check_account(username):
    data = {
        'steem': '0.00',
        'sbd': '0.00',
        'sp': '0.00',
        'power_down': 0.0,
    }
    power_down = 0.0
    account = Account(username, blockchain_instance=STEEM)
    steem = str(account.available_balances[0]).split()[0]
    sbd = str(account.available_balances[1]).split()[0]
    sp = f'{account.get_steem_power():.2f}'

    account_json = account.json()
    withdraw_rate = int(account_json['vesting_withdraw_rate']['amount'])
    vest_amount = int(account_json['vesting_shares']['amount'])
    vest_to_withdraw = int(account_json['to_withdraw'])

    if not withdraw_rate or not vest_amount or not vest_to_withdraw:
        power_down = 0.0
    else:
        # calculate power down %
        power_down = vest_to_withdraw / vest_amount * 100
        if power_down > 100.0:
            power_down = 100.0

    data['steem'] = steem
    data['sbd'] = sbd
    data['sp'] = sp
    data['power_down'] = power_down

    return data


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


def get_stats(discussions):
    data = dict()
    active_members = []
    total_posts = 0
    total_votes = 0
    total_comments = 0
    muted = get_muted_members()

    # Find active members and posts for the day
    for d in discussions:
        username = d.author

        # Skip muted member stats
        if username in muted:
            continue

        if username not in data.keys():
            user_data = check_account(username)

            # user rating
            star = ''
            if 0 <= float(user_data["sp"]) < 100:
                star = ''
            elif 100 <= float(user_data["sp"]) < 500:
                star = '⭐'
            elif 500 <= float(user_data["sp"]) < 1000:
                star = '⭐⭐'
            elif 1000 <= float(user_data["sp"]) < 5000:
                star = '✨'
            elif 5000 <= float(user_data["sp"]) < 50000:
                star = '🐬'
            else:
                star = '🐳'

            data[username] = {
                'posts': [d.permlink],
                'votes': 0,
                'comments': 0,
                'steem': user_data["steem"],
                'sbd': user_data["sbd"],
                'sp': user_data["sp"],
                'power_down': f'{user_data["power_down"]:.2f}',
                'star': star,
            }
            total_posts += 1
            continue

        data[username]['posts'].append(d.permlink)
        total_posts += 1

    active_members = data.keys()

    # Find number of comments/votes to active members
    for d in discussions:
        # Check comments
        replies = d.get_all_replies()
        for reply in replies:
            if reply.author in active_members:
                data[reply.author]['comments'] += 1
                total_comments += 1

        # Check member's vote numbers
        voters = d.get_votes().get_list()
        for username in voters:
            if username in active_members:
                data[username]['votes'] += 1
                total_votes += 1

    return {
        'stats': data,
        'total_posts': total_posts,
        'total_votes': total_votes,
        'total_comments': total_comments
    }


def get_main_image():
    # Download base image from pexels.com API
    # and store as report_base.png

    # Default Image URL
    img_url = 'https://i.imgur.com/wOSnnYI.png'

    img_dir = f'tasks/steem_japan'

    base_img_file = 'report_base.png'
    overlay_img_file = 'report_overlay.png'
    main_img_file = 'report_main.png'

    # Setting up user_agent, base_image_url
    user_agent_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'AppleWebKit/537.36 (KHTML, like Gecko)',
        'Chrome/92.0.4515.101 Safari/537.36'
    ]
    user_agent = ' '.join(user_agent_list)
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent', user_agent)]
    urllib.request.install_opener(opener)

    # base_image_url = "https://loremflickr.com/610/427/japan"

    # Pick a random page number
    page_number = random.randint(1, 80)

    # Search Japan image and access image data from pexels API
    PEXELS_API = API(PEXELS_API_KEY)
    PEXELS_API.search('japan', page=page_number, results_per_page=10)
    photos = PEXELS_API.get_entries()

    # Pick a random photo
    photos = [random.choice(photos)]

    base_image_url = ''
    image_params = '?auto=compress&cs=tinysrgb&fit=crop&h=427&w=610'
    for photo in photos:
        base_image_url = photo.landscape.split('?')[0]

    base_image_url += image_params

    # Call urlretrieve function to get an image
    urllib.request.urlretrieve(base_image_url, f'{img_dir}/{base_img_file}')

    # Open base image
    base_image = Image.open(rf"{img_dir}/{base_img_file}")

    # Open overlay image
    overlay_image = Image.open(
        rf"{img_dir}/{overlay_img_file}").convert("RGBA")

    # Paste overlay_image on top of base image at coordinates (x, y)
    base_image.paste(overlay_image, (5, 150), mask=overlay_image)

    # Save overlay image
    base_image.save(f'{img_dir}/{main_img_file}')

    # Upload image to steem
    # and get the uploaded image URL
    result = IU.upload(f'{img_dir}/{main_img_file}', USERNAME)
    img_url = result['url']

    return {
        'url': img_url,
        'src': base_image_url}


def get_post_body(data):
    sp_url = 'https://steemlogin.com/sign/delegateVestingShares'
    sp_url += '?delegator=&delegatee=japansteemit&vesting_shares='
    sp_delegation_list = [
        f'|[100 SP]({sp_url}100%20SP)',
        f'|[500 SP]({sp_url}500%20SP)',
        f'|[1000 SP]({sp_url}1000%20SP)',
        f'|[2000 SP]({sp_url}2000%20SP)',
        f'|[3000 SP]({sp_url}3000%20SP)|',
    ]
    sp_delegations = ''.join(sp_delegation_list)

    community_url = 'https://steemit.com/created/hive-161179'
    trail_url = 'https://tinyurl.com/curation-trail'
    trail_info = 'https://steemit.com/'
    trail_info += '@japansteemit/steem-japan-how-to-follow-curation-trail'

    main_image = data['main_image']

    total_posts = data['total_posts']
    total_comments = data['total_comments']
    total_votes = data['total_votes']

    stats_table = f"""
| Avatar | Member | STEEM, SBD, SP | Post, Cmt, Vote | Power⬇️ |
| --- | --- | --- | --- | --- |
|**Total**| | |**{total_posts}**, **{total_comments}**, **{total_votes}**|%|
    """

    # Sort stats by post count
    post_count = {}
    for d in data['stats']:
        post = len(data['stats'][d]['posts'])
        post_count[d] = post

    sorted_by_posts = dict(sorted(post_count.items(),
                                  key=lambda item: item[1],
                                  reverse=True))

    for member in sorted_by_posts:
        avatar = \
            f"<img src='https://steemitimages.com/u/{member}/avatar/small'>"
        post = len(data['stats'][member]['posts'])
        comment = data['stats'][member]['comments']
        vote = data['stats'][member]['votes']
        steem = data['stats'][member]['steem']
        sbd = data['stats'][member]['sbd']
        sp = data['stats'][member]['sp']
        power_down = data['stats'][member]['power_down']
        star = data['stats'][member]['star']

        stats_table += \
            f"|{avatar}|{member} {star}|{steem}, {sbd}, {sp}\
            |{post}, {comment}, {vote}|{power_down}%|\n"

    urltoimage = ''
    if data['news']['urlToImage']:
        urltoimage = f"<img src='{data['news']['urlToImage']}'> <br/>"

    description = ''
    if data['news']['description']:
        description = f"{data['news']['description']} <br/>"

    content = ''
    if data['news']['content']:
        content = f"{data['news']['content']} <br/>"

    body = f"""
![]({main_image['url']})
[source]({main_image['src']})

#### まずは今日のNewsAPIから ({data['news']['topic']}) <br/>
{data['news']['title']} <br/>
{urltoimage}
{description}
{content}
[続きはこちら]({data['news']['url']})

<center>
[![](https://i.imgur.com/UJIIIWO.png)](https://steemlogin.com/sign/account-witness-vote?witness=tomoyan.witness&approve=1)
[![](https://i.imgur.com/AmarQ5N.png)](https://tinyurl.com/twitter-tomoyan)
</center>

---
<center>
**Steemitの仕組みや使い方などを日本語で説明しています。**
[![](https://i.imgur.com/jT2loCz.png)](https://tinyurl.com/steemit-guide)
</center>

#### [Steem Japan]({community_url}) 毎日の活動状況 (24H)
コミュニティーに記事を投稿しているメンバーのアクティビティです。
コミュニティーページへ投稿数、コメント数、アップボート回数など、コミュニティー貢献度をリスト化。

* 投稿数合計: {data['total_posts']}
* コメント数合計: {data['total_comments']}
* アップボート数合計: {data['total_votes']}

{stats_table}

---

**キュレーショントレールをフォローしよう！👇**
{trail_url}
[![](https://i.imgur.com/0wVb3qI.png)]({trail_url})
フォローの仕方 👇:
{trail_info}

**@japansteemitにSPをデレゲーションしよう！**
| Click | And | Delegate | SP | Here 👇 |
| --- | --- | --- | --- | --- |
{sp_delegations}

<center>
[![](https://i.imgur.com/Fk8AhOW.png)](https://discord.gg/pE5fuktSAt)
</center>
    """

    return body


def publish_post(post_body):
    today = datetime.utcnow().strftime("%Y-%m-%d")

    title = f'Steem Japan: コミュティーレポート {today}'
    tags = ['hive-161179', 'steem', 'japan', 'community', 'stats', 'krsuccess']
    body = post_body

    STEEM.post(
        author=USERNAME,
        title=title,
        body=body,
        tags=tags,
        self_vote=True)


if __name__ == '__main__':
    main()
