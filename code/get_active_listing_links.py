import os
import re
import time
import datetime
import urllib2
from bs4 import BeautifulSoup
import urlparse
from progressbar import Bar, ETA, Percentage, ProgressBar, RotatingMarker, Timer

s = datetime.datetime.now().strftime("%Y-%m-%d")
output_fname = '{}_all_listings_url.txt'.format(s)

domain = 'http://streeteasy.com'
top_url = 'http://streeteasy.com/for-sale/nyc/type:D1,P1'  # condo (D1) and coop (P1)
#top_url = 'http://streeteasy.com/for-sale/nyc/type:D1'

top_page = urllib2.urlopen(top_url).read()
soup_tp = BeautifulSoup(top_page, 'lxml')

result_count = int(soup_tp.find(class_='result-count first').get_text().replace(',', ''))
print result_count, 'results'

page_count = int(soup_tp.find(class_='pagination').find_all('a')[-2].get_text())
print page_count, 'pages'

list_of_links = []
widgets = ['Gathering listings', ': ', Percentage(), ' ', Bar(), ' ', ETA()]
pbar = ProgressBar(widgets=widgets, maxval=page_count).start()
counter = 0
for i in range(1, page_count + 1):
#for i in range(1, 3):
    page_url = top_url + '?page={}&sort_by=listed_desc'.format(i)
    # print page_url
    # time.sleep(5)
    list_page = urllib2.urlopen(page_url).read()
    soup_list_page = BeautifulSoup(list_page, 'lxml')
    entries = soup_list_page.find(class_='item-rows').find_all(name='div', class_='item')

    for e in entries:
        href = e.find(class_='details-title').find('a').attrs['href']
        #print href
        list_of_links.append(urlparse.urljoin(domain, href))
    #print i, len(list_of_links), len(set(list_of_links))
    counter += 1
    pbar.update(counter)
pbar.finish()

#print len(set(list_of_links))


with open(output_fname, 'w') as f:
    f.write('\n'.join(list_of_links))
