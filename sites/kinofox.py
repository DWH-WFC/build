# -*- coding: utf-8 -*-
# Python 3
# Always pay attention to the translations in the menu!

from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.tools import logger, cParser
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.config import cConfig
from resources.lib.gui.gui import cGui

SITE_IDENTIFIER = 'kinofox'
SITE_NAME = 'KinoFox'
SITE_ICON = 'kinofox.png'
#SITE_GLOBAL_SEARCH = False     # Global search function is thus deactivated!
URL_MAIN = 'https://kinofox.su'
URL_SEARCH = URL_MAIN + '/index.php?do=search'


def load(): # Menu structure of the site plugin
    logger.info('Load %s' % SITE_NAME)
    params = ParameterHandler()
    params.setParam('sUrl', URL_MAIN)
    cGui().addFolder(cGuiElement(cConfig().getLocalizedString(30502), SITE_IDENTIFIER, 'showEntries'), params)  # Movies
    params.setParam('sCont', 'Genre')
    cGui().addFolder(cGuiElement(cConfig().getLocalizedString(30506), SITE_IDENTIFIER, 'showValue'), params)    # Genre
    params.setParam('sCont', 'Release Jahre')
    cGui().addFolder(cGuiElement(cConfig().getLocalizedString(30508), SITE_IDENTIFIER, 'showValue'), params)    # Release Year
    cGui().addFolder(cGuiElement(cConfig().getLocalizedString(30520), SITE_IDENTIFIER, 'showSearch'))   # Search
    cGui().setEndOfDirectory()


def showValue():
    params = ParameterHandler()
    sHtmlContent = cRequestHandler(URL_MAIN).request()
    isMatch, sContainer = cParser.parseSingleResult(sHtmlContent, 'nav-title">%s<.*?</ul>' % params.getValue('sCont'))
    if isMatch:
        pattern = ' href="([^"]+)">([^<]+)'
        isMatch, aResult = cParser.parse(sContainer, pattern)
    if not isMatch:
        cGui().showInfo()
        return

    for sUrl, sName in aResult:
        sUrl = URL_MAIN + sUrl
        if 'ctionfilm' in sName:
            continue
        if 'antasyfilm' in sName:
            continue
        if 'amilienfilm' in sName:
            continue
        if 'riminalfilm' in sName:
            continue
        if 'omödie' in sName:
            continue
        if 'riegsfilm' in sName:
            continue
        if 'orrorfilm' in sName:
            continue
        if 'istorienfilm' in sName:
            continue
        if 'ystery' in sName:
            continue
        if 'usikfilm' in sName:
            continue
        if 'hriller' in sName:
            continue
        if 'estern' in sName:
            continue             
        if 'erian' in sName:
            continue
        params.setParam('sUrl', sUrl)
        cGui().addFolder(cGuiElement(sName, SITE_IDENTIFIER, 'showEntries'), params)
    cGui().setEndOfDirectory()


def showEntries(entryUrl=False, sGui=False, sSearchText=False):
    oGui = sGui if sGui else cGui()
    params = ParameterHandler()
    if not entryUrl: entryUrl = params.getValue('sUrl')

    oRequest = cRequestHandler(entryUrl, ignoreErrors=sGui is not False)
    if sSearchText:
        oRequest.addParameters('do', 'search')
        oRequest.addParameters('subaction', 'search')
        oRequest.addParameters('search_start', '0')
        oRequest.addParameters('full_search', '1')
        oRequest.addParameters('result_from', '1')
        oRequest.addParameters('story', sSearchText)
        oRequest.addParameters('titleonly', '3')
    sHtmlContent = oRequest.request() 
    pattern = 'short clearfix.*?href="([^"]+).*?title">([^<]+).*?img src="([^"]+).*?short-label sl-y">([^<]+)'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch:
        if not sGui: oGui.showInfo()
        return

    total = len(aResult)
    for sUrl, sName, sThumbnail, sQuality in aResult:
        if sSearchText and not cParser().search(sSearchText, sName):
            continue
        if 'taffel' in sName:
            continue
        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showHosters')
        oGuiElement.setQuality(sQuality)
        oGuiElement.setMediaType('movie')
        if sThumbnail.startswith('/'):
            oGuiElement.setThumbnail(URL_MAIN + sThumbnail)
        else:
            oGuiElement.setThumbnail(sThumbnail)
        params.setParam('entryUrl', sUrl)
        oGui.addFolder(oGuiElement, params, False, total)
    if not sGui:
        isMatchNextPage, sNextUrl = cParser.parseSingleResult(sHtmlContent, 'class="pnext">[^>]*<a[^>]href="([^"]+)">')
        if isMatchNextPage:
            params.setParam('sUrl', sNextUrl)
            oGui.addNextPage(SITE_IDENTIFIER, 'showEntries', params)
        oGui.setView('movies')
        oGui.setEndOfDirectory()


def showHosters():
    hosters = []
    sUrl = ParameterHandler().getValue('entryUrl')
    sHtmlContent = cRequestHandler(sUrl).request()
    isMatch, aResult = cParser.parse(sHtmlContent, 'iframe src="([^"]+)')
    if isMatch:
        for sUrl in aResult:
            sName = cParser.urlparse(sUrl)
            if cConfig().isBlockedHoster(sName, checkResolver=True): continue # Hoster aus settings.xml oder deaktivierten Resolver ausschließen            
            hoster = {'link': sUrl, 'name': cParser.urlparse(sUrl)}
            hosters.append(hoster)
    if hosters:
        hosters.append('getHosterUrl')
    return hosters


def getHosterUrl(sUrl=False):
    return [{'streamUrl': sUrl, 'resolved': False}]


def showSearch():
    sSearchText = cGui().showKeyBoard()
    if not sSearchText: return
    _search(False, sSearchText)
    cGui().setEndOfDirectory()


def _search(oGui, sSearchText):
    showEntries(URL_SEARCH, oGui, sSearchText)
