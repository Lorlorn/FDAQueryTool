'''
This is the main script for OpenFDA parsing project.
'''
import sys
import os
sys.path.insert(1, os.path.sep + 'src')

import argparse
import json
import requests
import pandas as pd
from datetime import date
from src import PageParser
from src import BatchQuery

#### Argument Parser
parser = argparse.ArgumentParser()
parser.add_argument('-sr_key', type = str, help = '[Search] key for device name', default = '')
parser.add_argument('-sr_pd_code', type = str, help = '[Search] key for specific product code', default = None)
parser.add_argument('-sr_rgl_num', type = str, help = '[Search] key for regulation number', default = None)
parser.add_argument('-sr_time_f', type = str, help = '[Search] decision time from, should be YYYYMMDD', default = None)
parser.add_argument('-sr_time_t', type = str, help = '[Search] decision time to, should be YYYYMMDD', default = None)
parser.add_argument('-l_num', type = int, help = '[Limit] number of reports to be shown, range [1, 100]', default = 20)
parser.add_argument('-srt_type', type = int, help = '[Sort] type of sorting, 1 for desc, 2 for asc', choices = [1, 2], default = 1)
args = parser.parse_args()

print('*'*45 + '\n\t\tInput Arguments\n' + '*'*45)
print('Search Key:\t', args.sr_key)
print('Search Product Code:\t', args.sr_pd_code)
print('Search Regulation Number:\t', args.sr_rgl_num)
print('Search Time (From):\t', args.sr_time_f)
print('Search Time (To):\t', args.sr_time_t)
print('Search Number:\t', args.l_num)
print('Sort Type:\t', args.srt_type)

#### Batch Query
test = BatchQuery.APIforDevice()
test.add_queris(search_dv_name_key = args.sr_key,
                search_product_code_key = args.sr_pd_code, search_product_code_match = True,
                search_regulation_num_key = args.sr_rgl_num, search_regulation_num_match = True,
                search_date_f = args.sr_time_f, search_date_t = args.sr_time_t, 
                limit_num =  args.l_num, 
                sort_type = args.srt_type)
root_url  = test.return_final_query()
print('API Query:\t', root_url)

#### Requesting From FDA Database
## query
print('*'*45 + '\n\t\tRequest From Database\n' + '*'*45)

data = requests.get(root_url)
print('Connection Success:\t{}'.format(data.status_code == 200))

## read to json & output
json_data = json.loads(data.text)

if (data.status_code != 200):
    print('Error: ', json_data['error']['message'])
    exit('You suck at searching. \nBye bro.')

print('Return Files / Total:\t {} / {}'.format(json_data['meta']['results']['limit'], json_data['meta']['results']['total']))

# to data
df = pd.DataFrame(json_data['results'])
k_num_list = df['k_number'].to_list()

# save database results?
save = input('Save database query results into CSV? (Y/N): ')

if (save is 'Y') or (save is 'y'):
    file_name = '{}-{}-[{} to {}]-database.csv'.format(date.today().strftime('%Y%m%d'), args.sr_key, args.sr_time_f, args.sr_time_t)
    df.to_csv(file_name)
    print('Saved.')
print('Overview: ')
print(df.head())
del df

#### proceed parsing from single pages
# combine from k-number
print('*'*45 + '\n\t\tRequest From Pages\n' + '*'*45)
proceed = input('Proceed? (Y/N): ')

if (proceed is 'N') or (proceed is 'n'):
    exit('Bye bro.')

# parsing
print('Parsing...')
root_url = 'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID={}'
denovo_url = 'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/denovo.cfm?ID={}'
urls = [root_url.format(s) if s[0] == 'K' else denovo_url.format(s) for s in k_num_list] 

dict_list = []

for u in urls:
    test = PageParser.PageParser(u)
    test.run()
    dict_list.append(test.element_dict)
    print('Status: ', 'OK' if (test.get_url_data.status_code == 200) else 'Fail', ' | ', u)

# save?
save = input('Save parsed results into CSV? (Y/N): ')
df = pd.DataFrame(dict_list)

if (save is 'Y') or (save is 'y'):
    file_name = '{}-{}-[{} to {}]-parsed.csv'.format(date.today().strftime('%Y%m%d'), args.sr_key, args.sr_time_f, args.sr_time_t)
    df.to_csv(file_name)
    print('Saved.')
print('Overview: ')
print(df.head())
del df

print('~ END OF PROGRAM~')