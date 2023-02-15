# -*- coding: utf-8 -*-
# Python 3

import xbmc
from resources.lib.gui.gui import cGui
from resources.lib.tools import logger


class XstreamPlayer(xbmc.Player):
    def __init__(self, *args, **kwargs):
        xbmc.Player.__init__(self, *args, **kwargs)
        self.streamFinished = False
        self.streamSuccess = True
        self.playedTime = 0
        self.totalTime = 999999
        logger.info('player instance created')

    def onPlayBackStarted(self):
        logger.info('starting Playback')
        self.totalTime = self.getTotalTime()

    def onPlayBackStopped(self):
        logger.info('Playback stopped')
        if self.playedTime == 0 and self.totalTime == 999999:
            self.streamSuccess = False
            logger.error('Kodi failed to open stream')
        self.streamFinished = True

    def onPlayBackEnded(self):
        logger.info('Playback completed')
        self.onPlayBackStopped()


class cPlayer:
    def clearPlayList(self):
        oPlaylist = self.__getPlayList()
        oPlaylist.clear()

    def __getPlayList(self):
        return xbmc.PlayList(xbmc.PLAYLIST_VIDEO)

    def addItemToPlaylist(self, oGuiElement):
        oListItem = cGui().createListItem(oGuiElement)
        self.__addItemToPlaylist(oGuiElement, oListItem)

    def __addItemToPlaylist(self, oGuiElement, oListItem):
        oPlaylist = self.__getPlayList()
        oPlaylist.add(oGuiElement.getMediaUrl(), oListItem)

    def startPlayer(self):
        logger.info('start player')
        xbmcPlayer = XstreamPlayer()
        monitor = xbmc.Monitor()
        while (not monitor.abortRequested()) & (not xbmcPlayer.streamFinished):
            if xbmcPlayer.isPlayingVideo():
                xbmcPlayer.playedTime = xbmcPlayer.getTime()
            monitor.waitForAbort(10)
        return xbmcPlayer.streamSuccess
