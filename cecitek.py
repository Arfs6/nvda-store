import sys, requests
import json

class Cecitek(object):
    URL = 'https://www.cecitek.fr/'

    def __init__(self):
        super(Cecitek, self).__init__()
        self.session = requests.Session()
        
    def ping(self):
        resp = self.query()
        return resp.status == 200


    def query(self, *args, **kwargs):
        kwargs['_viewType'] = 'json';
        if 'module' not in kwargs:
            kwargs['module'] = 'index'
        # print repr(kwargs)
        try:
            resp = self.session.post(self.URL, data=kwargs, verify=False)
        except Exception, e:
            print "Failed to send request to the server: %s" % e
            return None
        if resp.status_code == 200:
            try:
                data = json.loads(resp.text)
            except:
                print "Invalid response from the server: %s" %(resp.text)
                return False
            notif = data[u'moduleNotifications']
            if len(notif) > 0:
                for n in notif:
                    print u"** %s" % n            
            if 'module' in kwargs:
                module = kwargs['module']
                func = getattr(self, "on_%s" % module, None)
                print "calling on_%s" % module
                if func:
                    return func(kwargs, data)
                else:
                    return False

    def authenticate(self, username, password):
        resp = self.query(module='index', action='login', username=username, passwd=password)

    def on_login(self, params, data):
        return self.query(module='episode', action='list')

    def on_index(self, params, data):
        if 'action' in params and params['action'] == 'login':
            return self.on_login(params, data)
        return True

    def on_episode(self, params, data):
        if 'action' in params and params['action'] == 'list':
            for episode in data[u'episodes']:
                print u"* %s: %s" %(episode[u'episode_id'], episode[u'episode_title'])
            return True
        elif params['action'] == 'view':
            print u"Episode: %s" %(data[u'episode'][u'title'])
            print u"Description: %s" % data[u'episode'][u'header']
            files = data[u'audiofiles']
            print repr(data)
            for file in files:
                print u"%s: %s" %(file[u'id'], file[u'file'])
            
        elif params['action'] == 'comment':
            print data
            
    def cmd_episode(self, args):
        if len(args) >= 1:
            limit = args[0]
        else:
            limit = 20
        self.query(module='episode', action='list', limit=limit)

    def cmd_detail(self, args):
        id = args[0]
        self.query(module='episode', action='view', id=id)

    def cmd_comment(self, args):
        id = args[0]
        self.query(module='episode', action='comment', epId=id)
    
if __name__ == '__main__':
    ctk = Cecitek()
    if ctk.ping<():
        print "Connected to Cecitek"
        cmd = sys.argv[1]
        func = getattr(ctk, "cmd_%s" % cmd, None)
        if func is not None:
            func(sys.argv[2:])
    else:
        print "Website is offline"
