import random
import requests
import json
import re
from common.header import UA_LIST
from bs4 import BeautifulSoup
ua = {
    'user-agent': random.choice(UA_LIST)
}


def GET(url: str, headers=None):
    if headers is None:
        headers = ua
    try:
        r = requests.get(url=url, headers=headers, timeout=5)
        r.raise_for_status()
        print('Request GET successfully!')
        return BeautifulSoup(r.text, 'lxml')
    except:
        print("Request GET Failed")
