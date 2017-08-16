# *-* coding: utf-8 *-*
#
# cecitek/capabilities.py
#A part of Cecitek NVDA Add-on
#Copyright (C) 2017 Yannick PLASSIARD
#This file is covered by the GNU General Public License.
#See the file LICENSE for more details.
#
# Retrieves capabilities from the system or NVDA itself that addons can check against to ensure
# they will work on the target environment before install.
#

import config
from logHandler import log
import winVersion
import winUser
from ctypes import *
from ctypes.wintypes import *

def cap_touch():
    if not config.isInstalledCopy():
	log.debugWarning("Touch only supported on installed copies")
	return False
    if (winVersion.winVersion.major*10+winVersion.winVersion.minor)<62:
	log.debugWarning("Touch only supported on Windows 8 and higher")
	return False
    maxTouches=windll.user32.GetSystemMetrics(95) #maximum touches
    if maxTouches<=0:
	log.debugWarning("No touch devices found")
	return False
    return True

