# -- coding: utf-8 --
import requests
import re
import string
import operator
import unicodedata
import urllib2

import pdb
import json 
from BeautifulSoup import BeautifulSoup
from py_bing_search import PyBingSearch
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
import time, timeit

def cleanString(someUnicodeString):
    return ''.join([i if ord(i) < 128 else ' ' for i in someUnicodeString])
def cleanStringArray(someStringArray):
    newArray=[]
    for each in someStringArray:
          newArray.append(str(unicode(each).encode('utf-8')))
    return newArray

def summary(someText, numWords):
    print "\nCalling summary"
    start = timeit.default_timer()
    p = ''.join([i if ord(i) < 128 else ' ' for i in someText])

    sentenceEnders = re.compile('.*?[\?|\.|\!]')
    result = sentenceEnders.findall(p)

    n = len(result)
    Matrix = [[0 for x in range(n)] for x in range(n)]
    Sum = [0 for x in range(n)]

    for i in range(0, n):
        for j in range(0, n):
            if i != j:
                s1 = set(result[i].split(" "))
                s2 = set(result[j].split(" "))
                Matrix[i][j] = len(s1.intersection(s2))
            Sum[i] = Sum[i] + Matrix[i][j]
    TempSum = Sum

    count = 0
    file = open('summaryResults.txt', 'w')

    for y in range(0, 9):
        max_index, max_value = max(enumerate(Sum), key=operator.itemgetter(1))

        n = len(result[max_index].split(" "))

        count = count + n
        if count < numWords:
            file.write(result[max_index])
        else:
            break

        Sum[max_index] = 0
    file.close
    file = open('summaryResults.txt', 'r')
    s= file.read()
    stop = timeit.default_timer()


    print "\nClosing summary. The Runtime of summary was:", stop - start ,"seconds"
    return s
   
def bingSearch(link, limit=4):
    #Sanitize input
    try:
	    linkfile = link.replace("^", "|")
	    bing=PyBingSearch('MsYC/eW39AiaY9EYFIC8mlX8C7HPRRooagMKRwVZx7Q')
	    try: result_list, next_uri = bing.search(linkfile, limit, format='json')
	    except: result_list, next_uri = bing.search(linkfile.replace(" news", ""), limit, format='json')
	    returning=[]
	    for i in xrange(limit):
		 try: returning.append(result_list[i].url.encode('utf8'))
		 except: break
	    return returning
    except: return [link.replace(" news", "")]

#Returns news as a list of tuples of url and title
def bingNews(query, limit=5, offset=0, format='json'):
    query= cleanString(query)
    query=query.replace(" ", "+")
    print query
    QUERY_URL = 'https://api.datamarket.azure.com/Bing/Search/News' \
                 + '?Query={}&$top={}&$skip={}&$format={}'
    url=QUERY_URL.format(urllib2.quote("'{}'".format(query)), limit, offset, format)
    r = requests.get(url, auth=("", 'MsYC/eW39AiaY9EYFIC8mlX8C7HPRRooagMKRwVZx7Q'))
    json_results = r.json()
    returning=[]
    for each in json_results['d']['results']:
         returning.append((each["Url"].encode('utf-8'),each["Title"].encode('utf-8')))
    return returning


