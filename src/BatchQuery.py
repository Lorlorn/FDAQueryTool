'''
this module is designed for adapting OpenFDA APIs.
source: https://open.fda.gov/apis/
'''

import json
import requests

#### Parent Class
class APIAdaptor:
    api_root = 'https://api.fda.gov/'
    api_params = {'search', 'sort', 'count', 'limit', 'skip'}
    api_warning = ('Search not assigned', 'Limit not assigned', 'Sort not assigned')

    @classmethod
    def warning_msg(cls, w_num):
        print('API Warning: ', cls.api_warning[w_num])

    def init(self):
        # core list, defining type of APIs
        self.endpoint_type = {'device/510k'}
        self.syntax_keys = {'end_point_end': '.json?', 
                            'param_asign': '=',
                            'mediator': ':',
                            'and': '&'}

    class Search:
        def __init__(self):
            self._search_query = 'search='
            self._searched = False
        
        @staticmethod
        def basic_search(field, term):
            return str(field) + ':\"' + str(term) + '\"'

        def simple_search(self, field, term):
            self._search_query = self.basic_search(field, term)
            self._searched = True
            return self
        
        def add_search(self, field, term, match = False):
            if self._search_query == '':
                self.simple_search(field, term)

            elif match:
                self._search_query += ('+AND+' + self.basic_search(field, term))
            
            else:
                self._search_query += ('+' + self.basic_search(field, term))
            self._searched = True
            return self
            
        def return_search(self):
            if (not self._searched):
                APIAdaptor.warning_msg(0)
                return
            return self._search_query
            
    class Limit:
        def __init__(self):
            self._limit_num = None
        
        def set_limit_num(self, num = 1):
            
            self._limit_num = num
            return self
        
        def return_limit(self):
            if (self._limit_num is not None):
                return 'limit=' + str(self._limit_num)
            
            else:
                APIAdaptor.warning_msg(1)

    class Sort:
        sort_fields = {'1':'report_date'} # unfinished
        sort_types = {'1': 'desc', '2': 'asc'}
        def __init__(self):
            self._sort_method = None
        
        def set_sort_method(self, sort_field, sort_type):
            self._sort_method = self.sort_fields[sort_field] + ':' + self.sort_types[sort_type]
        
        def return_sort(self):
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

class APIRequest(APIAdaptor):
    def init(self):
        self.api_adapt = APIAdaptor()
        self.data = []
    
    def request_formation(self, *args):
        pass
    
    def request_send(self):
        try:
            pass
        except:
            pass
        else:
            pass



#### Unit Test Script
if __name__ == '__main__':
    print('Unit Test')

    # Requests
    r = requests.get("https://api.fda.gov/device/510k.json?search=advisory_committee:cv&limit=1", verify=False)
    print(r.status_code)
    print(r.headers)
