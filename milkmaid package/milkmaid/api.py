import milkmaid
import requests

class api_requestor():
    header = {"Authorization": None }
    robj = None
    data = None

    def __init__(self, token):
        self.header["Authorization"] = "Token " + token

    def get_request(self, url_resource):
        self.robj = requests.get(milkmaid.baseurl + url_resource, headers=self.header)
        self.data = self.robj.json()

    def post_request(self, url_resource, data):
        self.robj = requests.post(milkmaid.baseurl + url_resource, data=data, headers=self.header)
        self.data = self.robj.json()
