# *-* coding: utf-8 *-*
# nvdastore/__init__.py
#A part of the NVDAStore Add-on
#Copyright (C) 2017 Yannick PLASSIARD
#This file is covered by the GNU General Public License.
#See the file LICENSE for more details.



import os, sys
import api
import ui, gui, config
import storeGui
import capabilities
import globalPluginHandler, logHandler, addonHandler
addonHandler.initTranslation()
sys.path.append(os.path.dirname(__file__))
import hmac
import requests
import json
import storeApi
del sys.path[-1]

class StoreAddon(object):
    id = ""
    category = ""
    name = ""
    description = ""
    author = ""
    email = ""
    latestVersion = ""
    versionChangelog = ""
    versionId = ""

    def __init__(self, id, category, name, author, email, description):
        super(StoreAddon, self).__init__()
        self.id = id
        self.category = category
        self.name = name
        self.author = author
        self.email = email
        self.description = description
    def addVersion(self, id, version, changelog, minVersion, maxVersion, capabilities=None):
        import versionInfo
        if (versionInfo.version >= minVersion and versionInfo.version <= maxVersion) or 'next' in versionInfo.version or 'dev' in versionInfo.version or 'master' in versionInfo.version:
            if self.checkCapabilities(version, capabilities) and self.latestVersion <= version:
                self.latestVersion = version
                self.versionChangelog = "Version: " + version + "\r\n" + changelog + "\r\n\r\n" + self.versionChangelog
                self.versionId = id
    def __str__(self):
        return u"%s (%s)" %(self.name, self.latestVersion)

    def checkCapabilities(self, version, requiredCaps):
        global capCache
        missingCaps = []
        if requiredCaps is None:
            return True
        for capability in requiredCaps.split(","):
            try:
                ret = capCache[capability]
            except:
                ret = None
            if ret is not None:
                if ret is False:
                    missingCaps.append(capability)
                continue                
            capName = "cap_%s" % capability
            capMethod = getattr(capabilities, capName, None)
            if capMethod is not None:
                logHandler.log.info("Executing %s" % capName)
                ret = capMethod()
            else:
                ret = False
            capCache[capability] = ret
            if ret is False:
                missingCaps.append(capability)
        if len(missingCaps) > 0:
            logHandler.log.info("The following capabilities are missing for %s to be installed: %s" %(self.name, ", ".join(missingCaps)))
            return False
        return True

capCache={}
class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    scriptCategory = _("NVDAStore")
    moduleConfig = {}
    addons = []
    
    def __init__(self):
        super(globalPluginHandler.GlobalPlugin, self).__init__()
        self.loadConfiguration()
        self.storeClient = storeApi.NVDAStoreClient(self.moduleConfig)

    def loadConfiguration(self):
        try:
            f = file(os.path.join(config.getUserDefaultConfigPath(), "nvdastore.json"))
            data = json.loads(f.read())
            f.close()
            self.moduleConfig = data
        except:
            pass
        
    def getCategory(self, catList, id):
        for cat in catList:
            if cat[u'id'] == id:
                return cat[u'name']
        return None

    def script_nvdaStore(self, gesture):
        global capCache
        capCache = {}
        self.addons = []
        modules = self.storeClient.getNvdaModules()
        notifs = self.storeClient.getNotifications()
        if len(notifs) > 0:
            ui.message(_(u"Notification: %s" %(", ".join(notifs))))
        if modules is None or len(modules) == 0:
            ui.message(_("Unable to connect to the Cecitek NVDAStore. Please check you're connected to the internet."))
            return
        catList = self.storeClient.getModuleCategories()
        if catList is None or len(catList) == 0:
            ui.message(_("Unable to connect to the Cecitek NVDAStore. Please check you're connected to the internet."))
            return
        
        for module in modules:
            m = StoreAddon(module[u'id'], self.getCategory(catList, module[u'id_category']), module[u'name'], module[u'author'], module[u'email'], module[u'description'])
            for v in module[u'versions']:
                caps = None
                try:
                    caps = v[u'capabilities']
                except:
                    caps = None
                m.addVersion(v[u'id'], v[u'version'], v[u'changelog'], v[u'minNvdaVersion'], v[u'maxNvdaVersion'], caps)
            if m.latestVersion != "":
                self.addons.append(m)
            
        log = ""
        for a in self.addons:
            log += "%s (%s) " %(a.name, a.latestVersion)
        logHandler.log.info("Available addons in the store: %s" % log)
        gui.mainFrame.prePopup()
        dlg = storeGui.StoreDialog(gui.mainFrame, self.storeClient, self.addons)
        dlg.Show()
        gui.mainFrame.postPopup()
        del dlg

    script_nvdaStore.__doc__ = _("Opens the NVDA Store to download, install and update NVDA add-ons.")

    __gestures = {
        "kb:nvda+shift+c": "nvdaStore",
    }
    
