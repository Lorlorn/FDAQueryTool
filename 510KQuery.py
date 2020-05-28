
import sys
import os
sys.path.insert(1, os.path.sep + 'src')

import argparse
import json
import requests
from pandas import DataFrame
from datetime import datetime
from src import PageParser
from src import BatchQuery
from src import PageParser
from src.utils.Utils import FilePathHandler

class SingleQuery:
# This class will be refactored to be a FSM
    PROCESS_LIST = {0:'Initialization', 1:'Argument Taking', 2:'Batch Query', 3:'Page Parsing', 4:'End Process', 5:'Exception'}
    ARGS = {'sr_key': '', 'sr_pd_code': None, 'bool_pd_code_or': False, 'sr_rgl_num': None, 'bool_rgl_num_or': False, 'sr_time_f': None, 'sr_time_t': None, 'l_num': 20, 'srt_type': 1}
    INPUT_TYPE = {'TERMINAL'}
    STATUS = 'None'
    ROOT = '.'
    ROOT_URL = 'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID={}'
    DENOVO_URL = 'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/denovo.cfm?ID={}'


    def _report(self):
        print('{} Process'.format(self.STATUS))


    def _set_process(self, curr_proc):
        self.STATUS = self.PROCESS_LIST[curr_proc]
        self._report()


    def __init__(self):
        self._set_process(0)
        self._args_dict = {}
        self._k_num_list = []
        self._quesy_list = ''
        self.path_handler = FilePathHandler()

        # set Folder
        self.path_handler.root = self.ROOT
        self.path_handler.curr_path = datetime.now().strftime('%Y%m%d-%H%M%S')


    def ArgumentProcessTerminal(self):
        self._set_process(1)

        # parse args from terminal
        parser = argparse.ArgumentParser()
        parser.add_argument('-sr_key', type = str, help = '[Search] key for device name', default = '')
        parser.add_argument('-sr_pd_code', type = str, help = '[Search] key for specific product code', default = None)
        parser.add_argument('--sr_pd_code_OR', help = '[Search] product code with OR', default = False, dest = 'bool_pd_code_or', action = 'store_true')
        parser.add_argument('--no-sr_pd_code_OR', help = '[Search] product code with AND', dest = 'bool_pd_code_or', action = 'store_false')

        parser.add_argument('-sr_rgl_num', type = str, help = '[Search] key for regulation number', default = None)
        parser.add_argument('--sr_rgl_num_OR', help = '[Search] regulation number with OR', default = False, dest = 'bool_rgl_num_or', action = 'store_true')
        parser.add_argument('--no-sr_rgl_num_OR',help = '[Search] regulation number with AND', dest = 'bool_rgl_num_or', action = 'store_false')

        parser.add_argument('-sr_time_f', type = str, help = '[Search] decision time from, should be YYYYMMDD', default = None)
        parser.add_argument('-sr_time_t', type = str, help = '[Search] decision time to, should be YYYYMMDD', default = None)
        parser.add_argument('-l_num', type = int, help = '[Limit] number of reports to be shown, range [1, 100]', default = 20)
        parser.add_argument('-srt_type', type = int, help = '[Sort] type of sorting, 1 for desc, 2 for asc', choices = [1, 2], default = 1)
        args = parser.parse_args()

        self._args_dict = vars(args)

        print('*'*45 + '\n\t\tInput Arguments\n' + '*'*45)
        print('Search Key:\t', args.sr_key)
        print('Search Product Code:\t', args.sr_pd_code, '(OR)' if args.bool_pd_code_or else '(AND)')
        print('Search Regulation Number:\t', args.sr_rgl_num, '(OR)' if args.bool_rgl_num_or else '(AND)')
        print('Search Time (From):\t', args.sr_time_f)
        print('Search Time (To):\t', args.sr_time_t)
        print('Search Number:\t', args.l_num)
        print('Sort Type:\t', args.srt_type)


    def BatchQueryProcess(self):
        self._set_process(2)

        # Find query
        batch_query = BatchQuery.APIforDevice()
        batch_query.add_queris(search_dv_name_key = self._args_dict['sr_key'],
                        search_product_code_key = self._args_dict['sr_pd_code'], search_product_code_match = (not self._args_dict['bool_pd_code_or']),
                        search_regulation_num_key = self._args_dict['sr_rgl_num'], search_regulation_num_match = (not self._args_dict['bool_rgl_num_or']),
                        search_date_f = self._args_dict['sr_time_f'], search_date_t = self._args_dict['sr_time_t'], 
                        limit_num =  self._args_dict['l_num'], 
                        sort_type = self._args_dict['srt_type'])
        root_url  = batch_query.return_final_query()
        self._quesy_list = batch_query.return_query_list()
        print('API Query:\t', root_url)

        # Request from database
        print('*'*45 + '\n\t\tRequest From Database\n' + '*'*45)
        
        data = requests.get(root_url)
        print('Connection Success:\t{}'.format(data.status_code == 200))

        # read to json & output
        json_data = json.loads(data.text)

        if (data.status_code != 200):
            # raise ConnectionError('Error: ', json_data['error']['message'])
            print('Error: ', json_data['error']['message'])
            self.EndProcess()

        print('Return Files / Total:\t {} / {}'.format(json_data['meta']['results']['limit'], json_data['meta']['results']['total']))

        # to data
        df = DataFrame(json_data['results'])
        self._k_num_list = df['k_number'].to_list()

        # save database results?
        save = input('Save database query results into CSV? (Y/N): ')

        if (save is 'Y') or (save is 'y'):
            file_name = self.path_handler.curr_path + '{}-database.csv'.format(self._quesy_list)
            df.to_csv(file_name)
            print('Saved.')
        print('Overview:\n', df.head())
        del df

    def PageParsingProcess(self):
        urls = [self.ROOT_URL.format(s) if s[0] == 'K' else self.DENOVO_URL.format(s) for s in self._k_num_list] 
        pdf_search_key = input('Search Additional Key in PDF? Press "Enter" if none. ')

        # Parsing each page
        dict_list = []
        for u in urls:
            page_parser = PageParser.PageParser(u)
            page_parser.run()

            # Search PDF Process
            key_dict = page_parser.pdf_dealer(self.path_handler.curr_path, pdf_search_key)

            dict_list.append(page_parser.element_dict)
            print('Status: {} | | {} | Number of PDF: {} | Containing Key {}'.format(
                'OK' if (page_parser.get_url_data.status_code == 200) else 'Fail',
                u,
                len(page_parser.return_pdf_links_dict()),
                'Yes' if len(key_dict) > 0 else 'No'
            ))

        # save?
        save = input('Save parsed results into CSV? (Y/N): ')
        df = DataFrame(dict_list)
        
        if (save is 'Y') or (save is 'y'):
            file_name = self.path_handler.curr_path + '{}-parsed.csv'.format(self._quesy_list)
            df.to_csv(file_name)
            print('Saved.')
        print('Overview: ', df.head())
        del df
    
    def EndProcess(self):
        print('Bye bro.')
        exit()
    


if __name__ == '__main__':
    a = SingleQuery()
    a.ArgumentProcessTerminal()
    a.BatchQueryProcess()
    a.PageParsingProcess()
    input('Exit Programe.')
