#!/usr/bin/python
# -*- coding: utf-8 -*-
# Writer (c) 2017, Silhouette2022@gmail.com
# Rev. 1.0.0

import os, sys, time
import xbmc, xbmcaddon, xbmcgui

__addon__ = xbmcaddon.Addon()
__addonversion__ = __addon__.getAddonInfo('version')
# __addonid__ = __addon__.getAddonInfo('id')
__addonname__ = __addon__.getAddonInfo('name')
# __addon_path__ = __addon__ .getAddonInfo('path').decode('utf-8')

_SERVICE_ID_ = 'script.pvr.reset'

stime = 0

def log(message):
	xbmc.log('[%s LOG]: %s' % (__addonname__, message))


class ResetService:

	def __init__(self):
		self._daemon()

	def pvr_stop(self):
		log("-pvr_stop:")
		xbmc.executebuiltin('XBMC.StopPVRManager')
		xbmc.executebuiltin('XBMC.Playlist.Clear')

	def pvr_start(self):
		log("-prv_start:")
		xbmc.executebuiltin('XBMC.StartPVRManager')
		
	def pvr_reload(self):
		log("-reload:")
		self.pvr_stop()
		xbmc.sleep(1500)
		self.pvr_start()
		xbmc.sleep(1500)

	def _daemon(self):

		stime = time.time()
		dtime = int(xbmcaddon.Addon(_SERVICE_ID_).getSetting('delay'))

		while (not xbmc.abortRequested) and stime and dtime:

			global stime

			ntime = time.time()
			if ntime - stime >= dtime:
				self.pvr_reload()
				stime = 0
			else:
				xbmc.sleep(2000)

		log('aborted')
						   

if __name__ == '__main__':
	log('version %s started' % __addonversion__)
	ResetService()
	del Reset
	log('version %s stopped' % __addonversion__)


