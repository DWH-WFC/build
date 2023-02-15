# -*- coding: utf-8 -*-
# Python 3
# Always pay attention to the translations in the menu!

import base64
import binascii
import json
import random
import string

from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.tools import logger, cParser, cUtil
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.config import cConfig
from resources.lib.gui.gui import cGui
from resources.lib import jsunpacker
from itertools import zip_longest as ziplist

SITE_IDENTIFIER = 'kinoger'
SITE_NAME = 'Kinoger'
SITE_ICON = 'kinoger.png'
#SITE_GLOBAL_SEARCH = False     # Global search function is thus deactivated!
URL_MAIN = 'https://' + cConfig().getSetting('kinoger-domain')
URL_SERIES = URL_MAIN + '/stream/serie/'


def load(): # Menu structure of the site plugin
    logger.info('Load %s' % SITE_NAME)
    params = ParameterHandler()
    params.setParam('sUrl', URL_MAIN)
    cGui().addFolder(cGuiElement(cConfig().getLocalizedString(30500), SITE_IDENTIFIER, 'showEntries'), params)    # New
    params.setParam('sUrl', URL_SERIES)
    cGui().addFolder(cGuiElement(cConfig().getLocalizedString(30511), SITE_IDENTIFIER, 'showEntries'), params)  # Series
    cGui().addFolder(cGuiElement(cConfig().getLocalizedString(30506), SITE_IDENTIFIER, 'showGenre'))    # Genre
    cGui().addFolder(cGuiElement(cConfig().getLocalizedString(30520), SITE_IDENTIFIER, 'showSearch'))   # Search
    cGui().setEndOfDirectory()


def showGenre():
    params = ParameterHandler()
    sHtmlContent = cRequestHandler(URL_MAIN).request()
    pattern = '<li[^>]class="links"><a href="([^"]+).*?/>([^<]+)</a>'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch:
        cGui().showInfo()
        return

    for sUrl, sName in aResult:
        params.setParam('sUrl', URL_MAIN + sUrl)
        cGui().addFolder(cGuiElement(sName, SITE_IDENTIFIER, 'showEntries'), params)
    cGui().setEndOfDirectory()


def showEntries(entryUrl=False, sGui=False, sSearchText=False):
    oGui = sGui if sGui else cGui()
    params = ParameterHandler()
    if not entryUrl: entryUrl = params.getValue('sUrl')
    oRequest = cRequestHandler(entryUrl, ignoreErrors=(sGui is not False))
    if sSearchText:
        oRequest.addParameters('story', sSearchText)
        oRequest.addParameters('do', 'search')
        oRequest.addParameters('subaction', 'search')
        oRequest.addParameters('x', '0')
        oRequest.addParameters('y', '0')
        oRequest.addParameters('titleonly', '3')
        oRequest.addParameters('submit', 'submit')
    else:
        oRequest.addParameters('dlenewssortby', 'date')
        oRequest.addParameters('dledirection', 'desc')
        oRequest.addParameters('set_new_sort', 'dle_sort_main')
        oRequest.addParameters('set_direction_sort', 'dle_direction_main')
    sHtmlContent = oRequest.request()
    pattern = 'class="title.*?href="([^"]+)">([^<]+).*?src="([^"]+)(.*?)</span>'
    isMatch, aResult = cParser().parse(sHtmlContent, pattern)
    if not isMatch:
        if not sGui: oGui.showInfo()
        return

    total = len(aResult)
    for sUrl, sName, sThumbnail, sDummy in aResult:
        if sSearchText and not cParser().search(sSearchText, sName):
            continue
        isTvshow = True if 'staffel' in sName.lower() or 'serie' in entryUrl or ';">S0' in sDummy else False
        isYear, sYear = cParser.parse(sName, '(.*?)\((\d*)\)')
        for name, year in sYear:
            sName = name
            sYear = year
            break
        isDesc, sDesc = cParser.parseSingleResult(sDummy, '</b>([^<]+)')
        isDuration, sDuration = cParser.parseSingleResult(sDummy, '(?:Laufzeit|Spielzeit).*?(\d[^<]+)')
        if ':' in sDuration:
            sDuration = time2minutes(sDuration)
        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showSeasons' if isTvshow else 'showHosters')
        oGuiElement.setThumbnail(sThumbnail)
        if isYear:
            oGuiElement.setYear(sYear)
        if isDesc:
            oGuiElement.setDescription(sDesc)
        if isDuration:
            oGuiElement.addItemValue('duration', sDuration)
        oGuiElement.setMediaType('tvshow' if isTvshow else 'movie')
        params.setParam('sThumbnail', sThumbnail)
        params.setParam('TVShowTitle', sName)
        params.setParam('entryUrl', sUrl)
        oGui.addFolder(oGuiElement, params, isTvshow, total)
    if not sGui:
        isMatchNextPage, sNextUrl = cParser().parseSingleResult(sHtmlContent, '<a[^>]href="([^"]+)">vorw')
        if isMatchNextPage:
            params.setParam('sUrl', sNextUrl)
            oGui.addNextPage(SITE_IDENTIFIER, 'showEntries', params)
        oGui.setView('tvshows' if 'staffel' in sName.lower() else 'movies')
        oGui.setEndOfDirectory()


def showSeasons():
    params = ParameterHandler()
    entryUrl = params.getValue('entryUrl')
    sThumbnail = params.getValue('sThumbnail')
    sTVShowTitle = params.getValue('TVShowTitle')
    sHtmlContent = cRequestHandler(entryUrl).request()
    L11 = []
    isMatchsst, sstsContainer = cParser.parseSingleResult(sHtmlContent, 'sst.show.*?</script>')
    if isMatchsst:
        sstsContainer = sstsContainer.replace('[', '<').replace(']', '>')
        isMatchsst, L11 = cParser.parse(sstsContainer, "<'([^>]+)")
        if isMatchsst:
            total = len(L11)
    L22 = []
    isMatchollhd, ollhdsContainer = cParser.parseSingleResult(sHtmlContent, 'ollhd.show.*?</script>')
    if isMatchollhd:
        ollhdsContainer = ollhdsContainer.replace('[', '<').replace(']', '>')
        isMatchollhd, L22 = cParser.parse(ollhdsContainer, "<'([^>]+)")
        if isMatchollhd:
            total = len(L22)
    L33 = []
    isMatchpw, pwsContainer = cParser.parseSingleResult(sHtmlContent, 'pw.show.*?</script>')
    if isMatchpw:
        pwsContainer = pwsContainer.replace('[', '<').replace(']', '>')
        isMatchpw, L33 = cParser.parse(pwsContainer, "<'([^>]+)")
        if isMatchpw:
            total = len(L33)
    isMatchgo, gosContainer = cParser.parseSingleResult(sHtmlContent, 'go.show.*?</script>')
    if isMatchgo:
        gosContainer = gosContainer.replace('[', '<').replace(']', '>')
        isMatchgo, L44 = cParser.parse(gosContainer, "<'([^>]+)")
        if isMatchgo:
            total = len(L44)

    isDesc, sDesc = cParser.parseSingleResult(sHtmlContent, '</b>([^"]+)<br><br>')
    for i in range(0, total):
        try:
            params.setParam('L11', L11[i])
        except Exception:
            pass
        try:
            params.setParam('L22', L22[i])
        except Exception:
            pass
        try:
            params.setParam('L33', L33[i])
        except Exception:
            pass
        try:
            params.setParam('L44', L44[i])
        except Exception:
            pass
        i = i + 1
        oGuiElement = cGuiElement('Staffel ' + str(i), SITE_IDENTIFIER, 'showEpisodes')
        oGuiElement.setMediaType('season')
        oGuiElement.setTVShowTitle(sTVShowTitle)
        oGuiElement.setSeason(i)
        oGuiElement.setThumbnail(sThumbnail)
        if isDesc:
            oGuiElement.setDescription(sDesc)
        params.setParam('sDesc', sDesc)
        params.setParam('sSeasonNr', i)
        cGui().addFolder(oGuiElement, params, True, total)
        cGui().setView('seasons')
    cGui().setEndOfDirectory()


def showEpisodes():
    params = ParameterHandler()
    sSeasonNr = params.getValue('sSeasonNr')
    sThumbnail = params.getValue('sThumbnail')
    sTVShowTitle = params.getValue('TVShowTitle')
    sDesc = params.getValue('sDesc')
    L11 = []
    if params.exist('L11'):
        L11 = params.getValue('L11')
        isMatch1, L11 = cParser.parse(L11, "(http[^']+)")
    L22 = []
    if params.exist('L22'):
        L22 = params.getValue('L22')
        isMatch, L22 = cParser.parse(L22, "(http[^']+)")
    L33 = []
    if params.exist('L33'):
        L33 = params.getValue('L33')
        isMatch3, L33 = cParser.parse(L33, "(http[^']+)")
    L44 = []
    if params.exist('L44'):
        L44 = params.getValue('L44')
        isMatch4, L44 = cParser.parse(L44, "(http[^']+)")
    liste = ziplist(L11, L22, L33, L44)
    i = 0
    for sUrl in liste:
        i = i + 1
        oGuiElement = cGuiElement('Episode ' + str(i), SITE_IDENTIFIER, 'showHosters')
        oGuiElement.setTVShowTitle(sTVShowTitle)
        oGuiElement.setSeason(sSeasonNr)
        oGuiElement.setEpisode(i)
        oGuiElement.setMediaType('episode')
        if sDesc:
            oGuiElement.setDescription(sDesc)
        if sThumbnail:
            oGuiElement.setThumbnail(sThumbnail)
        params.setParam('sLinks', sUrl)
        cGui().addFolder(oGuiElement, params, False)
    cGui().setView('episodes')
    cGui().setEndOfDirectory()


def showHosters():
    hosters = []
    headers = '&Accept-Language=de%2Cen-US%3Bq%3D0.7%2Cen%3Bq%3D0.3&Accept=%2A%2F%2A&User-Agent=Mozilla%2F5.0+%28Windows+NT+10.0%3B+Win64%3B+x64%3B+rv%3A99.0%29+Gecko%2F20100101+Firefox%2F99.0'
    params = ParameterHandler()
    if params.exist('sLinks'):
        sUrl = params.getValue('sLinks')
        isMatch, aResult = cParser().parse(sUrl, "(http[^']+)")
    else:
        sUrl = params.getValue('entryUrl')
        sHtmlContent = cRequestHandler(sUrl, ignoreErrors=True).request()
        pattern = "show[^>]\d,[^>][^>]'([^']+)"
        isMatch, aResult = cParser().parse(sHtmlContent, pattern)
    if isMatch:
        for sUrl in aResult:
            if 'kinoger.ru' in sUrl:
                oRequest = cRequestHandler(sUrl, caching=False, ignoreErrors=True)
                oRequest.addHeaderEntry('Referer', 'https://kinoger.com/')
                sHtmlContent = oRequest.request()
                isMatch, packed = cParser.parseSingleResult(sHtmlContent, '(eval\s*\(function.*?)</script>')
                if isMatch:
                    sHtmlContent = jsunpacker.unpack(packed)
                isMatch, j = cParser.parse(sHtmlContent, 'ct":"([^"]+)","iv":"([^"]+)","s":"([^"]+)')
                if isMatch:
                    try:
                        ciphertext = base64.b64decode(j[0][0])
                        salt = binascii.unhexlify(j[0][2])
                        password = 'XOmurdOgNnjMwYah'.encode('utf-8')
                        sHtmlContent = cUtil.evp_decode(ciphertext, password, salt)
                    except Exception:
                        sHtmlContent = ''
                isMatch, hUrl = cParser.parseSingleResult(sHtmlContent, 'sources.*?file.*?(http[^"]+)')
                if isMatch:
                    hUrl = hUrl.replace('\\', '')
                    oRequest = cRequestHandler(hUrl, caching=False, ignoreErrors=True)
                    oRequest.addHeaderEntry('Referer', 'https://kinoger.ru/')
                    oRequest.addHeaderEntry('Origin', 'https://kinoger.ru')
                    oRequest.removeNewLines(False)
                    sHtmlContent = oRequest.request()
                    pattern = 'RESOLUTION=(\d+x\d+).*?\n([^#"]+)'
                    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
                if isMatch:
                    for sQualy, sUrl in aResult:
                        sUrl = (hUrl.split('video')[0].strip() + sUrl.strip())
                        sUrl = sUrl + '|Origin=https%3A%2F%2Fkinoger.ru&Referer=https%3A%2F%2Fkinoger.ru%2F' + headers
                        hoster = {'link': sUrl, 'name': 'Kinoger.ru ' + sQualy, 'resolveable': True}
                        hosters.append(hoster)
            elif 'kinoger.pw' in sUrl:
                url = get_streamsburl('kinoger.pw', sUrl.replace('.html', '').split('/')[4])
                oRequest = cRequestHandler(url, caching=False, ignoreErrors=True)
                oRequest.addHeaderEntry('Referer', sUrl)
                oRequest.addHeaderEntry('watchsb', 'sbstream')
                sHtmlContent = oRequest.request()
                isMatch, aResult = cParser.parse(sHtmlContent, 'file":"([^"]+)')
                if isMatch:
                    oRequest = cRequestHandler(aResult[0], caching=False, ignoreErrors=True)
                    oRequest.addHeaderEntry('Referer', 'https://kinoger.pw/')
                    oRequest.addHeaderEntry('Origin', 'https://kinoger.pw')
                    sHtmlContent = oRequest.request()
                    isMatch, aResult = cParser.parse(sHtmlContent, 'RESOLUTION=(\d+x\d+).*?(http[^"]+)#')
                if isMatch:
                    for sQualy, sUrl in aResult:
                        sUrl = sUrl + '|Origin=https%3A%2F%2Fkinoger.pw&Referer=https%3A%2F%2Fkinoger.pw%2F' + headers
                        hoster = {'link': sUrl, 'name': 'Kinoger.pw ' + sQualy, 'resolveable': True}
                        hosters.append(hoster)
            elif 'kinoger.re' in sUrl:
                oRequest = cRequestHandler('https://kinoger.re/api/video/stream/get', ignoreErrors=True, jspost=True)
                oRequest.addHeaderEntry('Referer', sUrl)
                oRequest.addParameters('id', sUrl.split('/')[-1])
                sHtmlContent = oRequest.request()
                isMatch, aResult = cParser.parse(sHtmlContent, 'file":"([^"]+)')
                if isMatch:
                    for sUrl in aResult:
                        sUrl = sUrl + '|Referer=https%3A%2F%2Fkinoger.re%2F' + headers
                        hoster = {'link': sUrl, 'name': 'Kinoger.re ', 'resolveable': True}
                        hosters.append(hoster)
            elif 'start.u' in sUrl:
                t = sUrl.split('/')
                token = encodeUrl(t[4] + ':' + t[5])
                url2 = 'http://start.u-stream.in/ustGet.php?id=' + t[5] + '&token=' + token
                oRequest = cRequestHandler(url2, ignoreErrors=True)
                oRequest.addHeaderEntry('Referer', sUrl)
                content = oRequest.request()
                j = json.loads(content)
                if 'url' in j and j['url']:
                    for u in j['url']:
                        u = decodeStr(u) + '|Referer=https%3A%2F%2Fstart.u-stream.in%2F' + headers
                        hoster = {'link': u, 'name': cParser.urlparse(sUrl) + Qualy(u), 'resolveable': True}
                        hosters.append(hoster)
            else:
                hoster = {'link': sUrl + 'DIREKT', 'name': cParser.urlparse(sUrl)}
                hosters.append(hoster)
    if hosters:
        hosters.append('getHosterUrl')
        return hosters


def Qualy(q):
    if '480-' in q:
        return ' 480p'
    elif '720-' in q:
        return ' 720p'
    elif '1080-' in q:
        return ' 1080p'
    else:
        return ' 360p'


def getHosterUrl(sUrl=False):
    if sUrl.startswith('//'):
        sUrl = 'https:' + sUrl
    if sUrl.endswith('DIREKT'):
        return [{'streamUrl': sUrl[:-6], 'resolved': False}]
    else:
        return [{'streamUrl': sUrl, 'resolved': True}]


def showSearch():
    sSearchText = cGui().showKeyBoard()
    if not sSearchText: return
    _search(False, sSearchText)
    cGui().setEndOfDirectory()


def _search(oGui, sSearchText):
    showEntries(URL_MAIN, oGui, sSearchText)


def get_streamsburl(host, media_id):
    # Copyright (c) 2019 vb6rocod

    def makeid(length):
        t = string.ascii_letters + string.digits
        return ''.join([random.choice(t) for _ in range(length)])
    x = '{0}||{1}||{2}||streamsb'.format(makeid(12), media_id, makeid(12))
    c1 = binascii.hexlify(x.encode('utf8')).decode('utf8')
    x = '{0}||{1}||{2}||streamsb'.format(makeid(12), makeid(12), makeid(12))
    c2 = binascii.hexlify(x.encode('utf8')).decode('utf8')
    x = '{0}||{1}||{2}||streamsb'.format(makeid(12), c2, makeid(12))
    c3 = binascii.hexlify(x.encode('utf8')).decode('utf8')
    return 'https://{0}/sources50/{1}/{2}'.format(host, c1, c3)


def toString(number, base):
    string = '0123456789abcdefghijklmnopqrstuvwxyz'
    if number < base:
        return string[number]
    else:
        return toString(number // base, base) + string[number % base]


def keys(s):
    if s == '1': return ('54A80Ibc3VBdefWGTSFg1X7hEYNijZU', 'kQl2mCnDoMpOq9rHsPt6uLvawRxJyKz')
    elif s == '2': return ('4YMHUe5OFZ7L2PEJ8fgKAh1RGiIj0kV', 'aTlNmCn3oBpDqSr9sbtWu6vcwdxXyQz')
    elif s == '3': return ('AN4YZVHTJEOeLS2fGaFghiKWjQMbIkl', 'Xmc1d3nCo7p5qBrUsDt9u8vRw6x0yPz')
    elif s == '4': return ('V6YD2ZNWaTefXgObhS3UcRAP4dIiJjK', 'k7l5mLnCoEpMqGrBsFtQuHv1w0x9y8z')
    elif s == '5': return ('OGAFaN985MDHTbYW7ceQfdIgZhJiXj3', 'kSl6mRn2oCpKqErPsUt1u0v4wLxByVz')
    elif s == '6': return ('cZXK8O3BS5NRedFPfLAg2U6hIiDj7VT', 'k9lQmJnWoGp1q0rCsatHuYvbw4xMyEz')
    elif s == '7': return ('UZQXTPHcVS7deEfWDgRMLh9iIa1Y0j2', 'klb3m8nOoBpNqKr5s6tJuAvCwGxFy4z')
    elif s == '8': return ('AZI4WCcKOdNJGF3YEa2eHfgb8hMiLjD', 'kUlPmBnSoVp5q7r6s9t1uTv0wQxRyXz')
    elif s == '9': return ('OWZYcP3adUNSbeCfJVghTQDRIiKjBkG', 'X5lMmFnAoLp1q7r6s0tHu2vEw9x4y8z')
    else: return ('', '')


def decodeStr(e):
    d = ''
    t0, t1 = keys(e[-1])
    e = e[:-1]
    for i in range(len(e)):
        for ii in range(len(t0)):
            if e[i] in t0[ii]:
                d += t1[ii]
            elif e[i] in t1[ii]:
                d += t0[ii]
    return cParser.unquotePlus(base64.b64decode(d[::-1] + '==').decode())


def encodeStr(e):
    d = ''
    k = str(random.randint(2, 7))
    t0, t1 = keys(k)
    e = cParser.quotePlus(e)
    e = base64.b64encode(e.encode())
    e = e.decode().replace('=', '')[::-1]
    for i in range(len(e)):
        for ii in range(len(t0)):
            if e[i] in t0[ii]:
                d += t1[ii]
            elif e[i] in t1[ii]:
                d += t0[ii]
    return d + k


def encodeUrl(e):
    n = ''
    a = random.randint(2, 9)
    t0, t1 = keys(str(a))
    t = a + 5
    for r in range(len(e)):
        n += toString(ord(e[r]), t)
        n += '!'
    n = base64.b64encode(n[:-1].encode()).decode().replace('=', '')
    e = ''
    for i in range(len(n)):
        for ii in range(len(t0)):
            if n[i] in t0[ii]:
                e = e + t1[ii]
            elif n[i] in t1[ii]:
                e = e + t0[ii]
    return encodeStr(e + str(a))


def time2minutes(time):
    if type(time) == bytes:
        time = time.decode()
    t = time.split(":")
    minutes = float(t[0]) * 60 + float(t[1]) + float(t[2]) * 0.05 / 3
    minutes = str(minutes).split(".")[0] if '.' in str(minutes) else str(minutes)
    return minutes
