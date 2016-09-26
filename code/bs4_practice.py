# -*- coding: utf-8 -*-
"""
Created on Wed Sep 21 05:33:56 2016

@author: ran
"""

import urllib2
import re
from bs4 import BeautifulSoup
import os
import urlparse
import time

domain = 'http://streeteasy.com'

# top_url = 'http://streeteasy.com/for-sale/nyc/type:D1,P1'  # condo (D1) and coop (P1)

top_url = 'http://streeteasy.com/for-sale/nyc/type:D1'

top_page = urllib2.urlopen(top_url).read()

soup_tp = BeautifulSoup(top_page)

# %%


result_count = int(soup_tp.find(class_='result-count first').get_text().replace(',', ''))

print result_count, 'results'

page_count = int(soup_tp.find(class_='pagination').find_all('a')[-2].get_text())

print page_count, 'pages'

list_of_links = []
# for i in range(1, page_count+1):
for i in range(0, 3):
    page_url = top_url + '?page={}'.format(i)
    print page_url
    time.sleep(0.1)
    list_page = urllib2.urlopen(top_url).read()
    soup_list_page = BeautifulSoup(list_page)
    entries = soup_list_page.find(class_='item-rows').find_all(name='div', class_='item')

    for e in entries:
        href = e.find(class_='details-title').find('a').attrs['href']
        list_of_links.append(urlparse.urljoin(domain, href))

# %%





# %%

import urllib2
import re
from bs4 import BeautifulSoup
import os
import urlparse
import time
import pandas as pd
import datetime
from progressbar import Bar, ETA, Percentage, ProgressBar, RotatingMarker, Timer


domain = 'http://streeteasy.com/'

working_dir = '/Users/ran/Dropbox/streeteasy_webscrape'
parser = 'lxml'

url_list = [
    'http://streeteasy.com/building/murray-hill-terrace/11e',
    'http://streeteasy.com/building/110-east-36-street-new_york/9f?featured=1',
#    'http://streeteasy.com/building/92-warren-street-new_york/34w?featured=1',
#    'http://streeteasy.com/building/the-yard/3de?featured=1',
#    'http://streeteasy.com/building/245-east-50-street-new_york/7b?featured=1',
#    'http://streeteasy.com/building/555-washington-avenue-brooklyn/3c',
#    'http://streeteasy.com/building/88-morningside/8b',
#    'http://streeteasy.com/building/252-east-57th-st-new_york/43a',
#    'http://streeteasy.com/building/the-industry/1j',
#    'http://streeteasy.com/building/murray-hill-terrace/11e',
#    'http://streeteasy.com/building/devonshire-house/4b',
#    'http://streeteasy.com/building/7-harrison-street-new_york/7n',
#    'http://streeteasy.com/building/714-madison-street-brooklyn/1',
#    'http://streeteasy.com/building/the-churchill/11g',
#    'http://streeteasy.com/building/plaza-hotel/1238',
#    'http://streeteasy.com/building/324-twenty/2w',
#    'http://streeteasy.com/building/324-twenty/2e',
#    'http://streeteasy.com/building/the-noma/20a?featured=1',
#    'http://streeteasy.com/building/221-west-77-street-new_york/8w?featured=1',
#    'http://streeteasy.com/building/555-washington-avenue-brooklyn/3c',
#    'http://streeteasy.com/building/88-morningside/8b',
#    'http://streeteasy.com/building/252-east-57th-st-new_york/43a',
#    'http://streeteasy.com/building/the-industry/1j',
#    'http://streeteasy.com/building/murray-hill-terrace/11e',
#    'http://streeteasy.com/building/devonshire-house/4b',
#    'http://streeteasy.com/building/7-harrison-street-new_york/7n'
]

#with open(os.path.join(working_dir, '2016-09-22_all_listings_url.txt')) as f:
#    url_list = f.readlines()


use_local_files=True
page_store_folder_to_use = os.path.join(working_dir, '2016-09-23_page_storage')

info_list = []

if use_local_files and os.path.isdir(page_store_folder_to_use):
    file_list = os.listdir(page_store_folder_to_use)
    file_list.remove('.DS_Store')
    file_list = [os.path.join(page_store_folder_to_use, x) for x in file_list]
    page_list = file_list
else:
    file_list = []
    page_list = url_list
    s = datetime.datetime.now().strftime("%Y-%m-%d")
    page_store_folder = os.path.join(working_dir, '{}_page_storage'.format(s))

    if not os.path.isdir(page_store_folder):
        os.makedirs(page_store_folder)



for u in page_list:

    if use_local_files:
        with open(u, 'r') as f:
            page = f.read()

    else:
        page = urllib2.urlopen(u).read()
    
        page_filename = os.path.join(page_store_folder, os.path.relpath(u, domain).replace('/', '_')+'.txt')
        with open(page_filename, 'w') as p:
            p.write(page)
        file_list.append(page_filename)
    
    
    soup = BeautifulSoup(page, parser)

    info = dict()

    main_info = soup.find(class_='main-info')

    address = main_info.h1.a.string

    sep_address = re.compile(r'(.*)#(.*)')
    addr = sep_address.search(address)
    street_addr = addr.group(1).strip()
    apt_number = addr.group(2)
    info['street_address'] = street_addr
    info['apt_number'] = apt_number

    price_section = main_info.find(class_='price')
    find_price = re.compile(r'\$([\d,]+)')
    price = int(str(find_price.search(price_section.get_text()).group(1)).replace(',', ''))
    info['price'] = price

    main_info_details = main_info.find_all(class_='details_info')

    area_info = main_info_details[0].contents
    get_number = re.compile(r'[0-9,]+')
    info['area'] = int(get_number.search(area_info[0].get_text()).group().replace(',', ''))
    # info['price_per_sqft'] = int(get_number.search(tmp[1].get_text()).group())
    info['bed'] = 0
    info['bath'] = 0
    for t in area_info[2:]:
        s = t.get_text()
        if 'bed' in s:
            # info['bed'] = s
            info['bed'] = int(get_number.search(s).group())
        if 'bath' in s:
            info['bath'] = int(get_number.search(s).group())

    info['neighborhood'] = main_info_details[1]('span')[-1]('a')[0].get_text()

    vitals = soup.find(class_='vitals top_spacer')
    monthly_charges = re.compile('\$([\d,]+)')
    mc = monthly_charges.findall(vitals.find('h6', string='Monthly Charges').parent.get_text())
    cc = [int(x.replace(',', '')) for x in mc]
    info['monthly_charge'] = sum(cc)

    listing_sections = soup('section', class_='listings_sections')
    description = listing_sections[0]
    highlights = listing_sections[1]
    building_info = listing_sections[2]

    highlights_list = [('pet', 'Cats and Dogs Allowed'),
                       ('elevator', 'Elevator'),
                       ('laundry', 'Laundry'), ('gym', 'Gym'), ('doorman', 'Doorman')]

    for h in highlights_list:
        info[h[0]] = 0
        if highlights.find(string=re.compile(h[1])):
            info[h[0]] = 1

    # building_info('div')[2].get_text()
    # Out[100]: u'\n        Condo in Tribeca '
    aa = re.compile(r'([\w-]+) in (\w+)')
    info['type'] = aa.search(building_info('div')[2].get_text()).group(1)
    # info['neighborhood']=aa.search(building_info('div')[2].get_text()).group(1)

    # building_info('div')[3].get_text()
    # Out[136]: u'12 unitsBuilt in 1920'
    cc = re.compile('(\d+) units.*uilt in (\d+)')
    cc_result = cc.search(building_info('div')[3].get_text())
    info['built_year'] = cc_result.group(2)
    info['n_units'] = cc_result.group(1)

    # building_info('span', class_='subtitle')[0].parent.get_text()
    # Out[98]: u'\n\n 92 Warren Street\n\n        \xa0New York, NY 10007\n      '
    bb = re.compile('([A-Z][A-Z]).*(\d\d\d\d\d)')
    info['zipcode'] = bb.search(building_info('span', class_='subtitle')[0].parent.get_text()).group(2)

    info_list.append(info)

info_df = pd.DataFrame(info_list)

print info_df


#%%

