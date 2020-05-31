
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

class Interact:
    TYPE_LIST = ['terminal', 'web']
    def __init__(self, type_num):
        self._target = self.TYPE_LIST[type_num]

    def emit(self, msg):
        if (self._target == self.TYPE_LIST[0]):
            print(msg)
        elif (self._target == self.TYPE_LIST[1]):
            pass
    
    def receive(self, msg):
        if (self._target == self.TYPE_LIST[0]):
            value = input(msg)
            return value
        elif (self._target == self.TYPE_LIST[1]):
            pass


#### Define Query
class SingleQuery:
# This class will be refactored to be a FSM
    PROCESS_LIST = {0:'Initialization', 1:'Argument Taking', 2:'Batch Query', 3:'Page Parsing', 4:'End Process', 5:'Exception'}
    ARGS = {'sr_key': '', 'sr_pd_code': None, 'bool_pd_code_or': False, 'sr_rgl_num': None, 'bool_rgl_num_or': False, 'sr_time_f': None, 'sr_time_t': None, 'l_num': 20, 'srt_type': 1}
    INPUT_TYPE = {'TERMINAL'}
    STATUS = 'None'
    ROOT = '.'
    ROOT_URL = 'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID={}'
    DENOVO_URL = 'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/denovo.cfm?ID={}'

    class Args:
        def __init__(self, args_dict):
            for k, v in args_dict.items():
                self.k = v


    def __init__(self, interact_type = 0):
        # set interact
        self.interact = Interact(interact_type)

        # members
        self._set_process(0)
        self._args_dict = {}
        self._error_url = []
        self._k_num_list = []
        self._quesy_list = ''
        self.path_handler = FilePathHandler()

        # set Folder
        self.path_handler.root = self.ROOT
        self.path_handler.curr_path = datetime.now().strftime('%Y%m%d-%H%M%S')

    def _report(self):
        self.interact.emit(' > ' * 8 + '{} Process'.format(self.STATUS))

    def _set_process(self, curr_proc):
        self.STATUS = self.PROCESS_LIST[curr_proc]
        self._report()

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

        self.interact.emit('*'*45 + '\n\t\tInput Arguments\n' + '*'*45)
        self.interact.emit('Search Key:\t{}'.format(args.sr_key))
        self.interact.emit('Search Product Code:\t{} {}'.format(args.sr_pd_code, '(OR)' if args.bool_pd_code_or else '(AND)'))
        self.interact.emit('Search Regulation Number:\t{} {}'.format(args.sr_rgl_num, '(OR)' if args.bool_rgl_num_or else '(AND)'))
        self.interact.emit('Search Time (From):\t{}'.format(args.sr_time_f))
        self.interact.emit('Search Time (To):\t{}'.format(args.sr_time_t))
        self.interact.emit('Search Number:\t{}'.format(args.l_num))
        self.interact.emit('Sort Type:\t{}'.format(args.srt_type))


    def ArgumentProcess(self):
        self._set_process(1)

        # Deal input
        args = self.Args(self.ARGS)
        args.sr_key = self.interact.receive('Enter Search Device Name: ')
        args.sr_pd_code = self.interact.receive('Enter Search Product Code: ')
        if (args.sr_pd_code != ''): 
             args.bool_pd_code_or = bool(self.interact.receive('Search With AND? Press "Enter" for AND, any other characters for OR: '))
        else:
            args.sr_pd_code = None
            args.bool_pd_code_or = None
        args.sr_rgl_num = self.interact.receive('Enter Regulation Number: ')
        if (args.sr_rgl_num != ''):
            args.bool_rgl_num_or = bool(self.interact.receive('Search With AND? Press "Enter" for AND, any other characters for OR: '))
        else:
            args.sr_rgl_num = None
            args.bool_rgl_num_or = None
        args.sr_time_f = self.interact.receive('Enter Search Time (From, YYYYMMDD. Press "Enter" using DEFAULT): ')
        args.sr_time_t = self.interact.receive('Enter Search Time (To, YYYYMMDD. Press "Enter" using DEFAULT)  : ')
        args.l_num = self.interact.receive('Enter Files Numbers (Max. 100. Press "Enter" using DEFAULT): ')
        try:
            val = int(args.l_num)
            if val > 200 or val < 1:
                args.l_num = 20
                self.interact.emit('Wrong Input, using DEFAULT.')
            else:
                args.l_num = val

        except ValueError:
            self.interact.emit('Wrong Input, using DEFAULT.')
            args.l_num = 20

        args.srt_type = self.interact.receive('Enter Sort Type (1: Desc, 2 Asc. Press "Enter" using DEFAULT): ')
        try:
            val = int(args.srt_type)
            if val not in [1, 2]:
                self.interact.emit('Wrong Input, using DEFAULT.')
                args.srt_type = 1
            else:
                args.srt_type = val

        except ValueError:
            self.interact.emit('Wrong Input, using default.')
            args.srt_type = 1


        self._args_dict = vars(args)

        # Deal report
        self.interact.emit('*'*45 + '\n\t\tInput Arguments\n' + '*'*45)
        self.interact.emit('Search Key:\t{}'.format(args.sr_key))
        self.interact.emit('Search Product Code:\t{} {}'.format(args.sr_pd_code, '(OR)' if args.bool_pd_code_or else '(AND)'))
        self.interact.emit('Search Regulation Number:\t{} {}'.format(args.sr_rgl_num, '(OR)' if args.bool_rgl_num_or else '(AND)'))
        self.interact.emit('Search Time (From):\t{}'.format(args.sr_time_f))
        self.interact.emit('Search Time (To):\t{}'.format(args.sr_time_t))
        self.interact.emit('Search Number:\t{}'.format(args.l_num))
        self.interact.emit('Sort Type:\t{}'.format(args.srt_type))
        
        
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
        self.interact.emit('API Query:\t{}'.format(root_url))

        # Request from database
        self.interact.emit('*'*45 + '\n\t\tRequest From Database\n' + '*'*45)
        
        data = requests.get(root_url)
        self.interact.emit('Connection Success:\t{}'.format(data.status_code == 200))

        # read to json & output
        json_data = json.loads(data.text)

        if (data.status_code != 200):
            # raise ConnectionError('Error: ', json_data['error']['message'])
            self.interact.emit('Error: {}'.format(json_data['error']['message']))
            self.EndProcess()

        self.interact.emit('Return Files / Total:\t {} / {}'.format(json_data['meta']['results']['limit'], json_data['meta']['results']['total']))

        # to data
        df = DataFrame(json_data['results'])
        self._k_num_list = df['k_number'].to_list()

        # save database results?
        # save = self.interact.receive('Save database query results into CSV? (Y/N): ')
        save = 'Y'

        if (save is 'Y') or (save is 'y'):
            file_name = self.path_handler.curr_path + '{}-database.csv'.format(self._quesy_list)
            df.to_csv(file_name)
            self.interact.emit('Result Table Saved.')
        self.interact.emit('Overview:\n {}'.format(df.head()))
        del df

    def PageParsingProcess(self):
        self._set_process(3)

        # Read urls
        urls = [self.ROOT_URL.format(s) if s[0] == 'K' else self.DENOVO_URL.format(s) for s in self._k_num_list] 
        pdf_search_key = self.interact.receive('Search Additional Key in PDF? Press "Enter" if none. ')

        # Parsing each page
        dict_list = []
        for u in urls:
            self._error_url.append(u)
            page_parser = PageParser.PageParser(u)
            page_parser.run()

            # Search PDF Process
            key_dict = page_parser.pdf_dealer(self.path_handler.curr_path, pdf_search_key)

            dict_list.append(page_parser.element_dict)
            self.interact.emit('Status: {} | {} | Number of PDF: {} | Containing Key: {}'.format(
                'OK' if (page_parser.get_url_data.status_code == 200) else 'Fail',
                u,
                len(page_parser.return_pdf_links_dict()),
                'Yes' if len(key_dict) > 0 else 'No'))
            self._error_url.pop()

        # save?
        # save = self.interact.receive('Save parsed results into CSV? (Y/N): ')
        save = 'Y'
        df = DataFrame(dict_list)
        
        if (save is 'Y') or (save is 'y'):
            file_name = self.path_handler.curr_path + '{}-parsed.csv'.format(self._quesy_list)
            df.to_csv(file_name)
            self.interact.emit('Result Table Saved.')
        self.interact.emit('Overview: {}'.format(df.head()))
        del df
    
    def EndProcess(self):
        self.interact.emit('Bye bro.')
        exit()

    def ErrorProcess(self):
        self._set_process(5)
        with open(self.path_handler.curr_path + os.path.sep + 'Log.txt', 'w') as f:
            for line in self._error_url:
                f.write('Error at: ' + line)
        self.interact.emit('Error At: {}'.format(self._error_url))

if __name__ == '__main__':

    while(True):
        a = SingleQuery()
        try:
            a.ArgumentProcess()
            a.BatchQueryProcess()
            a.PageParsingProcess()
        except:
            a.ErrorProcess()
            print('Encounter Unexpected Error. Please search again.')
            continue

        if not bool(input('Continue? Press "Enter" to leave. Enter "OK" or random characters to conitnue: ')):
            a.EndProcess()
            break