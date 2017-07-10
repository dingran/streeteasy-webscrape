# -*- coding: utf-8 -*-
"""
Created on Sat Sep 24 10:50:18 2016

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


bldg_folder = os.path.join(working_dir, '{}_bldgs'.format(s))

fname = os.path.join('building_111-murray-street#tab_building_detail=2.html')

# page =

