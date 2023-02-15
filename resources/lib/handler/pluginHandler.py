# -*- coding: utf-8 -*-
# Python 3
# Muss komplett für die neue settings.xml umgeschrieben werden.
# Zeile 57 deaktiviert die def __updateSettings
# Ab Zeile 97 def __updateSettings muss überarbeitet werden

import json
import os
import sys

from resources.lib.config import cConfig
from resources.lib.tools import logger
from resources.lib import common


class cPluginHandler:
    def __init__(self):
        self.addon = common.addon
        self.rootFolder = common.addonPath
        self.settingsFile = os.path.join(self.rootFolder, 'resources', 'settings.xml')
        self.profilePath = common.profilePath
        self.pluginDBFile = os.path.join(self.profilePath, 'pluginDB')
        logger.info('profile folder: %s' % self.profilePath)
        logger.info('root folder: %s' % self.rootFolder)
        self.defaultFolder = os.path.join(self.rootFolder, 'sites')
        logger.info('default sites folder: %s' % self.defaultFolder)

    def getAvailablePlugins(self):
        pluginDB = self.__getPluginDB()
        # default plugins
        update = False
        fileNames = self.__getFileNamesFromFolder(self.defaultFolder)
        for fileName in fileNames:
            plugin = {'name': '', 'icon': '', 'settings': '', 'modified': 0}
            if fileName in pluginDB:
                plugin.update(pluginDB[fileName])
            try:
                modTime = os.path.getmtime(os.path.join(self.defaultFolder, fileName + '.py'))
            except OSError:
                modTime = 0
            if fileName not in pluginDB or modTime > plugin['modified']:
                logger.info('load plugin: ' + str(fileName))
                # try to import plugin
                pluginData = self.__getPluginData(fileName, self.defaultFolder)
                if pluginData:
                    pluginData['modified'] = modTime
                    pluginDB[fileName] = pluginData
                    update = True
        # check pluginDB for obsolete entries
        deletions = []
        for pluginID in pluginDB:
            if pluginID not in fileNames:
                deletions.append(pluginID)
        for id in deletions:
            del pluginDB[id]
        if update or deletions:
            #self.__updateSettings(pluginDB) # Verursacht erstmal Fehler weil die def __updateSettings nicht überarbeitet ist !!!!
            self.__updatePluginDB(pluginDB) # Erstellt PluginDB in Addon_data
        return self.getAvailablePluginsFromDB()

    def getAvailablePluginsFromDB(self):
        plugins = []
        iconFolder = os.path.join(self.rootFolder, 'resources', 'art', 'sites')
        pluginDB = self.__getPluginDB()
        for pluginID in pluginDB:
            plugin = pluginDB[pluginID]
            pluginSettingsName = 'plugin_%s' % pluginID
            plugin['id'] = pluginID
            if 'icon' in plugin:
                plugin['icon'] = os.path.join(iconFolder, plugin['icon'])
            else:
                plugin['icon'] = ''
            # existieren zu diesem plugin die an/aus settings
            if cConfig().getSetting(pluginSettingsName) == 'true':
                plugins.append(plugin)
        return plugins

    def __updatePluginDB(self, data):
        if not os.path.exists(self.profilePath):
            os.makedirs(self.profilePath)
        file = open(self.pluginDBFile, 'w')
        json.dump(data, file)
        file.close()

    def __getPluginDB(self):
        if not os.path.exists(self.pluginDBFile):
            return dict()
        file = open(self.pluginDBFile, 'r')
        try:
            data = json.load(file)
        except ValueError:
            logger.error('pluginDB seems corrupt, creating new one')
            data = dict()
        file.close()
        return data

    def __updateSettings(self, pluginData):
        index1 = []
        index2 = []
        x = 0
        while x < len(pluginData):
            if x < len(pluginData) // 2: index1.append(sorted(pluginData)[x])
            elif x >= len(pluginData) // 2: index2.append(sorted(pluginData)[x])
            x = x + 1

        # data (dict): containing plugininformations
        xmlString = '<plugin_settings>%s</plugin_settings>'
        import xml.etree.ElementTree as ET
        tree = ET.parse(self.settingsFile)
        # find Element for plugin Settings
        # 30094 Indexseiten 1
        # 30095 Indexseiten 2
        for i in ('30094', '30095'):
            index = index1
            if i == '30095': index = index2

            pluginElem = False
            for elem in tree.findall('category'):
                if elem.attrib['label'] == i:
                    pluginElem = elem
                    break
            if pluginElem is None:
                logger.error('could not update settings, pluginElement not found')
                return False
            pluginElements = pluginElem.findall('setting')
            for elem in pluginElements:
                pluginElem.remove(elem)
                # add plugins to settings

            # for pluginID in sorted(pluginData):
            for pluginID in index:
                plugin = pluginData[pluginID]
                subEl = ET.SubElement(pluginElem, 'setting', {'type': 'lsep', 'label': plugin['name']})
                subEl.tail = '\n        '
                attrib = {'default': 'true', 'type': 'bool'}
                attrib['id'] = 'plugin_%s' % pluginID
                attrib['label'] = '30050'
                subEl = ET.SubElement(pluginElem, 'setting', attrib)
                subEl.tail = '\n        '
                #Prüfen ob der Parameter SITE_GLOBAL_SEARCH auf False steht, wenn ja, ausblenden
                if plugin['globalsearch'] == False :
                    attrib = {'default': str(plugin['globalsearch']).lower(), 'type': 'bool'}
                    attrib['id'] = 'global_search_%s' % pluginID
                    attrib['label'] = '30052'
                    attrib['visible'] = 'eq(-1,false)'
                    subEl = ET.SubElement(pluginElem, 'setting', attrib)
                    subEl.tail = '\n        '
                else:
                    attrib = {'default': str(plugin['globalsearch']).lower(), 'type': 'bool'}
                    attrib['id'] = 'global_search_%s' % pluginID
                    attrib['label'] = '30052'
                    attrib['enable'] = '!eq(-1,false)'
                    subEl = ET.SubElement(pluginElem, 'setting', attrib)
                    subEl.tail = '\n        '

                if 'settings' in plugin:
                    customSettings = []
                    try:
                        customSettings = ET.XML(xmlString % plugin['settings']).findall('setting')
                    except Exception:
                        logger.error('Parsing of custom settings for % failed.' % plugin['name'])
                    for setting in customSettings:
                        setting.tail = '\n        '
                        pluginElem.append(setting)
                subEl = ET.SubElement(pluginElem, 'setting', {'type': 'sep'})
                subEl.tail = '\n        '
            pluginElements = pluginElem.findall('setting')[-1].tail = '\n    '
            try:
                ET.dump(pluginElem)
            except Exception:
                logger.error('Settings update failed')
                return
            tree.write(self.settingsFile)

    def __getFileNamesFromFolder(self, sFolder):
        aNameList = []
        items = os.listdir(sFolder)
        for sItemName in items:
            if sItemName.endswith('.py'):
                sItemName = os.path.basename(sItemName[:-3])
                aNameList.append(sItemName)
        return aNameList

    def __getPluginData(self, fileName, defaultFolder):
        pluginData = {}
        if not defaultFolder in sys.path: sys.path.append(defaultFolder)
        try:
            plugin = __import__(fileName, globals(), locals())
            pluginData['name'] = plugin.SITE_NAME
        except Exception as e:
            logger.error("Can't import plugin: %s" % fileName)
            return False
        try:
            pluginData['icon'] = plugin.SITE_ICON
        except Exception:
            pass
        try:
            pluginData['settings'] = plugin.SITE_SETTINGS
        except Exception:
            pass
        try:
            pluginData['globalsearch'] = plugin.SITE_GLOBAL_SEARCH
        except Exception:
            pluginData['globalsearch'] = True
            pass
        return pluginData
