#!/usr/bin/env python
import json
import re
import urllib
from urllib2 import Request, urlopen, URLError, HTTPError

from utilities import get_url

TITLES_URL = 'http://trove.nla.gov.au/ndp/del/titleList'
TITLE_HOLDINGS_URL = 'http://trove.nla.gov.au/ndp/del/yearsAndMonthsForTitle/'
YAHOO_ID = 'JAp9z33V34HzR4rvRaHUNsRuEadGdaoQlRWYwsObAM1YquTZ.m92jjrhx.X0mOro67op'
YAHOO_URL = 'http://wherein.yahooapis.com/v1/document'

def get_titles(locate=False):
    '''
    Retrieves a list of current newspaper titles from Trove.
    Retrieves current holdings details about each title.
    Saves details of newspapers with holdings to a list.
    Returns a list of dictionaries with the following fields:
    name, id, state, start_year, start_month, end_year, end_month.
    '''
    title_list = json.load(get_url(TITLES_URL))
    titles = []
    for title in title_list:
        name = title['name']
        print unicode(name).encode('utf-8')
        try:
            place, state = re.search(r'\(([a-zA-Z \.]+, )*?(National|ACT|NSW|NT|Qld|QLD|SA|Tas|TAS|Vic|VIC|WA)\.*?', 
                              name).groups()
        except AttributeError:
            place = None
            state = 'national'
        if locate and place is None and state is not 'national':
            locate_title(name)       
        url = '%s%s' % (TITLE_HOLDINGS_URL, title['id'])
        holdings = json.load(get_url(url))
        #Only save those who have holdings online
        if len(holdings) > 0:
            titles.append({'name': name,
                               'id': title['id'],
                               'state': state,
                               'start_year': holdings[0]['y'],
                               'start_month': holdings[0]['m'],
                               'end_year': holdings[-1]['y'],
                               'end_month': holdings[-1]['m'],
                               })
    return titles

def locate_title(title):
    '''
    Attempt to extract placenames from newspaper titles.
    '''
    values = {'appid': YAHOO_ID, 'documentType': 'text/plain', 'documentContent': unicode(title).encode('utf-8') + ' Australia', 'outputType': 'json'}
    data = urllib.urlencode(values)
    req = Request(YAHOO_URL, data)
    response = urlopen(req)
    place_data = json.load(response)
    print place_data
    if isinstance(place_data['document']['localScopes'], list):
        for scope in place_data['document']['localScopes']:
            print scope['localScope']['name']
    else:
        print place_data['document']['localScopes']['localScope']['name']
    try:
        print place_data['document']['placeDetails']['place']['name']
    except KeyError:
        print "No place"
    