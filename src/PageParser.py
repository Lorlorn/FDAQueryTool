'''
this module is designed for parsing single page of target 510k.
example source: https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K130878

'''

import urllib.request
from bs4 import BeautifulSoup as bs
import re
TEST = True

if TEST:
    url = 'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K130878'
    # Download from url
    response = urllib.request.urlopen(url)
    data = response.read()
    text = data.decode('utf-8-sig')

    # Parse from text
    soup = bs(text, 'lxml')

    # Simple Re
    tag = r'<tr><th align="left">'
    re.findall(tag, text)