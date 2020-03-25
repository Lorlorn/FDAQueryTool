'''
this module is designed for adapting OpenFDA APIs.
source: https://open.fda.gov/apis/
'''

import json
import requests

#### Parent Class
class APIAdaptor:
    def init(self):
        # core list, defining type of APIs
        self._api_type_list = {}
    
    def api_syntax(self):
        # defining core api combination syntax
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
