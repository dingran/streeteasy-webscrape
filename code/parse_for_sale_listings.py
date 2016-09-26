import urllib2
import re
from bs4 import BeautifulSoup
import os
import urlparse
import sys
import glob
import time
import pandas as pd
import datetime
from progressbar import Bar, ETA, Percentage, ProgressBar, RotatingMarker, Timer

s = datetime.datetime.now().strftime("%Y-%m-%d")

domain = 'http://streeteasy.com/'

working_dir = '/Users/ran/Dropbox/streeteasy_webscrape'
parser = 'lxml'
output_file = os.path.join(working_dir, '{}_output_df.csv'.format(s))

# url_list = [
#     'http://streeteasy.com/building/murray-hill-terrace/11e',
#     'http://streeteasy.com/building/110-east-36-street-new_york/9f?featured=1',
#     #    'http://streeteasy.com/building/92-warren-street-new_york/34w?featured=1',
#     #    'http://streeteasy.com/building/the-yard/3de?featured=1',
#     #    'http://streeteasy.com/building/245-east-50-street-new_york/7b?featured=1',
#     #    'http://streeteasy.com/building/555-washington-avenue-brooklyn/3c',
#     #    'http://streeteasy.com/building/88-morningside/8b',
#     #    'http://streeteasy.com/building/252-east-57th-st-new_york/43a',
#     #    'http://streeteasy.com/building/the-industry/1j',
#     #    'http://streeteasy.com/building/murray-hill-terrace/11e',
#     #    'http://streeteasy.com/building/devonshire-house/4b',
#     #    'http://streeteasy.com/building/7-harrison-street-new_york/7n',
#     #    'http://streeteasy.com/building/714-madison-street-brooklyn/1',
#     #    'http://streeteasy.com/building/the-churchill/11g',
#     #    'http://streeteasy.com/building/plaza-hotel/1238',
#     #    'http://streeteasy.com/building/324-twenty/2w',
#     #    'http://streeteasy.com/building/324-twenty/2e',
#     #    'http://streeteasy.com/building/the-noma/20a?featured=1',
#     #    'http://streeteasy.com/building/221-west-77-street-new_york/8w?featured=1',
#     #    'http://streeteasy.com/building/555-washington-avenue-brooklyn/3c',
#     #    'http://streeteasy.com/building/88-morningside/8b',
#     #    'http://streeteasy.com/building/252-east-57th-st-new_york/43a',
#     #    'http://streeteasy.com/building/the-industry/1j',
#     #    'http://streeteasy.com/building/murray-hill-terrace/11e',
#     #    'http://streeteasy.com/building/devonshire-house/4b',
#     #    'http://streeteasy.com/building/7-harrison-street-new_york/7n'
# ]

listing_url_files = glob.glob(os.path.join(working_dir, '*_all_listings_url.txt'))
print 'Found url files:\n', '\n'.join(listing_url_files)

latest_url_file = max(listing_url_files)
print 'using latest', latest_url_file

with open(latest_url_file) as f:
    url_list = f.readlines()
url_list = [u.strip('\n') for u in url_list]

download_pages_only = False
resume_download = False  # False means start over, and overwrite

use_local_files = True
page_store_folder_to_use = os.path.join(working_dir, '2016-09-23_page_storage')
if use_local_files and os.path.isdir(page_store_folder_to_use) and not download_pages_only:
    use_local_files = True
else:
    use_local_files = False

page_store_folder = os.path.join(working_dir, '{}_page_storage'.format(s))
if use_local_files:
    file_list = os.listdir(page_store_folder_to_use)
    file_list.remove('.DS_Store')
    file_list = [os.path.join(page_store_folder_to_use, x) for x in file_list]
    page_list = file_list
else:
    # file_list = []
    page_list = url_list
    if not os.path.isdir(page_store_folder):
        os.makedirs(page_store_folder)

info_list = []
widgets = ['Parsing files', ': ', Percentage(), ' ', Bar(), ' ', ETA()]
pbar = ProgressBar(widgets=widgets, maxval=len(page_list)).start()
counter = 0
for u in page_list:
    counter += 1
    pbar.update(counter)

    if 'sale' in u and 'building' not in u:
        print 'abnormal link', u
        continue

    if use_local_files:
        with open(u, 'r') as f:
            page = f.read()

    else:
        page_filename = os.path.join(page_store_folder, os.path.relpath(u, domain).replace('/', '_') + '.txt')

        if os.path.exists(page_filename) and download_pages_only and resume_download:
            # file_list.append(page_filename)
            continue

        page = urllib2.urlopen(u).read()

        with open(page_filename, 'w') as p:
            p.write(page)
            # file_list.append(page_filename)

    if not download_pages_only:

        soup = BeautifulSoup(page, parser)

        info = dict()

        main_info = soup.find(class_='main-info')

        address = main_info.h1.a.string

        try:
            sep_address = re.compile(r'(.*)#(.*)')
            addr = sep_address.search(address)
            street_addr = addr.group(1).strip()
            apt_number = addr.group(2)
            info['street_address'] = street_addr
            info['apt_number'] = apt_number
        except:
            info['street_address'] = address

        price_section = main_info.find(class_='price')
        find_price = re.compile(r'\$([\d,]+)')
        price = int(str(find_price.search(price_section.get_text()).group(1)).replace(',', ''))
        info['price'] = price

        main_info_details = main_info.find_all(class_='details_info')

        try:
            area_info = main_info_details[0].contents
            get_number = re.compile(r'[0-9,]+')
            info['area'] = int(get_number.search(area_info[0].get_text()).group().replace(',', ''))
        except:
            pass

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

        
        aa=re.compile('(.*) in (.*)')        
        info['type'] = aa.search(main_info_details[1].get_text().replace('\n', ' ').strip()).group(1)
        info['neighborhood'] = aa.search(main_info_details[1].get_text().replace('\n', ' ').strip()).group(2)

        vitals = soup.find(class_='vitals top_spacer')
        try:
            monthly_charges = re.compile(r'\$([\d,]+)')
            mc = monthly_charges.findall(vitals.find('h6', string='Monthly Charges').parent.get_text())
            total_mc = [int(x.replace(',', '')) for x in mc]
            info['monthly_charge'] = sum(total_mc)
        except:
            pass

        dom = re.compile(r'([\d]+) day')
        info['days_on_market'] = int(
            dom.search(vitals.find('h6', string=re.compile('Days')).parent.get_text()).group(1))

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

        # building_info('div')[3].get_text()
        # Out[136]: u'12 unitsBuilt in 1920'
        cc = re.compile(r'(\d+) unit')
        cc_result = cc.search(building_info('div')[3].get_text())
        if cc_result:
            info['n_units'] = cc_result.group(1)

        cc = re.compile(r'Built in (\d+)')
        cc_result = cc.search(building_info('div')[3].get_text())
        if cc_result:
            info['built_year'] = cc_result.group(1)

        # building_info('span', class_='subtitle')[0].parent.get_text()
        # Out[98]: u'\n\n 92 Warren Street\n\n        \xa0New York, NY 10007\n      '
        bb = re.compile(r'([A-Z][A-Z]).*(\d\d\d\d\d)')
        try:
            info['zipcode'] = bb.search(building_info('span', class_='subtitle')[0].parent.get_text()).group(2)
        except:
            pass

        info_list.append(info)
pbar.finish()

if not download_pages_only:
    info_df = pd.DataFrame(info_list)
    print info_df
    info_df.to_csv(output_file)
else:
    print len(page_list)
    print len(os.listdir(page_store_folder)) - 1
    print counter
