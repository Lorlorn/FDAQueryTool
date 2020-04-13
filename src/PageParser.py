'''
this module is designed for parsing single page of target 510k.
example source: https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K130878

'''

import requests
from bs4 import BeautifulSoup as bs
import re

#### Params
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

url = 'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K130878'
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

class PageParser:
    FDA_510K_CENTRAL_POSI = 3

    def __init__(self, url):
        self.url = url
        self.status = {'get_url':False, 'retrieve_central_content': False, 'retrieve_elements_dict':False}
        self.get_url_data = None
        self.central_table = None
        self.central_table_keys = []
        self.element_dict = {}
    
    def get_url(self):
        # intialize status
        self.status = {x : None for x in self.status}

        # get url
        try:
            self.get_url_data = requests.get(self.url)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

        # check in status
        self.status['get_url'] = True
        
        return None

    def retrieve_central_table(self):
        # parse url get data
        soup = bs(self.get_url_data.text, 'lxml')

        # retrieve central table content
        table = soup.find('table', {'align': 'center'})
        self.central_table_keys = [th.text.replace('\n', '') for th in table.find('tr').find_all('th')]
        trs = table.find_all('tr')[1:]
        self.central_table = trs[PageParser.FDA_510K_CENTRAL_POSI].find_all('tr')

        # check in status
        self.status['retrieve_central_content'] = True

    def retrieve_element_dict(self):
        # parse element into dict
        l_col = list()
        r_col = list()
        links = list()

        for tr in self.central_table:
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
                r_col.append(curr_val.lstrip())
                self.element_dict[curr_key] = curr_val.lstrip()

        # check in status
        self.status['retrieve_elements_dict'] = True
        return None
    
    def run(self):
        self.get_url()
        self.retrieve_central_table()
        self.retrieve_element_dict()
    
    def return_dict(self):
        return self.element_dict


if __name__ == "__main__":
    # url = 'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K130878'
    # url = 'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K091000'
    url = 'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K181373'

    print('*'* 100)

    p = PageParser(url)
    p.run()

    for k, v in p.element_dict.items():
        print(k, ': ', v)