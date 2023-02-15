# -*- coding: utf-8 -*-
# Python 3
# Always pay attention to the translations in the menu!

import json

from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.tools import logger, cParser, cUtil
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.config import cConfig
from resources.lib.gui.gui import cGui


SITE_IDENTIFIER = 'cinemathek'
SITE_NAME = 'Cinemathek'
SITE_ICON = 'cinemathek.png'
URL_MAIN = 'https://cinemathek.net/'
URL_MOVIES = URL_MAIN + 'movies/'
URL_SERIES = URL_MAIN + 'tvshows/'
URL_SEARCH = URL_MAIN + '?s=%s'


def load():
    logger.info('Load %s' % SITE_NAME)
    params = ParameterHandler()
    params.setParam('sUrl', URL_MOVIES)
    cGui().addFolder(cGuiElement(cConfig().getLocalizedString(30502), SITE_IDENTIFIER, 'showEntries'), params)  # Movies  
    params.setParam('sUrl', URL_SERIES)
    cGui().addFolder(cGuiElement(cConfig().getLocalizedString(30511), SITE_IDENTIFIER, 'showEntries'), params)  # Series  
    params.setParam('sUrl', URL_MAIN)
    cGui().addFolder(cGuiElement(cConfig().getLocalizedString(30506), SITE_IDENTIFIER, 'showGenre'), params)    # Genre    
    cGui().addFolder(cGuiElement(cConfig().getLocalizedString(30520), SITE_IDENTIFIER, 'showSearch'))           # Search
    cGui().setEndOfDirectory()
  


def showGenre():
    params = ParameterHandler()
    sUrl = params.getValue('sUrl')
    sHtmlContent = cRequestHandler(sUrl).request()
    pattern = '<li class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children menu-item-243">.*?</ul>'
    isMatch, aResult = cParser.parseSingleResult(sHtmlContent, '<li class="menu-item menu-item-type-taxonomy.*?href="(https[^"]+).*?>([^<]+)')
    
    for sUrl, sName in aResult:
        if sUrl.startswith('/'):
            sUrl = URL_MAIN + sUrl
        params.setParam('sUrl', sUrl)
        cGui().addFolder(cGuiElement(sName, SITE_IDENTIFIER, 'showEntries'), params)
    cGui().setEndOfDirectory()


def showEntries(entryUrl=False, sGui=False, sSearchText=False):
    oGui = sGui if sGui else cGui()
    params = ParameterHandler()
    isTvshow = False    
    if not entryUrl: entryUrl = params.getValue('sUrl')
    oRequest = cRequestHandler(entryUrl, ignoreErrors=sGui is not False) 
    sHtmlContent = oRequest.request()
    # Für Filme und Serien Content
    pattern = '<article id=.*?'  # container start
    pattern += '<img src="([^"]+).*?'  # sThumbnail
    pattern += 'href="([^"]+).*?'  # url  
    pattern += '>([^<]+).*?'  # name 
    # pattern += '<div class="texto">([^<]+).*?'  # desc
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch:
        # Für die Suche von Filme und Serien
        pattern = '<article.*?'  # container start
        pattern += '<img src="([^"]+).*?'  # sThumbnail
        pattern += 'href="([^"]+).*?'  # url  
        pattern += '>([^<]+).*?'  # name
        isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch:
        if not sGui: oGui.showInfo()
        return

    total = len(aResult)
    for sThumbnail, sUrl, sName in aResult:  #for sThumbnail, sUrl, sName, sDesc in aResult:
        if sSearchText and not cParser.search(sSearchText, sName):
            continue 
        isTvshow, aResult = cParser.parse(sUrl, 'tvshows') # Muss nur im Serien Content auffindbar sein
        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showSeasons' if isTvshow else 'showHosters')
        oGuiElement.setMediaType('tvshow' if isTvshow else 'movie')  
        oGuiElement.setThumbnail(sThumbnail)
        #oGuiElement.setDescription(sDesc)
        params.setParam('sThumbnail', sThumbnail)
        params.setParam('entryUrl', sUrl)
        params.setParam('sName', sName)
        oGui.addFolder(oGuiElement, params, isTvshow, total)

    if not sGui and not sSearchText:
        isMatchNextPage, sNextUrl = cParser.parseSingleResult(sHtmlContent, '<link[^>]*rel="next"[^>]*href="([^"]+)"') # Nächste Seite
        if isMatchNextPage:
            params.setParam('sUrl', sNextUrl)
            oGui.addNextPage(SITE_IDENTIFIER, 'showEntries', params)

        oGui.setView('tvshows' if isTvshow else 'movies')
        oGui.setEndOfDirectory()


def showSeasons():
    params = ParameterHandler()
    entryUrl = params.getValue('entryUrl')
    sHtmlContent = cRequestHandler(entryUrl).request()
    isMatch, aResult = cParser.parse(sHtmlContent, 'Staffel ([\d]+)') # Sucht den Staffel Eintrag und d fügt die Anzahl hinzu
    if not isMatch:
        cGui().showInfo()
        return

    isDesc, sDesc = cParser.parseSingleResult(sHtmlContent, 'class="wp-content">(.*?)</p>') # Staffel Beschreibung
    total = len(aResult)
    for sSeason in aResult:
        oGuiElement = cGuiElement('Staffel ' + sSeason, SITE_IDENTIFIER, 'showEpisodes')
        oGuiElement.setMediaType('season')
        oGuiElement.setSeason(sSeason)
        oGuiElement.setThumbnail(params.getValue('sThumbnail'))
        if isDesc:
            oGuiElement.setDescription(sDesc)
        params.setParam('Season', sSeason)
        cGui().addFolder(oGuiElement, params, True, total)
    cGui().setView('seasons')
    cGui().setEndOfDirectory()


def showEpisodes(): # einfache Abrage wird wenns mal funktioniert erweitert für sName,sThumb,Desc
    params = ParameterHandler()
    entryUrl = params.getValue('entryUrl')
    sSeason = params.getValue('Season')
    sHtmlContent = cRequestHandler(entryUrl).request()
    pattern = '>Staffel %s <i>.*?</ul>' % sSeason
    isMatch, sContainer = cParser.parseSingleResult(sHtmlContent, pattern)
    if isMatch:
        pattern = '''<li class='mark-([\d]+).*?<img src='([^']+).*?<a href='([^']+).*?>([^<]+)'''
        isMatch, aResult = cParser.parse(sContainer, pattern)

    isDesc, sDesc = cParser.parseSingleResult(sHtmlContent, 'class="wp-content">(.*?)</p>') # Staffel Beschreibung
    total = len(aResult)
    for sEpisode, sThumbnail, sUrl, sName in aResult:
        oGuiElement = cGuiElement('Episode ' + sEpisode + ' - ' + sName, SITE_IDENTIFIER, 'showHosters')
        oGuiElement.setSeason(sSeason)
        oGuiElement.setEpisode(sEpisode)
        oGuiElement.setMediaType('episode')
        oGuiElement.setThumbnail(sThumbnail)
        if isDesc:
            oGuiElement.setDescription(sDesc)
        params.setParam('sName', sName)
        params.setParam('entryUrl', sUrl)
        cGui().addFolder(oGuiElement, params, False, total)
    cGui().setView('episodes')
    cGui().setEndOfDirectory()


def showHosters():
    hosters = []
    sUrl = ParameterHandler().getValue('entryUrl')
    sHtmlContent = cRequestHandler(sUrl).request()
    pattern = "player-option-\d.*?type.*?'([^']+).*?(\d+).*?(\d)"
    isMatch, aResult = cParser().parse(sHtmlContent, pattern)
    if isMatch:
        for i in aResult:
            sUrl = 'https://cinemathek.net/wp-json/dooplayer/v2/%s/%s/%s' % (i[1], i[0], i[2])
            hoster = {'link': sUrl, 'name': 'Cinemathek '+ i[2]}
            hosters.append(hoster)
    if hosters:
        hosters.append('getHosterUrl')
    return hosters


def getHosterUrl(sUrl=False):
    sUrl = json.loads(cRequestHandler(sUrl).request()).get("embed_url")
    return [{'streamUrl': sUrl, 'resolved': False}]


def showSearch():
    oGui = cGui()
    sSearchText = oGui.showKeyBoard()
    if not sSearchText: return
    _search(False, sSearchText)
    oGui.setEndOfDirectory()


def _search(oGui, sSearchText):
    showEntries(URL_SEARCH % cParser().quotePlus(sSearchText), oGui, sSearchText)
