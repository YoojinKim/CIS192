from json import loads
from re import search
from urllib.request import urlopen, Request
from heapq import heappush
from collections import defaultdict, Counter
from feed import *
from string import punctuation

class Scraper(object):
    def __init__(self):
        # APP ID
        app = '783412255178688'
        # APP Secret
        secret = '32cdc4b39d029e2fa68916dc0a5bf6bf'
        self.access_token = app + '|' + secret
        self.feeds = defaultdict(lambda: [])
        self.counter = Counter()
        self.scrape_group()

    def tokenize(self, message):
        if message:
            for token in message.split():
                index = len(token)
                for i in range(len(token) - 1, -1, -1):
                    if token[i] not in punctuation:
                        break
                    index -= 1
                token = token[:index]
                yield token.upper()
        else:
            yield ''

    def store(self, message, name, picture, reactions):
        for token in self.tokenize(message):
            heappush(self.feeds[token], Feed(message, name, picture, reactions))
            self.counter[token] += reactions

    def scrape_feed(self, post):
        message = post['message'] if 'message' in post else ''
        name = post['from']['name']
        picture = post['full_picture'] if 'full_picture' in post else ''
        reactions = post['reactions']['summary']['total_count'] if 'reactions' in post else 0
        self.store(message, name, picture, reactions)
        return(message, name, picture, reactions)

    def scrape_group(self, until='', paging=''):
        oupscc = 'https://graph.facebook.com/v2.11/966590693376781'
        feed = '/feed/?limit=100&access_token=' + self.access_token
        feed += '&fields=message,from,name,full_picture,reactions.limit(0).summary(true)'
        while True:
            until = '' if until is '' else '&until=' + until
            paging = '' if until is '' else '&__paging_token=' + paging
            url = oupscc + feed + until + paging
            posts = loads((urlopen(Request(url)).read()))

            for post in posts['data']:
                self.scrape_feed(post)

            if 'paging' in posts and 'next' in posts['paging']:
                npage = posts['paging']['next']
                until = search('until=([0-9]*?)(&|$)', npage).group(1)
                paging = search('__paging_token=(.*?)(&|$)', npage).group(1)
            else:
                return
