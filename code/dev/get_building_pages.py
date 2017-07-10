# -*- coding: utf-8 -*-
"""
Created on Fri Sep 23 20:56:02 2016

@author: ran
"""

import urllib2
import re
from bs4 import BeautifulSoup
import os
import sys
import glob
import urlparse
import time
import pandas as pd
import datetime
from progressbar import Bar, ETA, Percentage, ProgressBar, RotatingMarker, Timer

s = datetime.datetime.now().strftime("%Y-%m-%d")

domain = 'http://streeteasy.com/'

working_dir = '/Users/ran/Dropbox/streeteasy_webscrape'
parser = 'lxml'


listing_url_files = glob.glob(os.path.join(working_dir, '*_all_listings_url.txt'))
print 'Found url files:\n', '\n'.join(listing_url_files)

latest_url_file = max(listing_url_files)
print 'using latest', latest_url_file

with open(latest_url_file) as f:
    url_list = f.readlines()
url_list =[x for x in url_list if 'http://streeteasy.com/building/' in x]

get_bldg = re.compile(r'(http://streeteasy.com/building/.*)/')

bldg_list = [get_bldg.search(x).group(1) for x in url_list]

print 'no. of entries:', len(bldg_list)

bldg_list = list(set(bldg_list))

print 'no. of unique buildings:', len(bldg_list)

sample_list = ['http://streeteasy.com/building/murray-hill-terrace',
               'http://streeteasy.com/building/devonshire-house',
               'http://streeteasy.com/building/7-harrison-street-new_york',
               'http://streeteasy.com/building/714-madison-street-brooklyn']

bldg_folder = os.path.join(working_dir, '{}_bldgs'.format(s))
if not os.path.isdir(bldg_folder):
    os.makedirs(bldg_folder)

# !/usr/bin/env python
from contextlib import closing
from selenium import webdriver
# use firefox to get page with javascript generated content

resume_download = True

widgets = ['Getting building pages', ': ', Percentage(), ' ', Bar(), ' ', ETA()]
pbar = ProgressBar(widgets=widgets, maxval=len(bldg_list)).start()
counter = 0
# file_list = []
# for bldg in sample_list[0:1]:
for bldg in bldg_list:
    # page = urllib2.urlopen(bldg).read()
    # soup = BeautifulSoup(page, parser)
    counter +=1
    pbar.update(counter)

    for i in [1, 2, 3]:
        bldg_url = bldg + '#tab_building_detail={}'.format(i)

        page_filename = os.path.join(bldg_folder, os.path.relpath(bldg_url, domain).replace('/', '_') + '.html')

        if os.path.exists(page_filename) and resume_download:
            # file_list.append(page_filename)
            continue

        if 0:
            page_tab = urllib2.urlopen(bldg_url).read()  # didn't work properly
        else:
            with closing(webdriver.PhantomJS()) as browser:
                browser.get(bldg_url)
                page_tab = browser.page_source

        with open(page_filename, 'w') as p:
            if type(page_tab) is unicode:
                p.write(page_tab.encode('ascii', errors='ignore'))
            else:
                p.write(page_tab)

        # file_list.append(page_filename)

pbar.finish()
