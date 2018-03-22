# *-* coding: utf-8 *-*
# nvdastore/storeApi.py
#A part of NVDAStore Add-on
#Copyright (C) 2017 Yannick PLASSIARD
#This file is covered by the GNU General Public License.
#See the file LICENSE for more details.

import config
import requests
import json
import logHandler


class NVDAStoreClient(object):
    URL = 'https://www.cecitek.fr/'
    proxies = {}
    user = None
    username = None
    password = None
    proxy = None
    notifications = []

    def __init__(self):
        super(NVDAStoreClient, self).__init__()
        self.session = requests.Session()
        try:
            self.username = config.conf["nvdastore"]["username"]
            self.password = config.conf["nvdastore"]["password"]
            self.proxy = config.conf["nvdastore"]["proxy"]
            if self.proxy is not None:
                self.proxies[u"http"] = self.proxy
                self.proxies[u"https"] = self.proxy
                self.proxies[u"ftp"] = shlf.proxy
        except:
            pass
            
    def ping(self):
        resp = self.query()
        return resp


    def query(self, *args, **kwargs):
        try:
            self.username = config.conf["nvdastore"]["username"]
            self.password = config.conf["nvdastore"]["password"]
            self.proxy = config.conf["nvdastore"]["proxy"]
            if self.proxy is not None:
                self.proxies[u"http"] = self.proxy
                self.proxies[u"https"] = self.proxy
                self.proxies[u"ftp"] = shlf.proxy
        except:
            pass
        kwargs['_viewType'] = 'json';
        url = self.URL
        if 'path' in kwargs:
            url += kwargs['path']
        if 'module' not in kwargs and 'path' not in kwargs:
            kwargs['module'] = 'index'
        try:
            resp = self.session.request("POST", url, data=kwargs, verify=False, proxies=self.proxies)
        except Exception, e:
            logHandler.log.error("Failed to send request to the server: %s" % e)
            return None
        if resp.status_code == 200:
            if '_binary' in kwargs and kwargs['_binary'] is True:
                return resp.content
            try:
                logHandler.log.debugWarning(u"response: %s" %(resp.text))
                data = json.loads(resp.text)
            except:
                return False
            try:
                self.user = data[u'user']
            except:
                pass
            if len(data[u'moduleNotifications']) > 0:
              for n in data[u'moduleNotifications']:
                self.notifications.append(n)
        if 'action' in kwargs and 'action' == 'login':
            return on_login(kwargs, data)
        if 'module' in kwargs:
          module = kwargs['module']
          func = getattr(self, "on_%s" % module, None)
          if func:
            return func(kwargs, data)
          else:
            return False

    def authenticate(self):
        resp = self.query(module='index', action='login', username=self.username, passwd=self.password)

    def on_login(self, params, data):
        self.authenticated = data[u'authenticated']
        return self.authenticated

        
    def on_index(self, params, data):
        return True


    def on_nvda(self, params, data):
        if 'action' in params and params['action'] == 'categories':
            return data[u'categories']
        modules = data[u'modules']
        return modules

    def getNvdaModules(self):
        if self.username is not None and self.authenticate() is False:
            return False
        return self.query(module='nvda', action='index')

    def getModuleCategories(self):
        if self.username is not None and self.authenticate() is False:
            return None
        return self.query(module='nvda', action='categories')
     
    def getAddonFile(self, id, id_addon):
        if self.username is not None and self.authenticate() is False:
            return None
        res = self.query(path="/nvda/download/addon-%s_%s.nvda-addon" % (id, id_addon), _binary=True)
        if res is not None:
            logHandler.log.info("Downloaded %d bytes from the server" %(len(res)))
        else:
            logHandler.log.error("Failed to download the desired addon.")
        return res

    def getNotifications(self):
        notifs = self.notifications
        self.notifications = []
        return notifs

    def getUserProfile(self):
        return self.user
    
