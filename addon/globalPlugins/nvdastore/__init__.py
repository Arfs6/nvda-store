# *-* coding: utf-8 *-*
# nvdastore/__init__.py
#A part of the NVDAStore Add-on
#Copyright (C) 2017 Yannick PLASSIARD
#This file is covered by the GNU General Public License.
#See the file LICENSE for more details.



import os, sys, time
import api
import ui, wx, gui, core, config, nvwave
import storeGui, storeUtils
import capabilities
import globalPluginHandler, logHandler, addonHandler
addonHandler.initTranslation()
sys.path.append(os.path.dirname(__file__))
import hmac
import requests
import json
import storeApi
del sys.path[-1]
NVDASTORE_MODULE_NAME = 'nvdastore'

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
    def addVersion(self, id, version, changelog, minVersion, maxVersion, capabilities="touch"):
        import versionInfo
        if (versionInfo.version >= minVersion and versionInfo.version <= maxVersion) or 'next' in versionInfo.version or 'dev' in versionInfo.version or 'master' in versionInfo.version:
            if self.checkCapabilities(version, capabilities):
                self.latestVersion = version
                self.versionChangelog = "Version: " + version + "\r\n" + changelog + "\r\n\r\n" + self.versionChangelog
                self.versionId = id
    def __str__(self):
        return u"%s" %(self.name)
    def __repr__(self):
        return u"%s" %(self.name)
    

    def checkCapabilities(self, version, requiredCaps):
        global capCache
        missingCaps = []
        if requiredCaps is None:
            requiredCaps = 'touch'
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
                try:
                    ret = capMethod()
                except Exception, e:
                    ret = False
                    logHandler.log.exception("Failed toexecute method", e)
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
        self.refreshing = False
        self.updates = []
        self.loadConfiguration()
        self.storeClient = storeApi.NVDAStoreClient(self.moduleConfig)
        wx.CallLater(5000, self.refreshAddons)

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

    def doRefreshAddons(self):
        if self.refreshing is False:
            self.refreshing = True
            self.refreshAddons()

    def refreshAddons(self, silent=False):
        global capCache
        self.refreshing = True
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
        self.refreshing = False
        self.selfUpdate(silent)

    def getLocalAddon(self, storeAddon):
        for a in addonHandler.getAvailableAddons():
            if a.manifest['name'].upper() == storeAddon.name.upper():
                return a
        return None

    def selfUpdate(self, silent=False):
        self.updates = []
        for addon in self.addons:
            localAddon = self.getLocalAddon(addon)
            if localAddon and localAddon.manifest[u'version'] <= addon.latestVersion:
                if addon.name.upper() == NVDASTORE_MODULE_NAME.upper():
                    # We should self-update the NVDAStore module itself.
                    if gui.messageBox(_(u"A new release is available for the NVDAStore add-on. Woul,d you like to install it right now? This will cause NVDA to restart."),
		                      _(u"Update available"),
                                      wx.YES_NO | wx.ICON_WARNING) == wx.YES:
                        ui.message(_("Updating..."))
                        ret = storeUtils.installAddon(self.storeClient, addon, True, True)
                        if ret: return
                    else:
                        break
                else:
                    self.updates.append(addon)
        if len(self.updates) > 0:
            nvwave.playWaveFile(os.path.join(os.path.dirname(__file__), "..", "..", "sounds", "notify.wav"))
            if silent is False:
                ui.message(_("NVDAStore: %d addons can be updated. Press NVDA+Shift+Control+U to update them." %(len(self.updates))))


    def script_updateAll(self, gesture):
        self.updateAll()
    script_updateAll.__doc__ = _("Updates all addons to the latest version")

    def updateAll(self):
        updated = 0
        if len(self.updates) is 0:
            self.refreshAddons(True)
            if len(self.updates) == 0:
                ui.message(_("NVDAStore: No update available."))
                return
            
                           
        for update in self.updates:
            gui.mainFrame.prePopup()
            progressDialog = gui.IndeterminateProgressDialog(gui.mainFrame,
			                                     _("NVDAStore"),
			                                     _("Updating %s..." %(update.name)))
            ui.message(_("Updating %s..." %(update.name)))
            try:
                gui.ExecAndPump(storeUtils.installAddon, self.storeClient, update, False, True)
            except:
                progressDialog.done()
                del progressDialog
                gui.mainFrame.postPopup()
                break
            progressDialog.done()
            del progressDialog
            updated += 1
            gui.mainFrame.postPopup()
        if updated:
            core.restart()

    def script_nvdaStore(self, gesture):
        if len(self.addons) == 0:
            gui.mainFrame.prePopup()
            progressDialog = gui.IndeterminateProgressDialog(gui.mainFrame,
			                                     _("Updating addons' list"),
			                                     _("Please wait while the add-on list is being updated."))
            try:
                gui.ExecAndPump(self.doRefreshAddons)
            except:
                progressDialog.done()
                del progressDialog
                gui.mainFrame.postPopup()
                return
            progressDialog.done()
            del progressDialog
            gui.mainFrame.postPopup()
                

        gui.mainFrame.prePopup()
        dlg = storeGui.StoreDialog(gui.mainFrame, self.storeClient, self.addons)
        dlg.Show()
        gui.mainFrame.postPopup()
        del dlg

    script_nvdaStore.__doc__ = _("Opens the NVDA Store to download, install and update NVDA add-ons.")

    __gestures = {
        "kb:nvda+shift+n": "nvdaStore",
        "kb:nvda+shift+control+u": "updateAll",
    }
    
