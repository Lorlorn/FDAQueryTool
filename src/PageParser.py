'''
this module is designed for parsing single page of target 510k.
example source: https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K130878

'''

import urllib.request
import requests
from bs4 import BeautifulSoup as bs
import re

#### Params
url = 'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K130878'

keys = tuple([
    "Device Classification Name",
    "510(K) Number",
    "Device Name",
    "Applicant",
    "Applicant Contact",
    "Correspondent",
    "Correspondent Contact",
    "Regulation Number",
    "Classification Product Code",
    "Date Received",
    "Decision Date",
    "Decision",
    "Regulation Medical Specialty",
    "510k Review Panel",
    "Summary",
    "Type",
    "Reviewed By Third Party",
    "Combination Product"
    ])

r = requests.get(url)

# Check Status
r.status_code

# Check encoding
r.encoding

# Check content
text = r.text

# Parse with BeautifulSoup
soup = bs(text, 'lxml')

# Retrieve Central Table Content
table = soup.find('table', {'align': 'center'})
keys = [th.text.replace('\n', '') for th in table.find('tr').find_all('th')]
keys_2 = [th.text.replace('\n', '') for th in table.find('tr').find_all('th', {'align': 'left'} )]

# trs = table.find_all('tr')[1:]
# main_table = trs[3].find_all('tr')

# content = dict() 
# l_col = list()
# r_col = list()
# links = list()

# last_key = ''
# last_val = ''

# for tr in main_table:
#     curr_key = ' '.join([re.sub('[\n\t\r\xa0]', '', th.text) for th in tr.find_all('th', {'align': 'left'})])
#     curr_val = ' '.join([re.sub('[\n\t\r\xa0]', '', td.text) for td in tr.find_all('td', {'align': 'left'}, recursive = False)])
#     link = [l.get('href') for l in tr.find('td').find_all('a', href = True)]

#     if len(link) != 0:
#         links.append(link)
#         l_str = ' | '.join(link)
#         curr_val += (' | ' + (l_str))

#     if (curr_key == ''):
#         continue

#     else:       
#         l_col.append(curr_key)
#         r_col.append(curr_val)

# for i in range(len(l_col)):
#     print(l_col[i], ' : ', r_col[i])

if __name__ == "__main__":
    url = 'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K130878'
    # url = 'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K091000'
    # Download from url
    r = requests.get(url)

    # Parse with BeautifulSoup
    soup = bs(r.text, 'lxml')

    # Retrieve Central Table Content
    table = soup.find('table', {'align': 'center'})
    keys = [th.text.replace('\n', '') for th in table.find('tr').find_all('th')]

    # Temp Try
    trs = table.find_all('tr')[1:]
    main_table = trs[3].find_all('tr')

    content = dict() 
    l_col = list()
    r_col = list()
    links = list()

    last_key = ''
    last_val = ''

    for tr in main_table:
        curr_key = ' '.join([re.sub('[\n\t\r\xa0]', '', th.text) for th in tr.find_all('th', {'align': 'left'})])
        curr_val = ' '.join([re.sub('[\n\t\r\xa0]', '', td.text) for td in tr.find_all('td', {'align': 'left'}, recursive = False)])
        link = [l.get('href') for l in tr.find('td').find_all('a', href = True)]

        if len(link) != 0:
            links.append(link)
            l_str = ' | '.join(link)
            curr_val += (' | ' + (l_str))

        if (curr_key == ''):
            continue

        else:       
            l_col.append(curr_key)
            r_col.append(curr_val)

    for i in range(len(l_col)):
        print(l_col[i], ' : ', r_col[i])