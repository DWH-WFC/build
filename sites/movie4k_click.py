# -*- coding: utf-8 -*-
# Python 3
# Always pay attention to the translations in the menu!

from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.tools import logger, cParser
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.config import cConfig
from resources.lib.gui.gui import cGui

SITE_IDENTIFIER = 'movie4k_click'
SITE_NAME = 'Movie4k Click'
SITE_ICON = 'movie4k_click.png'
#SITE_GLOBAL_SEARCH = False     # Global search function is thus deactivated!
#URL_MAIN = 'https://movie4k.pics'
URL_MAIN = str(cConfig().getSetting('movie4k-domain', 'https://movie4k.pics/'))
URL_KINO = URL_MAIN + 'aktuelle-kinofilme-im-kino'
URL_MOVIES = URL_MAIN + 'kinofilme-online'
URL_SERIES = URL_MAIN + 'serienstream-deutsch'


def checkDomain():
    oRequest = cRequestHandler(URL_MAIN, caching=False)
    oRequest.request()
    Domain = str(oRequest.getStatus())
    if oRequest.getStatus() == '301':
        url = oRequest.getRealUrl()
        if not url.startswith('http'):
            url = 'https://' + url
        # Setzt aktuelle Domain in der settings.xml
        cConfig().setSetting('movie4k-domain', str(url))


def load(): # Menu structure of the site plugin
    logger.info('Load %s' % SITE_NAME)
    params = ParameterHandler()
    params.setParam('sUrl', URL_KINO)
    cGui().addFolder(cGuiElement(cConfig().getLocalizedString(30501), SITE_IDENTIFIER, 'showEntries'), params)  # Current films in the cinema  
    params.setParam('sUrl', URL_MOVIES)
    cGui().addFolder(cGuiElement(cConfig().getLocalizedString(30502), SITE_IDENTIFIER, 'showEntries'), params)  # Movies
    params.setParam('sUrl', URL_SERIES)
    cGui().addFolder(cGuiElement(cConfig().getLocalizedString(30511), SITE_IDENTIFIER, 'showEntries'), params)  # Series
    params.setParam('sCont', 'Jahr')
    cGui().addFolder(cGuiElement(cConfig().getLocalizedString(30508), SITE_IDENTIFIER, 'showValue'), params)    # Release Year  
    params.setParam('sCont', 'Land')
    cGui().addFolder(cGuiElement(cConfig().getLocalizedString(30402), SITE_IDENTIFIER, 'showValue'), params)    # Countries
    params.setParam('sCont', 'Genre')
    cGui().addFolder(cGuiElement(cConfig().getLocalizedString(30506), SITE_IDENTIFIER, 'showValue'), params)    # Genre
    cGui().addFolder(cGuiElement(cConfig().getLocalizedString(30520), SITE_IDENTIFIER, 'showSearch'))   # Search
    cGui().setEndOfDirectory()


def showValue():
    params = ParameterHandler()
    sHtmlContent = cRequestHandler(URL_MAIN).request()
    isMatch, sContainer = cParser.parseSingleResult(sHtmlContent, '%s<.*?</ul>' % params.getValue('sCont'))
    if isMatch:
        pattern = 'href="([^"]+).*?true">([^"]+)</a>'
        isMatch, aResult = cParser.parse(sContainer, pattern)
    if not isMatch:
        cGui().showInfo()
        return

    for sUrl, sName in aResult:
        if sUrl.startswith('/'):
            sUrl = URL_MAIN + sUrl
        if 'ino' in sName or 'erien' in sName:
            continue
        params.setParam('sUrl', sUrl)
        cGui().addFolder(cGuiElement(sName, SITE_IDENTIFIER, 'showEntries'), params)
    cGui().setEndOfDirectory()


def showEntries(entryUrl=False, sGui=False, sSearchText=False):
    oGui = sGui if sGui else cGui()
    params = ParameterHandler()
    # >>>> Domain Check <<<<<
    oRequest = cRequestHandler(URL_MAIN, ignoreErrors=True)
    oRequest.request()
    Domain = str(oRequest.getStatus())
    if not Domain == '200':
        checkDomain()
    # >>>> Ende Domain Check <<<<<     
    if not entryUrl: entryUrl = params.getValue('sUrl')
    oRequest = cRequestHandler(entryUrl, ignoreErrors=(sGui is not False))
    if sSearchText:
        oRequest.addParameters('story', sSearchText)
        oRequest.addParameters('do', 'search')
        oRequest.addParameters('subaction', 'search')
    sHtmlContent = oRequest.request() 
    pattern = 'movie-item.*?href="([^"]+).*?<h3>([^<]+).*?<ul><li>([^<]+).*?white">([^<]+).*?data-src="/([^"]+)'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch:
        if not sGui: oGui.showInfo()
        return

    total = len(aResult)
    for sUrl, sName, sQuality, sYear, sThumbnail in aResult:
        sThumbnail = URL_MAIN + sThumbnail
        if sSearchText and not cParser().search(sSearchText, sName):
            continue
        isTvshow = True if 'taffel' in sName else False
        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showEpisodes' if isTvshow else 'showHosters')
        oGuiElement.setMediaType('tvshow' if isTvshow else 'movie')
        oGuiElement.setThumbnail(sThumbnail)
        oGuiElement.setQuality(sQuality)
        oGuiElement.setYear(sYear)
        params.setParam('entryUrl', sUrl)
        params.setParam('sName', sName)
        params.setParam('sThumbnail', sThumbnail)
        oGui.addFolder(oGuiElement, params, isTvshow, total)
    if not sGui:
        isMatchNextPage, sNextUrl = cParser().parseSingleResult(sHtmlContent, 'Nächste[^>]Seite">[^>]*<a[^>]href="([^"]+)')
        if isMatchNextPage:
            if '/xfsearch/' not in entryUrl:
                params.setParam('sUrl', sNextUrl)
                oGui.addNextPage(SITE_IDENTIFIER, 'showEntries', params)
        oGui.setView('tvshows' if 'taffel' in sName else 'movies')
        oGui.setEndOfDirectory()


def showEpisodes():
    params = ParameterHandler()
    sThumbnail = params.getValue('sThumbnail')
    entryUrl = params.getValue('entryUrl')
    sHtmlContent = cRequestHandler(entryUrl).request()
    pattern = 'id="serie-(\d+)[^>](\d+).*?href="#">([^<]+)'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch:
        cGui().showInfo()
        return

    isShow, sTVShowTitle = cParser.parseSingleResult(sHtmlContent, '<title>([^-]+)')
    isDesc, sDesc = cParser.parseSingleResult(sHtmlContent, 'name="description" content="([^"]+)')
    total = len(aResult)
    for sNr, eNr, sName in aResult:
        oGuiElement = cGuiElement('Folge ' + eNr, SITE_IDENTIFIER, 'showHosters')
        if isShow:
            oGuiElement.setTVShowTitle(sTVShowTitle.strip())
        oGuiElement.setSeason(sNr)
        oGuiElement.setEpisode(eNr)
        oGuiElement.setThumbnail(sThumbnail)
        oGuiElement.setMediaType('episode')
        if isDesc:
            oGuiElement.setDescription(sDesc)
        params.setParam('sEpisodeNr', sName)
        params.setParam('entryUrl', entryUrl)
        cGui().addFolder(oGuiElement, params, False, total)
    cGui().setView('episodes')
    cGui().setEndOfDirectory()


def showHosters():
    hosters = []
    sHtmlContent = cRequestHandler(ParameterHandler().getValue('entryUrl')).request()
    if ParameterHandler().getValue('sEpisodeNr'):
        pass
        pattern = '%s<.*?</ul>' % ParameterHandler().getValue('sEpisodeNr')
        isMatch, sHtmlContent = cParser.parseSingleResult(sHtmlContent, pattern)
    isMatch, aResult = cParser().parse(sHtmlContent, 'link="([^"]+)">([^<]+)')
    if isMatch:
        for sUrl, sName in aResult:
            if cConfig().isBlockedHoster(sName, checkResolver=True): continue # Hoster aus settings.xml oder deaktivierten Resolver ausschließen
            if 'railer' in sName: 
                continue
            elif 'vod' in sUrl:
                continue
            if sUrl.startswith('//'):
                sUrl = 'https:' + sUrl
            hoster = {'link': sUrl, 'name': sName}
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
    showEntries(URL_MAIN, oGui, sSearchText)
