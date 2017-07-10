# -*- coding: utf-8 -*-
"""
Created on Sat Sep 24 21:21:09 2016

@author: ran
"""

import os


import os
import re
import sys
import glob
import time
import urllib2
import datetime
from bs4 import BeautifulSoup
import urlparse
import logging
import pandas as pd
from progressbar import Bar, ETA, Percentage, ProgressBar, RotatingMarker, Timer
from contextlib import closing
from selenium import webdriver


working_dir = '/Users/ran/Dropbox/streeteasy_webscrape/output/2016-09-24_building_page_storage'

file_list = os.listdir(working_dir)
if '.DS_Store' in file_list:
    file_list.remove('.DS_Store')

keys = ['past_sales', 'past_rentals']

file_list_to_use = dict()
file_list_to_use[keys[0]] = [x for x in file_list if 'detail=2' in x]
file_list_to_use[keys[1]] = [x for x in file_list if 'detail=3' in x]


for k in keys:
    f_list = file_list_to_use[k]
    

    for f in f_list:
        f_path = os.path.join(working_dir, f)
        print f_path
    
        with open(f_path, 'r') as fi:
            page = fi.read()
        
        soup = BeautifulSoup(page, 'lxml')
        
        tables = soup(id='past_transactions_table')

        if tables:
            table= tables[0]
        else:  # not past transactions
            continue
        
        entries = table('tr', class_='activity item')
        
        #parser = re.compile(r'(\d\d/\d\d/\d\d\d\d)\s#(\w+).*\$([\d,]+).*Sold.*(\d) bed.*(\d) bath.*')
        parser = re.compile(r'(\d\d/\d\d/\d\d\d\d)\s+#(\w+).*\$([\d,]+)\s+Sold.*(\d) bed.*(\d) bath')
        for e in entries:
            s= e.get_text().replace('\n', ' ').strip()
            result = parser.search(s)
            if result is not None:
                for i in range(1, parser.groups+1):
                    print result.group(i)
                print e('a')[0]['href']
                sys.exit(0)
            
        
        
    