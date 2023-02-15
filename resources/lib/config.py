# -*- coding: utf-8 -*-
# Python 3

import xbmcaddon
import resolveurl as resolver

from resources.lib import common
from urllib.parse import urlparse


class cConfig:
    def __init__(self):
        self.__addon = xbmcaddon.Addon(common.addonID)
        self.__aLanguage = self.__addon.getLocalizedString

    def showSettingsWindow(self):
        self.__addon.openSettings()

    def getSetting(self, sName, default=''):
        result = self.__addon.getSetting(sName)
        if result:
            return result
        else:
            return default

    def setSetting(self, id, value):
        if id and value:
            self.__addon.setSetting(id, value)

    def getLocalizedString(self, sCode):
        return self.__aLanguage(sCode)
        
    def isBlockedHoster(self, domain, checkResolver=True ):
        domain = urlparse(domain).path if urlparse(domain).hostname == None else urlparse(domain).hostname
        hostblockDict = ['flashx','streamlare','evoload']  # permanenter Block
        blockedHoster = cConfig().getSetting('blockedHoster').split(',')  # aus setting.xml blockieren
        if len(blockedHoster) <= 1: blockedHoster = cConfig().getSetting('blockedHoster').split()
        for i in blockedHoster: hostblockDict.append(i.lower())
        for i in hostblockDict:
            if i in domain.lower() or i.split('.')[0] in domain.lower(): return True
        if checkResolver:
            if resolver.relevant_resolvers(domain=domain) == []: return True    # Überprüfung in resolveUrl
        return False
