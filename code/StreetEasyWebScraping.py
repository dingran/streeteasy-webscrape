from __future__ import print_function
import os
import re
import sys
import glob
import time
import random
from bs4 import BeautifulSoup
import urlparse
import logging
# from progressbar import Bar, ETA, Percentage, ProgressBar, RotatingMarker, Timer
from random import shuffle
from tqdm import tqdm

import colorama
import datetime
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException

pd.set_option('display.max_colwidth', -1)
pd.set_option('display.colheader_justify', 'left')
colorama.init()


def random_pause():
    if random.random() < 0.01:
        set_pause(5)
    elif random.random() < 0.05:
        set_pause(4)
    elif random.random() < 0.1:
        set_pause(3)
    elif random.random() < .9:
        set_pause(2)
    else:
        set_pause(1)


def log_time(kind='general', color_str=None):
    if color_str is None:
        if kind == 'error' or kind.startswith('e'):
            color_str = colorama.Fore.RED
        elif kind == 'info' or kind.startswith('i'):
            color_str = colorama.Fore.YELLOW
        elif kind == 'overwrite' or kind.startswith('o'):
            color_str = colorama.Fore.MAGENTA
        elif kind == 'write' or kind.startswith('w'):
            color_str = colorama.Fore.CYAN
        elif kind == 'highlight' or kind.startswith('h'):
            color_str = colorama.Fore.GREEN
        else:
            color_str = colorama.Fore.WHITE

    print(color_str + str(datetime.datetime.now()) + colorama.Fore.RESET, end=' ')


def calc_pause(base_seconds=3., variable_seconds=5.):
    return base_seconds + random.random() * variable_seconds


def set_pause(kind=1, t=None, t_limit=55):
    log_time('info')
    if t is not None:
        kind_str = 'specific'
    else:
        if kind == 5:
            kind_str = 'ultra long'
            t = calc_pause(base_seconds=1000, variable_seconds=1000)
        elif kind == 4:
            kind_str = 'very long'
            t = calc_pause(base_seconds=100, variable_seconds=100)
        elif kind == 3:
            kind_str = 'long'
            t = calc_pause(base_seconds=10, variable_seconds=10)
        elif kind == 2:
            kind_str = 'short'
            t = calc_pause(base_seconds=3., variable_seconds=3.)
        else:
            kind_str = 'very short'
            t = calc_pause(base_seconds=0.5, variable_seconds=0.5)

    print('{} pause: {}s...'.format(kind_str, t))

    if t_limit is None:
        t_limit = 0
    time.sleep(min(t, t_limit))


def init_driver(driver_type='Chrome'):
    log_time('info')
    print('initiating driver: {}'.format(driver_type))
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
    print('closing driver...')
    dr.quit()


def load_url(driver=None, url=None, n_attempts_limit=3):
    """
    page loader with n_attempts
    :param driver: 
    :param url: 
    :param n_attempts_limit: 
    :return: 
    """
    n_attempts = 0
    page_loaded = False
    while n_attempts < n_attempts_limit and not page_loaded:
        try:
            driver.get(url)
            page_loaded = True
            log_time()
            print('page loaded successfully: {}'.format(url))
        except TimeoutException:
            n_attempts += 1
            log_time('error')
            print('loading page timeout', url, 'attempt {}'.format(n_attempts))
            set_pause(1)
        except:
            n_attempts += 1
            log_time('error')
            print('loading page unknown error', url, 'attempt {}'.format(n_attempts))
            set_pause(1)

    if n_attempts == n_attempts_limit:
        driver.quit()
        log_time('error')
        print('loading page failed after {} attempts, now give up:'.format(n_attempts_limit), url)
        return False

    return True


def print_sep():
    print(50 * '*')


class StreetEasyWebScraping:
    def __init__(self, output_folder=None):
        if not output_folder:
            output_folder = '/Users/dingran/github/streeteasy-webscrape/output'

        self.output_folder = output_folder
        folder_list = [self.output_folder]

        self.domain = 'http://streeteasy.com/'
        self.parser = 'lxml'
        self.time_string = datetime.datetime.now().strftime("%Y-%m-%d")
        # self.time_string = '2016-09-26'

        self.active_listing_search_condition_string = {'active_sales': 'for-sale/nyc/type:D1',  # ,P1',
                                                       'active_rentals': 'for-rent/nyc/type:D1',  # ,P1'
                                                       }
        # for-sale in NYC, condo (D1) and coop (P1)

        keys = ['active_sales', 'active_rentals', 'past_sales', 'past_rentals']

        d = dict()
        for k in keys:
            d[k] = '*_{}_url.txt'.format(k)
        self.url_list_fname_template = d

        d = dict()
        for k in keys:
            d[k] = os.path.join(self.output_folder,
                                self.url_list_fname_template[k].replace('*', '{}').format(self.time_string))
        self.url_list_fname = d

        d = dict()
        for k in keys:
            d[k] = '*_{}_df.csv'.format(k)
        self.listing_analysis_result_fname_template = d

        d = dict()
        for k in keys:
            d[k] = os.path.join(self.output_folder, self.listing_analysis_result_fname_template[k].
                                replace('*', '{}').format(self.time_string))
        self.listing_analysis_result_fname = d

        d = dict()
        for k in keys:
            d[k] = -1
        self.n_listings = d

        d = dict()
        for k in keys:
            d[k] = '*_{}_page_storage'.format(k)
        self.listing_page_storage_foldername_template = d

        d = dict()
        for k in keys:
            d[k] = os.path.join(self.output_folder, self.listing_page_storage_foldername_template[k].
                                replace('*', '{}').format(self.time_string))
        self.listing_page_storage_foldername = d

        folder_list.extend(self.listing_page_storage_foldername.values())

        self.building_page_storage_foldername_template = '*_building_page_storage'
        self.building_page_storage_foldername = \
            os.path.join(self.output_folder, self.building_page_storage_foldername_template.replace('*',
                                                                                                    '{}').format(
                self.time_string))
        folder_list.append(self.building_page_storage_foldername)

        d = dict()
        for k in keys:
            d[k] = []
        self.url_list = d
        self.building_url_list = []

        print(folder_list)
        for folder in folder_list:
            if not os.path.isdir(folder):
                print('initializing, creating folder {}'.format(folder))
                os.makedirs(folder)

    def __str__(self):
        s = str(pd.Series(self.__dict__))
        # s = ''
        # for key, item in self.__dict__.items():
        #     s += '{}:\t\t{}\n'.format(str(key), str(item))
        return s

    def pull_active_listing(self, listing_type='active_sales', overwrite=True):
        func_name = 'pull_active_listing'

        if 'sale' in listing_type:
            listing_type = 'active_sales'
        else:
            listing_type = 'active_rentals'

        print_sep()
        print('{}: listing_type == {}'.format(func_name, listing_type))

        top_url = urlparse.urljoin(self.domain, self.active_listing_search_condition_string[listing_type])
        print('{}: opening {}'.format(func_name, top_url))

        # top_page = urllib2.urlopen(top_url).read()

        driver = init_driver()
        load_url(driver, top_url)
        top_page = driver.page_source

        # with closing(webdriver.Chrome()) as browser:
        #     browser.get(top_url)
        #     top_page = browser.page_source
        #     print top_page
        #
        #     with open('debug.html', 'w') as p:
        #         if type(top_page) is unicode:
        #             p.write(top_page.encode('ascii', errors='ignore'))
        #         else:
        #             p.write(top_page)
        soup_tp = BeautifulSoup(top_page, 'lxml')

        result_count = int(soup_tp.find(class_='result-count first').get_text().replace(',', ''))
        self.n_listings[listing_type] = result_count
        print('{}: {} results'.format(func_name, result_count))

        page_count = int(soup_tp.find(class_='pagination').find_all('a')[-2].get_text())
        self.n_listings[listing_type] = page_count
        print('{}: {} pages'.format(func_name, page_count))

        if not overwrite:
            if os.path.exists(self.url_list_fname[listing_type]):
                print('{}: output file exist and overwrite=False, returning...'.format(func_name))
                return

        list_of_links = []
        print('pull_active_listing')
        for i in tqdm(range(1, page_count + 1)):
            # for i in range(1, 3):

            page_url = top_url + '?page={}&sort_by=listed_desc'.format(i)

            # print page_url
            # time.sleep(5)
            # list_page = urllib2.urlopen(page_url).read()

            random_pause()
            load_url(driver, page_url)
            list_page = driver.page_source

            soup_list_page = BeautifulSoup(list_page, self.parser)
            entries = soup_list_page.find(class_='item-rows').find_all(name='div', class_='item')

            for e in entries:
                href = e.find(class_='details-title').find('a').attrs['href']
                # print href
                list_of_links.append(urlparse.urljoin(self.domain, href))
                # print i, len(list_of_links), len(set(list_of_links))
        quit_driver(driver)

        # print len(set(list_of_links))

        self.url_list[listing_type] = list_of_links
        print('{}: done, writing output file {}'.format(func_name, self.url_list_fname[listing_type]))
        with open(self.url_list_fname[listing_type], 'w') as f:
            f.write('\n'.join(list_of_links))

    def find_latest_file_or_folder(self, template):
        func_name = 'find_latest_file_or_folder (template=={})'.format(template)
        items = glob.glob(os.path.join(self.output_folder, template))
        print('{}: found {} files:\n'.format(func_name, len(items)), '\n'.join(items))
        if items:
            latest_item = max(items)
            print('{}: using latest {}'.format(func_name, latest_item))
            return latest_item
        else:
            return None

    def update_active_listing_url_list(self):
        for listing_type in ['active_sales', 'active_rentals']:
            latest_url_file = self.find_latest_file_or_folder(self.url_list_fname_template[listing_type])
            if latest_url_file is not None:
                with open(latest_url_file) as f:
                    url_list = f.readlines()
                url_list = [u.strip('\n') for u in url_list]
                self.url_list[listing_type] = url_list

    def update_building_url_list(self):
        func_name = 'update_building_url_list'
        print_sep()
        if not self.url_list['active_sales'] or not self.url_list['active_rentals']:
            self.update_active_listing_url_list()

        url_list = self.url_list['active_sales'] + self.url_list['active_rentals']
        url_list = [u for u in url_list if ('sale' not in u) and ('rental' not in u)]

        if url_list:  # not empty
            url_list = [x for x in url_list if 'http://streeteasy.com/building/' in x]

            get_bldg = re.compile(r'(http://streeteasy.com/building/.*)/')

            bldg_list = [get_bldg.search(x).group(1) for x in url_list]

            print('{}: detected {} building entries, {} unique buildings'.format(func_name, len(bldg_list),
                                                                                 len(set(bldg_list))))

            bldg_list = list(set(bldg_list))

            bldg_list_extended = []
            for i in [2, 3]:
                bldg_list_extended.extend([x + '#tab_building_detail={}'.format(i) for x in bldg_list])
            self.building_url_list = bldg_list_extended
            print('{}: length of extended building url list is {}'.format(func_name, len(bldg_list_extended)))
        else:
            print('{}: no active listing url list available, abort'.format(func_name))

    def url_to_basefname_transformation(self, url=None, fname=None, method='new'):
        forward = True
        if (url is not None) and (fname is not None):
            print('cannot figure out translation direction')
            assert 0
        elif (url is None) and (fname is None):
            print('both inputs are None')
            assert 0
        elif url is not None:
            forward = True
        elif fname is not None:
            forward = False

        if forward:  # translate from url to fnanme
            if method.startswith('n'):
                fname_output = os.path.relpath(url, self.domain).replace('/', ']]]')
            else:
                assert 0
                # fname_output = os.path.relpath(url, self.domain).replace('/', '_')
            if not fname_output.endswith('.html'):
                fname_output += '.html'
            return fname_output
        else:
            basefname = os.path.basename(fname)
            if method.startswith('n'):
                assert ']]]' in basefname
                url = urlparse.urljoin(self.domain, basefname.replace(']]]', '/'))
                if url.endswith('.html'):
                    url = url[:-5]
            else:
                assert 0  # cann't translate back
            return url

    def download_pages(self, url_list, output_folder, method='direct', overwrite=False):
        shuffle(url_list)

        func_name = 'download_pages (output_folder=={}, method=={})'.format(output_folder, method)
        print_sep()
        print(func_name)

        file_skipped = []
        file_added = []

        driver = init_driver()
        print('Downloading files')
        for u in tqdm(url_list):
            # page_filename_old = os.path.join(output_folder, self.url_to_basefname_transformation(url=u, method='old'))
            page_filename = os.path.join(output_folder, self.url_to_basefname_transformation(url=u, method='new'))

            # if os.path.exists(page_filename_old):
            #     shutil.move(page_filename_old, page_filename)
            #     print 'renamed file {} to {}'.format(page_filename_old, page_filename)

            if os.path.exists(page_filename) and not overwrite:
                # print page_filename
                file_skipped.append(page_filename)
                continue

            try:
                random_pause()
                load_url(driver, u)
                page = driver.page_source
            except:
                page = ''
                log_time('error')
                print('failed to load {}'.format(u))

            file_added.append(page_filename)

            if sys.version_info[0] == 2:
                with open(page_filename, 'w') as p:
                    if type(page) is unicode:
                        p.write(page.encode('ascii', errors='ignore'))
                    else:
                        p.write(page)
            else:
                with open(page_filename, 'w', encoding='utf-8') as p:
                    p.write(page)

        quit_driver(driver)

        return {'file_added': file_added, 'file_skipped': file_skipped}

    def download_listing_pages(self, listing_type='active_sales', overwrite=False):
        assert self.url_list[listing_type]  # not empty
        result = self.download_pages(self.url_list[listing_type],
                                     self.listing_page_storage_foldername[listing_type],
                                     overwrite=overwrite)
        print(
            'download active listing pages: added {} files, skipped {} files'.format(len(result['file_added']),
                                                                                     len(result['file_skipped'])))

    def download_building_pages(self, overwrite=False, enable_pbar=True):
        assert self.building_url_list  # not empty

        result = self.download_pages(self.building_url_list,
                                     self.building_page_storage_foldername,
                                     method='s',
                                     overwrite=overwrite)
        print('download building pages: added {} files, skipped {} files'.format(len(result['file_added']),
                                                                                 len(result['file_skipped'])))

    def parse_building_page(self, overwrite=True):
        func_name = 'parse_building_page'
        print_sep()
        print(func_name)

        latest_building_page_folder = self.find_latest_file_or_folder(self.building_page_storage_foldername_template)

        file_list = os.listdir(latest_building_page_folder)
        if '.DS_Store' in file_list:
            file_list.remove('.DS_Store')

        keys = ['past_sales', 'past_rentals']

        file_list_to_use = dict()
        file_list_to_use[keys[0]] = [x for x in file_list if 'detail=2' in x]
        file_list_to_use[keys[1]] = [x for x in file_list if 'detail=3' in x]

        for listing_type in keys:
            output_fname = self.url_list_fname[listing_type]
            if not overwrite and os.path.exists(output_fname):
                print('output file exists, and not overwriting, returning...')
                return

            f_list = file_list_to_use[listing_type]
            print(func_name)
            for f in tqdm(f_list):
                f_path = os.path.join(latest_building_page_folder, f)

                with open(f_path, 'r') as fi:
                    page = fi.read()

                soup = BeautifulSoup(page, 'lxml')

                tables = soup(id='past_transactions_table')

                if tables:
                    table = tables[0]
                else:  # not past transactions
                    continue

                entries = table('tr', class_='activity item')

                parser = re.compile(r'(\d\d/\d\d/\d\d\d\d)\s+#(\w+).*\$([\d,]+)\s+Sold.*(\d) bed.*(\d) bath')
                for e in entries:
                    s = e.get_text().replace('\n', ' ').strip()
                    result = parser.search(s)
                    if result is not None:
                        for i in range(1, parser.groups + 1):
                            pass
                            # print result.group(i)
                        self.url_list[listing_type].append(urlparse.urljoin(self.domain, e('a')[0]['href']))

            print('{} ({}): done, writing output file {}'.format(func_name, listing_type, self.url_list_fname[
                listing_type]))
            with open(output_fname, 'w') as f:
                f.write('\n'.join(self.url_list[listing_type]))

    def parse_listing_page(self, listing_type='active_sales', overwrite=True):
        func_name = 'parse_listing_page ({})'.format(listing_type)
        print_sep()
        print(func_name)

        output_fname = self.listing_analysis_result_fname[listing_type]

        if not overwrite and os.path.exists(output_fname):
            print('output file exists, and not overwriting, returning...')
            return

        latest_page_storage_folder = self.find_latest_file_or_folder(
            self.listing_page_storage_foldername_template[listing_type])

        file_list = os.listdir(latest_page_storage_folder)
        if '.DS_Store' in file_list:
            file_list.remove('.DS_Store')
        file_list = [os.path.join(latest_page_storage_folder, x) for x in file_list]

        print('{}: {} pages to parse'.format(func_name, len(file_list)))

        info_list = []
        print(func_name)
        for u in tqdm(file_list):
            if 'active' in listing_type and (('sale' in os.path.basename(u)) or ('rent' in os.path.basename(u))):
                print('abnormal link', u)
                continue

            with open(u, 'r') as f:
                page = f.read()

            soup = BeautifulSoup(page, self.parser)

            info = dict()

            main_info = soup.find(class_='main-info')

            try:
                address = main_info.h1.a.string
            except:
                print(u)
                print(main_info)

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

            aa = re.compile('(.*) in (.*)')
            info['type'] = aa.search(main_info_details[1].get_text().replace('\n', ' ').strip()).group(1)
            info['neighborhood'] = aa.search(main_info_details[1].get_text().replace('\n', ' ').strip()).group(2)

            vitals = soup.find(class_='vitals top_spacer')
            try:
                monthly_charges = re.compile(r'\$([\d,]+)')
                mc = monthly_charges.findall(vitals.find('h6', string='Monthly Charges').parent.get_text())
                total_mc = [int(x.replace(',', '')) for x in mc]
                info['monthly_charge'] = sum(total_mc)
            except:
                url = self.url_to_basefname_transformation(fname=u)
                print(url)
                sys.exit(0)
                pass

            dom = re.compile(r'([\d]+) day')
            try:
                info['days_on_market'] = int(
                    dom.search(vitals.find('h6', string=re.compile('Days')).parent.get_text()).group(1))
            except:
                print(vitals.find('h6', string=re.compile('Days')))
                url = self.url_to_basefname_transformation(fname=u)
                print(url)
                sys.exit(0)
                pass

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

            info['fname'] = u
            try:
                info['url'] = self.url_to_basefname_transformation(fname=u)
            except:
                print(u)
                sys.exit(0)

            info_list.append(info)

        info_df = pd.DataFrame(info_list)
        info_df.to_csv(output_fname)
