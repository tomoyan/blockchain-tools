import os
from datetime import timedelta


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or '@5b1c-8a23-7875-c70a-302a'
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    UPVOTE_ACCOUNT = os.environ.get('UPVOTE_ACCOUNT') or 'USERNAME'
    UPVOTE_KEY = os.environ.get('UPVOTE_KEY') or 'PRIVATE_POSTING_KEY'
    FB_APIKEY = os.environ.get('FB_APIKEY') or 'FB_APIKEY'
