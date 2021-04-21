import urllib.parse

from functools import reduce
from cloudscraper import create_scraper


API_PATH = "https://api.bitclout.com"


def get_profiles(number=None, next=None):
    json = {}
    client = create_scraper()
    if number: json['NumToFetch'] = number
    if next: json['PublicKeyBase58Check'] = next
    url = reduce(urllib.parse.urljoin, [API_PATH, "get-profiles"])
    return client.post(url, json=json).json()


# https://github.com/HPaulson/BitClout/wiki/Get-the-current-block
def current_block():
    json = {}
    client = create_scraper()
    url = reduce(urllib.parse.urljoin, [API_PATH, "api/v1"])
    return client.get(url, json=json).json()
