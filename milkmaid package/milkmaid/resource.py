import milkmaid.api
import milkmaid

class MementoEvent():
    id = None
    deployment = None
    datetime = None
    unread = None
    api = None

    def __init__(self, token=None, api_r=None):

        if token == None:
            token = milkmaid.token
        self.api = milkmaid.api.api_requestor(token)
        if api_r != None:
            self.api = api_r

    def from_dict(self, m_obj):
        self.id = m_obj['pk']
        self.deployment = m_obj['deployment']
        self.datetime = m_obj['datetime']
        self.unread = m_obj['unread']

    def create(self):
        payload = {'datetime': self.datetime, 'unread':True}
        self.api.post_request('/memento/e/smart/', payload)
        self.from_dict(self.api.data)

    def list(token=None):
        if token == None:
            token = milkmaid.token
        api = milkmaid.api.api_requestor(token)
        api.get_request('/memento/e/smart/')
        l = []
        for m_raw in api.data:
            new_mev = MementoEvent(api_r=api)
            new_mev.from_dict(m_raw)
            l.append(new_mev)
        return l

class AthenaNotification():
    id = None
    deployment = None
    nottype = None
    ack_time = None
    event_time = None
    time_created = None

    def __init__(self, token=None, api_r=None):
        self.id = None
        self.deployment = None
        self.nottype = None
        self.ack_time = None
        self.event_time = None
        self.time_created = None

        if token == None:
            token = milkmaid.token
        self.api = milkmaid.api.api_requestor(token)
        if api_r != None:
            self.api = api_r

    def from_dict(self, a_obj):
        self.id = a_obj['pk']
        self.deployment = a_obj['deployment']
        self.nottype = a_obj['nottype']
        self.ack_time = a_obj['ack_time']
        self.event_time = a_obj['event_time']
        self.time_created = a_obj['time_created']

    def create(self):
        payload = {'event_time':self.event_time, 'nottype':self.nottype}
        self.api.post_request('/athena/notify/smart/', payload)
        self.from_dict(self.api.data)

    def list(token=None):
        if token == None:
            token = milkmaid.token
        api = milkmaid.api.api_requestor(token)
        api.get_request('/athena/notify/smart/')
        l = []
        for anot_raw in api.data:
            new_anot = AthenaNotification(api_r=api)
            new_anot.from_dict(anot_raw)
            l.append(new_anot)
        return l

class AthenaNotifyType():
    id = None
    title = None
    detail = None

    def __init__(self, token=None, api_r=None):
        self.id = None
        self.title = None
        self.detail= None

        if token == None:
            token = milkmaid.token
        self.api = milkmaid.api.api_requestor(token)
        if api_r != None:
            self.api = api_r

    def from_dict(self, nt_obj):
        self.id = nt_obj['id']
        self.title = nt_obj['title']
        self.detail = nt_obj['detail']

    def list(token=None):
        if token == None:
            token = milkmaid.token
        api = milkmaid.api.api_requestor(token)
        api.get_request('/athena/types/')
        l = []
        for nt_raw in api.data:
            new_nt = AthenaNotifyType(api_r=api)
            new_nt.from_dict(nt_raw)
            l.append(new_nt)
        return l
