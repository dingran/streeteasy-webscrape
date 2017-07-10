# -*- coding: utf-8 -*-
"""
Created on Tue Sep 20 07:50:44 2016

@author: ran
"""

def package_url_sale(page):
    return 'http://streeteasy.com/for-sale/nyc?page=' + page
    
def package_url_rent(page):
    return 'http://streeteasy.com/for-rent/nyc?page=' + page
    
from bs4 import BeautifulSoup
import urllib
import pandas as pd
import pandas as np

price=[]
where=[]
bed=[]
bath=[]
size=[]
monthly=[]
street=[]

for x in range(757,1500): #loop through all pages
    url=package_url_rent(str(x))
    r = urllib.urlopen(url).read()
    soup = BeautifulSoup(r,'html.parser')
    lst = soup.find_all(lambda tag: tag.has_attr('data-id'))
    for i in range(len(lst)):
        #price
        if lst[i].find_all('span',{'class':'price'})==[]:
            price.append('')
        else:
            price.append(lst[i].find_all('span',{'class':'price'})[0].string)
        #where
        length=len(lst[i].find_all('div',{'class':'details_info'}))
        if(lst[i].find_all('div',{'class':'details_info'})[0].find_all('a',href=True)==[]):
            if(length==1):
                where.append('')
            else:
                if(lst[i].find_all('div',{'class':'details_info'})[1].find_all('a',href=True)==[]):
                    where.append('')
                else:
                    where.append(lst[i].find_all('div',{'class':'details_info'})[1].find_all('a',href=True)[0].string)
        else:
            where.append(lst[i].find_all('div',{'class':'details_info'})[0].find_all('a',href=True)[0].string)
        #bedroom
        if(lst[i].find_all('span',{'class':'first_detail_cell'})==[]):
            bed.append('')
        else:
            bed.append(lst[i].find_all('span',{'class':'first_detail_cell'})[0].string)
        #bedroom
        if(lst[i].find_all('span',{'class':'detail_cell'})==[]):
            bath.append('')
        else:
            bath.append(lst[i].find_all('span',{'class':'detail_cell'})[0].string)
        #size
        if(lst[i].find_all('span',{'class':'last_detail_cell'})==[]):
            size.append('')
        else:
            size.append(lst[i].find_all('span',{'class':'last_detail_cell'})[0].string)
        #monthly rent
        #monthly.append(lst[i].find_all('span',{'class':'monthly_payment'})[0].string)
        #street
        street.append(lst[i].find_all('div',{'class':'details-title'})[0].a.string)   
    #print x

print 'done'