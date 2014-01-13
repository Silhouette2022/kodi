#!/usr/bin/python
# -*- coding: utf-8 -*-
# Writer (c) 2013, otaranda@hotmail.com
# Rev. 1.0.1

import sys
import xbmc
import xbmcgui
import xbmcaddon
__addon__ = xbmcaddon.Addon()
__addonversion__ = __addon__.getAddonInfo('version')
__addonid__ = __addon__.getAddonInfo('id')
__addonname__ = __addon__.getAddonInfo('name')
_SERVICE_ID_ = 'script.service.rodina.tv'
_RODINA_ID_ = 'plugin.video.rodina.tv'

def log(message, level = 1):
    print '[%s LOG]: %s' % (__addonname__, message.encode('utf8'))


class RodinaService:

    def __init__(self):
#        self.time = ''
#        self.seek = ''
        self.Player = RodinaPlayer()
        self._daemon()

    def _daemon(self):
        while not xbmc.abortRequested:
            xbmc.sleep(1000)

        log('abort requested')


class RodinaPlayer(xbmc.Player):

    def __init__(self):
        self.arch_play = 'false'
        xbmcaddon.Addon(_RODINA_ID_).setSetting('arch_on', 'false')

#    def arch_on(self):
#        log('arch_on')
#        self.arch_play = 'true'

#    def onPlayBackStarted(self):
#        log('player starts')
#        self.time = ''
#        self.seek = ''

    def onPlayBackEnded(self):
        self.onPlayBackStopped()

    def onPlayBackStopped(self):
#        log('player stops')
        self.arch_play = 'false'
        xbmcaddon.Addon(_RODINA_ID_).setSetting('arch_on', 'false')

#    def onPlayBackPaused(self):
#        log('player pauses')

#    def onPlayBackResumed(self):
#        log('player resumes')

    def onPlayBackSeek(self, time, seekOffset):
#        log('## Playback Seek ##')
#        log('#seekOffset: %s #' % seekOffset)
#        log('#time: %s #' % time)
#        self.time = time
#        self.seek = seekOffset
        if seekOffset > 0: seek = 60
        else: seek = -60
        time = self.getTime()
        self.arch_play = xbmcaddon.Addon(_RODINA_ID_).getSetting('arch_on')
        if self.arch_play == 'true':
            params = 'mode=seek&time=%s&seek=%s' % (int(float(time)), seek)
            script = 'special://home/addons/%s/default.py' % 'plugin.video.rodina.tv'
            xbmc.executebuiltin('XBMC.RunScript(%s, %d, %s)' % (script, 99, params))
      


if __name__ == '__main__':
    log('script version %s started' % __addonversion__)
    RodinaService()
    del RodinaPlayer
    del RodinaService
    log('script version %s stopped' % __addonversion__)

