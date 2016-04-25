# coding=utf-8
import logging

import requests

__author__ = 'ilov3'
logger = logging.getLogger(__name__)
FACEBOOK_CLIENT_ID = '105323143198945'
FACEBOOK_CLIENT_SECRET = 'e10beb3dc3a388480927d29493168545'


def get_access_token(client_id, client_secret):
    url = 'https://graph.facebook.com/oauth/access_token'
    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials',

    }
    req = requests.get(url, params=params)
    s = req.text.split('=')
    if (s[0] == 'access_token') and (len(s) == 2):
        return s[1]
    else:
        return None