'''
this module is designed for adapting OpenFDA APIs.
source: https://open.fda.gov/apis/
'''

import json
import requests
import time
import datetime
from functools import singledispatch

#### Time Module
class SingleTime:
    def __init__(self, arg = None):
        try:
            self.date = SingleTime._from_none() if isinstance(arg, type(None)) else SingleTime._from_string(arg)
        except ValueError:
            print('Invalid input format: {}, should be YYYYMMDD\n Instantiate with current time'.format(arg))
            self.date = SingleTime._from_none()

    @classmethod
    def _from_none(cls):
        return datetime.datetime.now().strftime('%Y-%m-%d')

    @classmethod
    def _from_string(cls, yyyy_mm_dd):
        return datetime.date(year = int(yyyy_mm_dd[0:4]), 
                            month = int(yyyy_mm_dd[4:6]), 
                            day = int(yyyy_mm_dd[6:8])).strftime('%Y-%m-%d')

class TimeRange:
    INIT_DATE = '19700101'
    CURR_DATE = datetime.date.today().strftime('%Y%m%d')
    SEP_TIME_ATTACH = '+TO+'
    def __init__(self, from_:str = INIT_DATE, to_:str = CURR_DATE):        
        # Time formation
        str_f = SingleTime(from_).date
        str_t = SingleTime(to_).date

        if (str_f == str_t) and (from_ != self.INIT_DATE):
            str_f = SingleTime(self.INIT_DATE).date
            
        self._f = str_f if (str_f < str_t) else str_t
        self._t = str_t if (str_f < str_t) else str_f
        self.range = '[{}{}{}]'.format(self._f, self.SEP_TIME_ATTACH, self._t)

#### Parent Class
class APIAdaptor:
    API_BASE = 'https://api.fda.gov/'
    API_PARAMS = {'search', 'sort', 'count', 'limit', 'skip'}
    API_WARNINGS = ('Search not assigned', 'Limit not assigned', 'Sort not assigned')
    API_SYNTAX_KEYS = {'end_point_end': '.json?', 'param_asign': '=', 'mediator': ':', 'and': '&'}

    @classmethod
    def warning_msg(cls, w_num):
        print('API Warning: ', cls.API_WARNINGS[w_num])
        
    def init(self):
        # core list, defining type of APIs
        self.endpoint_type = {'device/510k'}
    
    class Search:
        SEP_SEARCH_INIT = 'search='
        SEP_SEARCH_ATTACH_AND = '+AND+'
        SEP_SEARCH_ATTACH_OR = '+'

        def __init__(self):
            self._search_query = self.SEP_SEARCH_INIT
            self._search_time_range = ''
            self._searched = False
        
        @staticmethod
        def basic_search(field, term):
            return str(field) + ':\"' + str(term) + '\"'

        def simple_search(self, field, term):
            self._search_query = self.basic_search(field, term)
            self._searched = True
            return self
        
        def add_search(self, field, term, match = False):
            if (not self._searched):
                self.simple_search(field, term)
                self._searched = True

            elif match:
                self._search_query += (self.SEP_SEARCH_ATTACH_AND + self.basic_search(field, term))
            
            else:
                self._search_query += (self.SEP_SEARCH_ATTACH_OR + self.basic_search(field, term))
        
        def add_time(self, field:str, begin_t:str, end_t:str):
            tm_term = TimeRange(begin_t, end_t).range
            if (not self._searched):
                self._search_query = str(field) + ':' + tm_term
                self._searched = True
            
            else:
                self._search_query += self.SEP_SEARCH_ATTACH_AND + str(field) + ':' + tm_term

        def return_search(self):
            if (not self._searched):
                APIAdaptor.warning_msg(0)
                return
            
            elif (self._search_time_range is not ''):
                return self._search_query + self.SEP_SEARCH_ATTACH_AND + self._search_time_range
            
            else:
                return self._search_query

        def return_final(self):
            return self.SEP_SEARCH_INIT + self._search_query

    class Limit:
        LIMIT_DEFAULT_NUM = 20
        LIMIT_MAX = 100
        def __init__(self):
            self._limit_num = None
        
        def set_limit_num(self, num = LIMIT_DEFAULT_NUM):
            if (num > self.LIMIT_MAX):
                print('Limited query number is 100')
                num = self.LIMIT_MAX
            self._limit_num = num
            return self
        
        def return_final(self):
            if (self._limit_num is not None):
                return 'limit=' + str(self._limit_num)
            
            else:
                APIAdaptor.warning_msg(1)

    class Sort:
        sort_types = {1: 'desc', 2: 'asc'}
        def __init__(self):
            self._sort_method = None
        
        def set_sort_method(self, field, sort_type):
            self._sort_method = str(field) + ':' + self.sort_types[sort_type]
        
        def return_final(self):
            if (self._sort_method is not None):
                return 'sort='+ self._sort_method
            else:
                APIAdaptor.warning_msg(2)

    def api_syntax(self):
        # defining core api combination syntax
        # search
        pass

    def api_former(self):
        # formation accdoring to API
        pass


#### Children Classes
## 510K APIAdaptor
class APIforDevice(APIAdaptor):
    API_BASE = APIAdaptor.API_BASE + 'device/510k' + APIAdaptor.API_SYNTAX_KEYS['end_point_end']
    API_SEARCH_FIELDS = {'openfda.regulation_number', 'fei_number', 'device_name', 'device_class', 'product_code', 'medical_specialty_description', 'registration_number', 'k_number'}

    def __init__(self):
        self._final_query = self.API_BASE
        self._query_dict = {}
        self._search_complete = ''

    def add_search_device_name(self, name_key:str):
        if not ('search' in self._query_dict):
            self._query_dict['search'] = self.Search()
            self._query_dict['search'].add_search('device_name', name_key)
        else:
            self._query_dict['search'].add_search('device_name', name_key)    
        self._search_complete = name_key
        return self      
    
    def add_search_product_code(self, product_code_key:str, match:bool = True):
        if not ('search' in self._query_dict):
            self._query_dict['search'] = self.Search()
            self._query_dict['search'].add_search('product_code', product_code_key)          
        else:
            self._query_dict['search'].add_search('product_code', product_code_key, match)
        self._search_complete += ('-' + product_code_key)
        return self      

    def add_search_regulation_number(self, regulation_number_key:str, match:bool = True):
        if not ('search' in self._query_dict):
            self._query_dict['search'] = self.Search()
            self._query_dict['search'].add_search('openfda.regulation_number', regulation_number_key)          
        else:
            self._query_dict['search'].add_search('openfda.regulation_number', regulation_number_key, match)

        self._search_complete += ('-' + regulation_number_key)
        return self      

    def add_search_decision_date_range(self, from_ = None, to_ = None):
        if not ('search' in self._query_dict):
            self._query_dict['search'] = self.Search()
            self._query_dict['search'].add_time('decision_date', from_, to_)          
        else:
            self._query_dict['search'].add_time('decision_date', from_, to_)    
        self._search_complete += TimeRange(from_, to_).range
        return self

    def add_limit(self, num = 20):
        if not ('limit' in self._query_dict):
            self._query_dict['limit'] = self.Limit()
            self._query_dict['limit'].set_limit_num(num)
        else:
            self._query_dict['limit'].set_limit_num(num)
        
        return self

    def add_sort_by_decision_date(self, sort_type = 1):
        if not ('sort' in self._query_dict):
            self._query_dict['sort'] = self.Sort()
            self._query_dict['sort'].set_sort_method('decision_date', sort_type)
        else:
            self._query_dict['sort'].set_sort_method('decision_date', sort_type)
        return self

    def add_queris(self, search_dv_name_key:str = '', 
                         search_product_code_key:str = None,
                         search_product_code_match:bool = True,
                         search_regulation_num_key:str = None,
                         search_regulation_num_match:bool = True,
                         search_date_f:str = None, search_date_t:str = None,
                         limit_num:int = None, 
                         sort_type:int = None):
        
        self.add_search_device_name(search_dv_name_key).add_search_decision_date_range(search_date_f, search_date_t)
        if (search_product_code_key != None):
            self.add_search_product_code(search_product_code_key, search_product_code_match)

        if (search_regulation_num_key != None):
            self.add_search_regulation_number(search_regulation_num_key, search_regulation_num_match)

        num = limit_num
        st = sort_type
        if (limit_num is None):
            num = self.Limit.LIMIT_DEFAULT_NUM
        
        if (sort_type is None):
            st = 1

        self.add_limit(num).add_sort_by_decision_date(st)

    def check_device_search(self):
        print('Current Search: ', self._query_dict['device_name'].return_final())

    def check_all_queries(self):
        for k, v in self._query_dict.items():
            print(k, ':\t', v.return_final())
    
    def return_final_query(self, show = False):
        curr_str = ''
        for _, v in self._query_dict.items():
            curr_str += (v.return_final() + self.API_SYNTAX_KEYS['and'])
        
        self._final_query += curr_str[:-1]
        if show:
            print('Final Query: ', self._final_query)
        return self._final_query
    
    def return_query_list(self):
        return self._search_complete

#### Unit Test Script
TEST_REQUEST = False
TEST_CLASS = True
TEST_CHILD = True

if __name__ == '__main__':
    print('Unit Test')

    if TEST_REQUEST:
        # Requests
        test_url = 'https://api.fda.gov/device/510k.json?search=device_name:%22ekg%22+AND+decision_date:[2011-01-01+TO+2020-01-01]&limit=100'
        r = requests.get(test_url, verify=False)

        print(r.status_code)
        print(r.headers)
        print(r.text)
    
    if TEST_CLASS:
        print('ROOT is ', APIforDevice.API_BASE)

        #### 
        test = APIforDevice()
        test.add_search_device_name('ecg').add_search_decision_date_range('19900425', None).add_limit(20).add_sort_by_decision_date().add_search_product_code('MHX', False).add_search_regulation_number('870.1025', False)
        s1 = test.return_final_query()
        print('S1 is ', s1)

        test_2 = APIforDevice()
        test_2.add_queris(search_dv_name_key = 'ecg', 
                          search_product_code_key = 'MHX', search_product_code_match = False,
                          search_regulation_num_key = '870.1025', search_regulation_num_match = False, search_date_f = '19900425', search_date_t = None, limit_num = 20, sort_type = None)
        s2 = test_2.return_final_query()
        print('S2 is ', s2)
        print(s1 == s2)
        test_2.return_query_list()