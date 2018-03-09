# *-* coding: utf-8 *-*
# nvdastore/storeUtils.py
#A part of the NVDAStore Add-on
#Copyright (C) 2017 Yannick PLASSIARD
#This file is covered by the GNU General Public License.
#See the file LICENSE for more details.

import addonHandler, core, config, ui, gui, wx, os
import logHandler
addonHandler.initTranslation()

def installAddon(storeClient, addon, closeAfter=False, silent=False):
    if silent == False:
        ui.message(_("Downloading %s") %(addon.name))
    data = storeClient.getAddonFile(addon.id, addon.versionId)
    
    if data is None:
        if silent == False:
            ui.message(_("Unable to download the add-on."))
        return False
    tmp = os.path.join(config.getUserDefaultConfigPath(), "storeDownloadedAddon.nvda-addon")
    logHandler.log.info(u"Saving to %s" %(tmp))
    f = file(tmp, "wb")
    f.write(data)
    f.close()
    path = tmp
    if path is None:
        if silent == False:
            ui.message(_("Unable to download %s") %(addon.name))
        return False
    if silent == False:
        ui.message(_("Installing"))
    try:
        bundle = addonHandler.AddonBundle(path)
    except:
        logHandler.log.error("Error opening addon bundle from %s"%path,exc_info=True)
        # Translators: The message displayed when an error occurs when opening an add-on package for adding. 
        if silent == False:
            gui.messageBox(_("Failed to open add-on package file at %s - missing file or invalid file format")%path,
		           # Translators: The title of a dialog presented when an error occurs.
		           _("Error"),
		           wx.OK | wx.ICON_ERROR)
        return False
    bundleName = bundle.manifest['name']
    prevAddon = None
    for addon in addonHandler.getAvailableAddons():
        if not addon.isPendingRemove and bundleName == addon.manifest['name']:
	    prevAddon = addon
            break
    if prevAddon:
        prevAddon.requestRemove()
    if silent is False:
        progressDialog = gui.IndeterminateProgressDialog(gui.mainFrame,
			                                 # Translators: The title of the dialog presented while an Addon is being installed.
			                                 _("Installing Add-on"),
			                                 # Translators: The message displayed while an addon is being installed.
			                                 _("Please wait while the add-on is being installed."))
        try:
            gui.ExecAndPump(addonHandler.installAddonBundle,bundle)
        except:
            logHandler.log.error("Error installing  addon bundle from %s"%addonPath,exc_info=True)
            progressDialog.done()
            del progressDialog
            # Translators: The message displayed when an error occurs when installing an add-on package.
            gui.messageBox(_("Failed to install add-on from %s")%(addon.name),
		           # Translators: The title of a dialog presented when an error occurs.
		           _("Error"),
		           wx.OK | wx.ICON_ERROR)
            return False
        progressDialog.done()
        del progressDialog
    else:
        try:
            addonHandler.installAddonBundle(bundle)
        except:
            return False
    if closeAfter:
        wx.CallLater(1, core.restart)
    return True
