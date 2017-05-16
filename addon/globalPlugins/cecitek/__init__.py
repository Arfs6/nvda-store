# *-* coding: utf-8 *-*

# *-* coding: utf8 *-*


import os, sys
import api
import ui, gui
import storeGui
import globalPluginHandler, logHandler, addonHandler
addonHandler.initTranslation()
sys.path.append(os.path.dirname(__file__))
import hmac
import requests
import cecitek
import json
del sys.path[-1]

class StoreAddon(object):
    id = ""
    name = ""
    description = ""
    author = ""
    email = ""
    latestVersion = ""
    versionChangelog = ""
    versionId = ""

    def __init__(self, id, name, author, email, description):
        super(StoreAddon, self).__init__()
        self.id = id
        self.name = name
        self.author = author
        self.email = email
        self.description = description
    def addVersion(self, id, version, changelog, minVersion, maxVersion):
        import versionInfo
        if (versionInfo.version >= minVersion and versionInfo.version <= maxVersion) or 'next' in versionInfo.version or 'dev' in versionInfo.version or 'master' in versionInfo.version:
            if self.latestVersion <= version:
                self.latestVersion = version
                self.versionChangelog = changelog
                self.versionId = id
    def __str__(self):
        return u"%s (%s)" %(self.name, self.latestVersion)

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    scriptCategory = _("Cecitek")
    addons = []
    
    def __init__(self):
        super(globalPluginHandler.GlobalPlugin, self).__init__()
        self.cecitek = cecitek.Cecitek()
    
    def script_cecitekStore(self, gesture):
        self.addons = []
        modules = self.cecitek.getNvdaModules()
        notifs = self.cecitek.getNotifications()
        if len(notifs) > 0:
            ui.message(_(u"Notification: %s" %(", ".join(notifs))))
        if modules is None or len(modules) == 0:
            ui.message(_("Unable to connect to the Cecitek NVDAStore. Please check you're connected to the internet."))
            return
        for module in modules:
            m = StoreAddon(module[u'id'], module[u'name'], module[u'author'], module[u'email'], module[u'description'])
            for v in module[u'versions']:
                m.addVersion(v[u'id'], v[u'version'], v[u'changelog'], v[u'minNvdaVersion'], v[u'maxNvdaVersion'])
            if m.latestVersion != "":
                self.addons.append(m)
            
        log = ""
        for a in self.addons:
            log += "%s (%s) " %(a.name, a.latestVersion)
        logHandler.log.info("Available addons in the store: %s" % log)
        gui.mainFrame.prePopup()
        dlg = storeGui.StoreDialog(gui.mainFrame, self.cecitek, self.addons)
        dlg.Show()
        gui.mainFrame.postPopup()
        del dlg

    script_cecitekStore.__doc__ = _("Opens the NVDA Store to download, install and update NVDA add-ons.")
    def script_cecitekEpisode(self, gesture):
        episodes = self.cecitek.getEpisodes(limit=1)
        ui.message(_("Last published episode: %s") %(episodes[0]['episode_title']))
    script_cecitekEpisode.__doc__ = _("Speaks the latest published episode title from Cecitek.fr")

    __gestures = {
        "kb:nvda+shift+c": "cecitekStore",
        "kb:nvda+shift+e": "cecitekEpisode",
    }
    
