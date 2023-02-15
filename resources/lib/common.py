# -*- coding: utf-8 -*-
# Python 3

import xbmcaddon
import sys

addonID = 'plugin.video.xstream'
addon = xbmcaddon.Addon(addonID)
addonName = addon.getAddonInfo('name')
    
from xbmcvfs import translatePath
addonPath = translatePath(addon.getAddonInfo('path'))
profilePath = translatePath(addon.getAddonInfo('profile'))
