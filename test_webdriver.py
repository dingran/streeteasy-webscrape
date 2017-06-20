import numpy as np
import os
import re
import sys
import glob
import time
import shutil
import random
import urllib2
import logging
import urlparse
import platform
import datetime
import pandas as pd
from random import shuffle
from bs4 import BeautifulSoup
from contextlib import closing
from pyvirtualdisplay import Display
from progressbar import Bar, ETA, Percentage, ProgressBar, RotatingMarker, Timer

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import termcolor


def log_time(kind='general', color_str=None):
    if color_str is None:
        if kind == 'error' or kind.startswith('e'):
            color_str = 'red'
        elif kind == 'info' or kind.startswith('i'):
            color_str = 'yellow'
        elif kind == 'overwrite' or kind.startswith('o'):
            color_str = 'magenta'
        elif kind == 'write' or kind.startswith('w'):
            color_str = 'cyan'
        elif kind == 'highlight' or kind.startswith('h'):
            color_str = 'green'
        else:
            color_str = 'white'

    print termcolor.colored(datetime.datetime.now(), color_str),


def init_driver(driver_type='Chrome'):
    log_time('info')
    print 'initiating driver: {}'.format(driver_type)
    if driver_type == 'Chrome':
        dr = webdriver.Chrome()
    elif driver_type.startswith('Pha'):
        dr = webdriver.PhantomJS()
    elif driver_type.startswith('Fi'):
        dr = webdriver.Firefox()
    else:
        assert False
    dr.set_window_size(1920, 600)
    dr.wait = WebDriverWait(dr, 5)
    dr.set_page_load_timeout(25)
    return dr


def quit_driver(dr):
    log_time('info')
    print 'closing driver...'
    dr.quit()


target_url = 'http://streeteasy.com'

driver = init_driver()
driver.get(target_url)
time.sleep(1.02)
top_page = driver.page_source

with open('debug.html', 'w') as p:
    if type(top_page) is unicode:
        p.write(top_page.encode('ascii', errors='ignore'))
    else:
        p.write(top_page)

driver.quit()
