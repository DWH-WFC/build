# -*- coding: utf-8 -*-

# 2022-04-26

from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.tools import logger, cParser
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.gui.gui import cGui
import json

SITE_IDENTIFIER = 'netzkino'
SITE_NAME = 'NetzKino'
SITE_ICON = 'netzkino.png'
URL_MAIN = 'https://api.netzkino.de.simplecache.net/capi-2.0a/categories/%s.json?d=www&l=de-DE'
URL_SEARCH = 'https://api.netzkino.de.simplecache.net/capi-2.0a/search?q=%s&d=www&l=de-DE'
SITE_GLOBAL_SEARCH = False


def load():
    logger.info('Load %s' % SITE_NAME)
    oGui = cGui()
    params = ParameterHandler()
    params.setParam('sUrl', URL_MAIN % 'neu-frontpage')
    oGui.addFolder(cGuiElement('Neu bei Netzkino', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % 'highlights-frontpage')
    oGui.addFolder(cGuiElement('Highlights', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % 'themenkino-frontpage')
    oGui.addFolder(cGuiElement('Themenkino', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % 'beste-bewertung-frontpage')
    oGui.addFolder(cGuiElement('Beste Bewertung', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % 'blockbuster-kultfilme-frontpage')
    oGui.addFolder(cGuiElement('Blockbuster & Kultfilme', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % 'meisgesehene_filme-frontpage')
    oGui.addFolder(cGuiElement('Meistgesehene Filme', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % 'beliebte-animes-frontpage')
    oGui.addFolder(cGuiElement('Beliebte Animes', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % 'mockbuster-frontpage')
    oGui.addFolder(cGuiElement('Mockbuster', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % 'filme_mit_auszeichnungen-frontpage')
    oGui.addFolder(cGuiElement('Filme mit Auszeichnungen', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % 'frontpage-exklusiv-frontpage')
    oGui.addFolder(cGuiElement('Exklusiv bei Netzkino', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % 'empfehlungen_woche-frontpage')
    oGui.addFolder(cGuiElement('Unsere Empfehlungen der Woche', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % 'komodien-frontpage')
    oGui.addFolder(cGuiElement('Komödien', SITE_IDENTIFIER, 'showEntries'), params)
    oGui.addFolder(cGuiElement('Genre', SITE_IDENTIFIER, 'showGenreMenu'))
    oGui.addFolder(cGuiElement('Suche', SITE_IDENTIFIER, 'showSearch'))
    oGui.setEndOfDirectory()


def showGenreMenu():
    oGui = cGui()
    params = ParameterHandler()
    params.setParam('sUrl', URL_MAIN % 'actionkino')
    oGui.addFolder(cGuiElement('Actionkino', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % 'animekino')
    oGui.addFolder(cGuiElement('Animekino', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % 'arthousekino')
    oGui.addFolder(cGuiElement('Arthousekino', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % 'asiakino')
    oGui.addFolder(cGuiElement('Asiakino', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % 'dramakino')
    oGui.addFolder(cGuiElement('Dramakino', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % 'thrillerkino')
    oGui.addFolder(cGuiElement('Thrillerkino', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % 'liebesfilmkino')
    oGui.addFolder(cGuiElement('Liebesfilmkino', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % 'scifikino')
    oGui.addFolder(cGuiElement('Scifikino', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % 'kinderkino')
    oGui.addFolder(cGuiElement('Kinderkino', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % 'spasskino')
    oGui.addFolder(cGuiElement('Spasskino', SITE_IDENTIFIER, 'showEntries'), params)
    #params.setParam('sUrl', URL_MAIN % 'queerkino')
    #oGui.addFolder(cGuiElement('Queerkino', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % 'horrorkino')
    oGui.addFolder(cGuiElement('Horrorkino', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % 'thrillerkino')
    oGui.addFolder(cGuiElement('Thrillerkino', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN % 'kinoab18')
    oGui.addFolder(cGuiElement('Kino ab 18', SITE_IDENTIFIER, 'showEntries'), params)
    oGui.setEndOfDirectory()


def showEntries(entryUrl=False, sGui=False, sSearchText=False):
    oGui = sGui if sGui else cGui()
    params = ParameterHandler()
    if not entryUrl: entryUrl = params.getValue('sUrl')
    try:
        sJson = cRequestHandler(entryUrl, ignoreErrors=sGui is not False).request()
        aJson = json.loads(sJson)
    except:
        if not sGui: oGui.showInfo()
        return

    if 'posts' not in aJson or len(aJson['posts']) == 0:
        if not sGui: oGui.showInfo()
        return

    total = len(aJson['posts'])
    for item in aJson['posts']:
        try:
            if sSearchText and not cParser().search(sSearchText, item['title']):
                continue
            oGuiElement = cGuiElement(item['title'], SITE_IDENTIFIER, 'showHosters')
            oGuiElement.setThumbnail(item['thumbnail'])
            oGuiElement.setDescription(item['content'])
            oGuiElement.setFanart(item['custom_fields']['featured_img_all'][0])
            oGuiElement.setYear(item['custom_fields']['Jahr'][0])
            oGuiElement.setMediaType('movie')
            if 'Duration' in item['custom_fields'] and item['custom_fields']['Duration'][0]:
                oGuiElement.addItemValue('duration', item['custom_fields']['Duration'][0])
            urls = ''
            if 'Streaming' in item['custom_fields'] and item['custom_fields']['Streaming'][0]:
                urls += 'http://netzkino_and-vh.akamaihd.net/i/%s.mp4/master.m3u8' % item['custom_fields']['Streaming'][0]
            if 'Youtube_Delivery_Id' in item['custom_fields'] and item['custom_fields']['Youtube_Delivery_Id'][0]:
                urls += '#' + 'plugin://plugin.video.youtube/play/?video_id=%s' % item['custom_fields']['Youtube_Delivery_Id'][0]
            params.setParam('entryUrl', urls)
            oGui.addFolder(oGuiElement, params, False, total)
        except:
            continue

    if not sGui:
        oGui.setView('movies')
        oGui.setEndOfDirectory()


def showHosters():
    hosters = []
    URL = ParameterHandler().getValue('entryUrl')
    for sUrl in URL.split('#'):
        hoster = {'link': sUrl, 'name': 'Netzkino' if 'netzkino' in sUrl else 'Youtube', 'resolveable': True}
        hosters.append(hoster)
    if hosters:
        hosters.append('getHosterUrl')
    return hosters


def getHosterUrl(sUrl=False):
    return [{'streamUrl': sUrl, 'resolved': True}]


def showSearch():
    sSearchText = cGui().showKeyBoard()
    if not sSearchText: return
    _search(False, sSearchText)
    cGui().setEndOfDirectory()


def _search(oGui, sSearchText):
    showEntries(URL_SEARCH % cParser().quotePlus(sSearchText), oGui, sSearchText)
