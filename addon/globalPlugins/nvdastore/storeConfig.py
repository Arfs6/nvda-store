# NVDA Store configuration manager.
# Copyright 2018 Yannick PLASSIARD, released under GPL.

# Base config section was inspired by Clip Contents Designer (Noelia Martinez).


import os
import threading
import re
import config
import gui
import wx
from logHandler import log
import addonHandler
addonHandler.initTranslation()

# Add-on config database
confspec = {
	"accountUsername": "string()",
	"accountPassword": "string()",
}
config.conf.spec["nvdastore"] = confspec

class StoreConfigDialog(wx.Dialog):
        def __init__(self, parent):
		# Translators: The title of a dialog to configure advanced WinTenApps add-on options such as update checking.
		super(StoreConfigDialog, self).__init__(parent, title=_("NVDAStore settings"))

		mainSizer = wx.BoxSizer(wx.VERTICAL)
		storeHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)

		# Translators: The label for an edit box to enter NVDAStore account username.
		labelText = _("NVDAStore &username:")
		self.username = storeHelper.addLabeledControl(labelText, wx.TextCtrl)
                self.password = storeHelper.addLabeledControl(_("&password:"), wx.TextCtrl, style=wx.TE_PASSWORD)
                self.proxy = storeHelper.addLabeledControl(_("Prox&y (host:port):"), wx.TextCtrl)
		try:
                        self.username.Clear()
                        self.password.Clear()
                        self.proxy.Clear()
                        self.username.AppendText(config.conf["nvdastore"]["username"])
                        self.password.AppendText(config.conf["nvdastore"]["password"])
                        self.proxy.AppendText(config.conf["nvdastore"]["proxy"])
                except:
                        pass
		storeHelper.addDialogDismissButtons(self.CreateButtonSizer(wx.OK | wx.CANCEL))
		self.Bind(wx.EVT_BUTTON, self.onOk, id=wx.ID_OK)
		self.Bind(wx.EVT_BUTTON, self.onCancel, id=wx.ID_CANCEL)
		mainSizer.Add(storeHelper.sizer, border=gui.guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		mainSizer.Fit(self)
		self.Sizer = mainSizer
                self.username.SetFocus()
		self.Center(wx.BOTH | (wx.CENTER_ON_SCREEN if hasattr(wx, "CENTER_ON_SCREEN") else 2))

	def onOk(self, evt):
		config.conf["nvdastore"]["username"] = self.username.Value
                config.conf["nvdastore"]["password"] = self.password.Value
                config.conf["nvdastore"]["proxy"] = self.proxy.Value
		self.Destroy()

	def onCancel(self, evt):
		self.Destroy()


def onConfigDialog(evt):
	gui.mainFrame._popupSettingsDialog(StoreConfigDialog)


