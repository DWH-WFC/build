# -*- coding: utf-8 -*-
# Python 3
# Always pay attention to the translations in the menu!

import re
import sys

from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.tools import logger, cParser
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.config import cConfig
from resources.lib.gui.gui import cGui
from json import loads


SITE_IDENTIFIER = 'kinokiste'
SITE_NAME = 'KinoKiste'
SITE_ICON = 'kinokiste.png'
#SITE_GLOBAL_SEARCH = False     # Global search function is thus deactivated!
URL_MAIN = 'https://api.tmdb.club/data/browse/?lang=%s&type=%s&order_by=%s&page=%s'     # 2 = deutsch / 3 = englisch / all = Alles
URL_SEARCH = 'https://api.tmdb.club/data/browse/?lang=%s&keyword=%s&page=%s'
URL_THUMBNAIL = 'https://image.tmdb.org/t/p/w300%s'
URL_WATCH = 'https://api.tmdb.club/data/watch/?_id=%s'
ORIGIN = 'https://www1.movie2k.ch'
REFERER = ORIGIN + '/'


def load():
    logger.info('Load %s' % SITE_NAME)
    params = ParameterHandler()
    sLanguage = cConfig().getSetting('prefLanguage')
    # remap language
    if sLanguage == '0':
        sLanguage = '2'
    elif sLanguage == '1':
        sLanguage = '3'
    else:
        sLanguage = 'all'
    params.setParam('sLanguage', sLanguage)
    cGui().addFolder(cGuiElement('Filme', SITE_IDENTIFIER, 'showMovieMenu'), params)
    cGui().addFolder(cGuiElement('Serien', SITE_IDENTIFIER, 'showSeriesMenu'), params)
    cGui().addFolder(cGuiElement('Suche', SITE_IDENTIFIER, 'showSearch'), params)
    cGui().setEndOfDirectory()


def _cleanTitle(sTitle):
    sTitle = re.sub("[\xE4]", 'ae', sTitle)
    sTitle = re.sub("[\xFC]", 'ue', sTitle)
    sTitle = re.sub("[\xF6]", 'oe', sTitle)
    sTitle = re.sub("[\xC4]", 'Ae', sTitle)
    sTitle = re.sub("[\xDC]", 'Ue', sTitle)
    sTitle = re.sub("[\xD6]", 'Oe', sTitle)
    sTitle = re.sub("[\x00-\x1F\x80-\xFF]", '', sTitle)
    return sTitle


def _getQuality(sQuality):
    isMatch, aResult = cParser.parse(sQuality, '(HDCAM|HD|WEB|BLUERAY|BRRIP|DVD|TS|SD|CAM)', 1, True)
    if isMatch:
        return aResult[0]
    else:
        return sQuality


def showMovieMenu():
    params = ParameterHandler()
    sLanguage = params.getValue('sLanguage')
    params.setParam('sUrl', URL_MAIN % (sLanguage, 'movies', 'featured', '1'))
    cGui().addFolder(cGuiElement('Kinofilme', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % (sLanguage, 'movies', 'releases', '1'))
    cGui().addFolder(cGuiElement('Filme (neu)', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % (sLanguage, 'movies', 'trending', '1'))
    cGui().addFolder(cGuiElement('Filme (trend)', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % (sLanguage, 'movies', 'updates', '1'))
    cGui().addFolder(cGuiElement('Filme (aktualisiert)', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % (sLanguage, 'movies', 'requested', '1'))
    cGui().addFolder(cGuiElement('Filme (nachgefragt)', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % (sLanguage, 'movies', 'rating', '1'))
    cGui().addFolder(cGuiElement('Filme (IMDB)', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % (sLanguage, 'movies', 'votes', '1'))
    cGui().addFolder(cGuiElement('Filme (bewertung)', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % (sLanguage, 'movies', 'views', '1'))
    cGui().addFolder(cGuiElement('Filme (aufrufe)', SITE_IDENTIFIER, 'showEntries'), params)
    cGui().setEndOfDirectory()


def showSeriesMenu():
    params = ParameterHandler()
    sLanguage = params.getValue('sLanguage')
    params.setParam('sUrl', URL_MAIN % (sLanguage, 'tvseries', 'releases', '1'))
    cGui().addFolder(cGuiElement('Serien (neu)', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % (sLanguage, 'tvseries', 'trending', '1'))
    cGui().addFolder(cGuiElement('Serien (trend)', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % (sLanguage, 'tvseries', 'updates', '1'))
    cGui().addFolder(cGuiElement('Serien (aktualisiert)', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % (sLanguage, 'tvseries', 'requested', '1'))
    cGui().addFolder(cGuiElement('Serien (nachgefragt)', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % (sLanguage, 'tvseries', 'rating', '1'))
    cGui().addFolder(cGuiElement('Serien (IMDB)', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % (sLanguage, 'tvseries', 'votes', '1'))
    cGui().addFolder(cGuiElement('Serien (bewertung)', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % (sLanguage, 'tvseries', 'views', '1'))
    cGui().addFolder(cGuiElement('Serien (aufrufe)', SITE_IDENTIFIER, 'showEntries'), params)
    cGui().setEndOfDirectory()


def showEntries(entryUrl=False, sGui=False, sSearchText=False):
    oGui = sGui if sGui else cGui()
    params = ParameterHandler()
    isTvshow = False
    sThumbnail = ''
    sLanguage = params.getValue('sLanguage')
    if not entryUrl: entryUrl = params.getValue('sUrl')
    try:
        oRequest = cRequestHandler(entryUrl)
        oRequest.addHeaderEntry('Referer', REFERER)
        oRequest.addHeaderEntry('Origin', ORIGIN)
        sJson = oRequest.request()
        aJson = loads(sJson)
    except:
        if not sGui: oGui.showInfo()
        return

    if 'movies' not in aJson or len(aJson['movies']) == 0:
        if not sGui: oGui.showInfo()
        return

    total = 0
    # ignore movies which does not contain any streams
    for movie in aJson['movies']:
        if 'streams' in movie:
            total += 1
    for movie in aJson['movies']:
        if 'streams' not in movie:
            continue
        if sys.version_info[0] == 2:
            sTitle = _cleanTitle(movie['title'])
        else:
            sTitle = movie['title']
        if sSearchText and not cParser().search(sSearchText, sTitle):
            continue
        if (('tv' in movie) and (movie['tv'] == 1)):
            isTvshow = True
        oGuiElement = cGuiElement(sTitle, SITE_IDENTIFIER, 'showEpisodes' if isTvshow else 'showHosters')
        if 'poster_path_season' in movie:
            sThumbnail = URL_THUMBNAIL % movie['poster_path_season']
        elif 'poster_path' in movie:
            sThumbnail = URL_THUMBNAIL % movie['poster_path']
        elif 'backdrop_path' in movie:
            sThumbnail = URL_THUMBNAIL % movie['backdrop_path']
        oGuiElement.setThumbnail(sThumbnail)
        if 'storyline' in movie:
            oGuiElement.setDescription(movie['storyline'])
        elif 'overview' in movie:
            oGuiElement.setDescription(movie['overview'])
        if 'year' in movie:
            oGuiElement.setYear(movie['year'])
        if 'quality' in movie:
            oGuiElement.setQuality(_getQuality(movie['quality']))
        if 'rating' in movie:
            oGuiElement.addItemValue('rating', movie['rating'].replace(',', '.'))
        if 'lang' in movie:
            if (sLanguage != '3' and movie['lang'] == 2):
                oGuiElement.setLanguage('DE')
            elif (sLanguage != '2' and movie['lang'] == 3):
                oGuiElement.setLanguage('EN')
        oGuiElement.setMediaType('tvshows' if isTvshow else 'movie')
        if 'runtime' in movie:
            isMatch, sRuntime = cParser.parseSingleResult(movie['runtime'], '\d+')
            if isMatch:
                oGuiElement.addItemValue('duration', sRuntime)
        params.setParam('entryUrl', URL_WATCH % movie['_id'])
        params.setParam('sName', sTitle)
        params.setParam('sThumbnail', sThumbnail)
        oGui.addFolder(oGuiElement, params, isTvshow, total)

    if not sGui and not sSearchText:
        curPage = aJson['pager']['currentPage']
        if curPage < aJson['pager']['totalPages']:
            sNextUrl = entryUrl.replace('page=' + str(curPage), 'page=' + str(curPage + 1))
            params.setParam('sUrl', sNextUrl)
            oGui.addNextPage(SITE_IDENTIFIER, 'showEntries', params)
        oGui.setView('tvshows' if isTvshow else 'movies')
        oGui.setEndOfDirectory()


def showEpisodes():
    aEpisodes = []
    params = ParameterHandler()
    sUrl = params.getValue('entryUrl')
    sThumbnail = params.getValue("sThumbnail")
    try:
        oRequest = cRequestHandler(sUrl)
        oRequest.addHeaderEntry('Referer', REFERER)
        oRequest.addHeaderEntry('Origin', ORIGIN)
        sJson = oRequest.request()
        aJson = loads(sJson)
    except:
        cGui().showInfo()
        return

    if 'streams' not in aJson or len(aJson['streams']) == 0:
        cGui().showInfo()
        return

    for stream in aJson['streams']:
        if 'e' in stream:
            aEpisodes.append(stream['e'])
    if aEpisodes:
        aEpisodesSorted = sorted(list(set(aEpisodes)))

        total = len(aEpisodesSorted)
        for sEpisode in aEpisodesSorted:
            oGuiElement = cGuiElement('Episode ' + str(sEpisode), SITE_IDENTIFIER, 'showHosters')
            oGuiElement.setThumbnail(sThumbnail)
            if 's' in aJson:
                oGuiElement.setSeason(aJson['s'])
            oGuiElement.setTVShowTitle('Episode ' + str(sEpisode))
            oGuiElement.setEpisode(sEpisode)
            oGuiElement.setMediaType('episode')
            cGui().addFolder(oGuiElement, params, False, total)
    cGui().setView('episodes')
    cGui().setEndOfDirectory()


def showHosters():
    hosters = []
    params = ParameterHandler()
    sUrl = params.getValue('entryUrl')
    sEpisode = params.getValue('episode')
    try:
        oRequest = cRequestHandler(sUrl)
        oRequest.addHeaderEntry('Referer', REFERER)
        oRequest.addHeaderEntry('Origin', ORIGIN)
        sJson = oRequest.request()
    except:
        return hosters
    if sJson:
        aJson = loads(sJson)
        if 'streams' in aJson:
            i = 0
            for stream in aJson['streams']:
                if (('e' not in stream) or (str(sEpisode) == str(stream['e']))):
                    sHoster = str(i) + ':'
                    isMatch, aName = cParser.parse(stream['stream'], '//([^/]+)/')
                    if isMatch:
                        sName = aName[0][:aName[0].rindex('.')]
                        sHoster = sHoster + ' ' + sName
                    if 'release' in stream:
                        sHoster = sHoster + ' [' + _getQuality(stream['release']) + ']'
                    hoster = {'link': stream['stream'], 'name': sHoster}
                    hosters.append(hoster)
                    i += 1
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
    sLanguage = ParameterHandler().getValue('sLanguage')
    showEntries(URL_SEARCH % (sLanguage, cParser().quotePlus(sSearchText), '1'), oGui, sSearchText)
