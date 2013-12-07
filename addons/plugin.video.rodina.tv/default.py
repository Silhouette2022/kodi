#!/usr/bin/python
# -*- coding: utf-8 -*-
# Writer (c) 2013, otaranda@hotmail.com
# Rev. 1.0.0


_VERSION_ = '1.0.0'

import os, re, sys, datetime, time
import urllib, urllib2
import xbmc, xbmcplugin, xbmcgui, xbmcaddon
import uuid
import hashlib

#try:
#    sys.path.append(os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
#    import XbmcHelpers
#except:
#    try:
#        sys.path.insert(0, os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
#        import XbmcHelpers
#    except:
#        sys.path.append(os.path.join(os.getcwd(), r'resources', r'lib'))
#        import XbmcHelpers
        
import XbmcHelpers
common = XbmcHelpers
common.plugin = "Rodina TV"

import cookielib
cookiejar = cookielib.LWPCookieJar()
cookie_handler = urllib2.HTTPCookieProcessor(cookiejar)
opener = urllib2.build_opener(cookie_handler)

def QT(url): return urllib.quote_plus(url)
    
#def dt(u): return datetime.datetime.utcfromtimestamp(u)

class RodinaTV():
    def __init__(self):
        self.id = 'plugin.video.rodina.tv'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.fanart = self.addon.getAddonInfo('fanart')
        self.profile = self.addon.getAddonInfo('profile')

        self.language = self.addon.getLocalizedString

        self.handle = int(sys.argv[1])
        self.params = sys.argv[2]

        self.url = 'http://rodina.tv'
        self.api = 'http://api.rodina.tv'
        self.auth = self.api + '/auth.xml'
        self.get_auth = False

        self.token = ''
        self.portal = ''
        self.ttl = ''
        
        self.cat = ''
        self.has_pwd = ''
        self.has_rec = ''
        self.pid = ''
        
        self.count = ''
        self.offset = ''
        self.word = ''
                        
        self.timeserver = ''
       
        self.path = xbmc.translatePath(self.addon.getAddonInfo('path')).decode('utf-8')
        self.path_resources = os.path.join(self.path, 'resources')
        self.path_icons = os.path.join(self.path_resources, 'icons')
        self.path_icons_tv = os.path.join(self.path_icons, 'icon_tv_small.png')
        self.path_icons_td = os.path.join(self.path_icons, 'icon_timedelay_small.png')
        self.path_icons_ts = os.path.join(self.path_icons, 'icon_timeshift_small.png')
        self.path_icons_kino = os.path.join(self.path_icons, 'icon_kinozal_small.png')
        self.path_icons_info = os.path.join(self.path_icons, 'icon_info_small.png')
                
        self.profile_chan = xbmc.translatePath(os.path.join(self.profile, 'cache_c.tmp'))
        self.profile_epg = xbmc.translatePath(os.path.join(self.profile, 'cache_e.tmp'))

        self.uid = self.addon.getSetting('uid')
        self.pwd = self.addon.getSetting('pwd')
        self.tsd = self.addon.getSetting('tsd')
        self.br = '141' if self.addon.getSetting('br') == 'high' else '148'
        self.ss = self.addon.getSetting('ss')   
        self.view_mode = self.addon.getSetting('view_mode')      

        self.debug = True
        common.dbg = self.debug

    def main(self):
        self.log("Addon: %s"  % self.id)
        self.log("Params: %s" % self.params)

        params = common.getParameters(self.params)
        
        mode = params['mode'] if 'mode' in params else None
        self.cat = params['cat'] if 'cat' in params else ''
        self.token = params['token'] if 'token' in params else ''
        self.portal = urllib.unquote_plus(params['portal']) if 'portal' in params else ''
        self.numb = params['numb'] if 'numb' in params else ''
        self.has_pwd = params['pwd'] if 'pwd' in params else ''    
        self.has_rec = params['rec'] if 'rec' in params else '' 
        self.ts = params['ts'] if 'ts' in params else '' 
        self.cicon = urllib.unquote_plus(params['icon']) if 'icon' in params else '' 
        self.adt = params['dt'] if 'dt' in params else ''
        self.pid = params['pid'] if 'pid' in params else ''
        self.fid = params['fid'] if 'fid' in params else ''
        self.lid = params['lid'] if 'lid' in params else ''
        self.count = params['count'] if 'count' in params else ''
        self.offset = params['offset'] if 'offset' in params else ''
        self.word = params['word'] if 'word' in params else ''
                                
        if mode == 'tv':
            self.m_tv()
        elif mode == 'cat':
            self.m_cat()
        elif mode == 'tvplay':
            self.tv_play()
        elif mode == 'arch':
            self.m_arch()       
        elif mode == 'atv':
            self.m_atv()   
        elif mode == 'adate':
            self.m_adate()  
        elif mode == 'aepg':
            self.m_aepg()              
        elif mode == 'kino':
            self.m_kino() 
        elif mode == 'search':
            self.m_search() 
        elif mode == 'genres':
            self.m_genres() 
        elif mode == 'all':
            self.m_all() 
        elif mode == 'film':
            self.m_film()             
        elif mode == 'set':
            self.m_set() 
        else:
            self.m_main()
            
    def xmlerror(self, xml):
        msg = common.parseDOM(xml, "item", attrs={"name": "message"})[0]
        code  = common.parseDOM(xml, "item", attrs={"name": "code"})[0]
        if code == '4002':
            self.log('%s: %s' % (code, msg));
            self.get_auth = True
            return 
        self.showErrorMessage('%s: %s' % (code, msg))
        
    def alarm_set(self):
        xbmc.executebuiltin("XBMC.AlarmClock(%s,XBMC.Container.Refresh,%s,True)" % (('%s_refresh_list' % self.id), self.ttl))

    def alarm_reset(self):
        xbmc.executebuiltin("XBMC.CancelAlarm(%s,True)" % ('%s_refresh_list' % self.id))
 
    def cached_rst(self, fn):
        self.log("-cached_rst:")
 
        if os.path.isfile(fn) == True:
            self.log("--exist")
            try: os.remove(fn)
            except: pass

               
    def cached_get(self, type):
        self.log("-cached_get: %s" % type)
        cache = ''
        if type == 'tv':
            cquery = '&query=%s' % 'get_channels'
            fn = self.profile_chan
            tt = time.time()
        elif type == 'etv':
            cquery = '&query=%s&key="period|count"&value="%s|%s"' % ('get_epg', 60*60*3, 3)
            fn = self.profile_epg
            tt = time.time()
        elif type == 'dtv':
            tstart = str(int(time.time()))
            cquery = '&query=%s&key="start|period|count"&value="%s|%s|%s"' % ('get_epg', tstart, 60*60*3, 3)
            fn = self.profile_epg
            tt = time.time()
        elif type == 'atv':
            cquery = '&query=%s&key="start|period|number"&value="%s|%s|%s"' % ('get_epg', self.adt, 60*60*24, self.numb)
            fn = self.profile_epg
            tt = float(self.adt)
            type += self.numb
        else: return
        self.log("-tt: %s" % tt)
        
        if os.path.isfile(fn) == True:
            self.log("--exist")
            try:
                cf = open(fn, 'r')
                self.log("--opened")
                slast = cf.readline()
                flast = float(slast)
            except: flast = 0.0
            
            if abs(tt - flast) < 300:
                self.log("--toread")
                try: 
                    ctype = cf.readline()
                    if ctype.strip() == type:
                        cache = cf.readline()
                        self.log("--readline")
                except: pass
            cf.close()
            
        if cache == '':
            self.log("--empty")
#            tv = self.portal + '?token=%s&query=%s' % (self.token, 'get_channels')
#            resp = self.getPage({"link": tv})       
#            if self.get_auth == True:
#                self.log("--get_auth")
#                self.authorize()
#                if self.get_auth == False:
#                    self.log("--getpage")
#                    resp = self.getPage({"link": tv})

            self.authorize()
            if self.get_auth == False:
                self.log("--getpage")
                req = self.portal + '?token=%s' % self.token + cquery
                resp = self.getPage({"link": req})


            if resp != None:
                self.log("--gotit")
                cf = open(fn, 'w')
                cf.write(str(tt) + '\n')
                cf.write(type + '\n')
                cf.write(resp + '\n')
                cf.close()
                cache = resp
                
        return cache

    def getPage(self, cdict):
        self.log("-getPage:")
        resp = common.fetchPage(cdict)
        if resp["status"] == 200:
            status = common.parseDOM(resp["content"], "entity", ret="status")[0]
            self.timeserver = common.parseDOM(resp["content"], "entity", ret="timeserver")[0]
            if status == "success":
                self.get_auth = False
                return resp["content"]
            else:
                self.xmlerror(resp["content"])
            
        else:
            self.showErrorMessage('Error: %s' % (str(resp["status"])))
            
        return None
        
    def epg2dict(self, sepg, tconv = True):
        self.log("-epg2dict:")
        depg = {}
        a_raw = common.parseDOM(sepg, "row")
        for raw in a_raw:
#            print '----------'
#            print raw.encode('utf8')   
            try: numb = common.parseDOM(raw, "item", attrs={"name": "number"})[0]
            except: numb = ''
            if numb != '':
                a_progs = common.parseDOM(raw, "array", attrs={"name": "programmes"})
                l_progs = []
                for progs in a_progs:
#                    print '----------------------'
#                    print progs.encode('utf8')

                    a_title = common.parseDOM(progs, "item", attrs={"name": "title"})
                    a_pid = common.parseDOM(progs, "item", attrs={"name": "pid"})
                    a_utstart = common.parseDOM(progs, "item", attrs={"name": "ut_start"})
                    a_utstop = common.parseDOM(progs, "item", attrs={"name": "ut_stop"})
                    a_has_desc = common.parseDOM(progs, "item", attrs={"name": "has_desc"})
                    a_desc = common.parseDOM(progs, "item", attrs={"name": "desc"})
                    a_has_rec = common.parseDOM(progs, "item", attrs={"name": "has_record"})
 
                    j = 0
                    for i in range(len(a_title)):
                        if a_has_desc[i] == '1':
                            desc = a_desc[j]
                            j += 1
                        else: desc = ''

                        ststart = time.strftime("%H:%M",time.localtime(float(a_utstart[i])))
                        ststop = time.strftime("%H:%M",time.localtime(float(a_utstop[i])))
                        l_progs.append([ststart, ststop, a_title[i], desc, a_pid[i], a_has_rec[i]])
                    
                    depg[numb] = l_progs

#        print depg
        return depg        
        
    def authorize(self):

        device = 'xbmc'
        version = _VERSION_
        
        resp = self.getPage({"link": self.auth})
        if resp != None:
        
            tmserv = common.parseDOM(resp, "entity", ret="timeserver")[0]
            rand = common.parseDOM(resp, "item", attrs={"name": "rand"})[0]
            sid  = common.parseDOM(resp, "item", attrs={"name": "sid"})[0]
        
            resp = self.getPage({"link": self.auth 
                    + '?device=%s&version=%s&sid=%s&login=%s&passwd=%s&serial=%s' % 
                    (device, version, sid, self.uid, 
                    hashlib.md5( rand + hashlib.md5(self.pwd).hexdigest()).hexdigest(),
                    uuid.getnode())})
                    
            if resp != None:
                self.get_auth = False
                self.token = common.parseDOM(resp, "item", attrs={"name": "token"})[0]
                self.portal = common.parseDOM(resp, "item", attrs={"name": "portal"})[0]
                self.ttl = common.parseDOM(resp, "item", attrs={"name": "ttl"})[0]
                
    def list_items(self, ictlg, view):
        self.log("-list_items:")
        
        for ctUrl, ctIcon, ctFolder, ctLabels  in ictlg:
            ctTitle = ctLabels['title']
            item = xbmcgui.ListItem(ctTitle, iconImage=ctIcon, thumbnailImage=ctIcon)
#            infoLabels = {'title':ename,
#              'tvshowtitle':sport,
#              'plot':plot,
#              'aired':start,
#              'premiered':start,
#              'duration':length}
#            if ctPlot == None: infoLabels={'title': ctTitle}
#            else: infoLabels={'title': ctTitle, 'plot': ctPlot}    
            item.setInfo( type='Video', infoLabels=ctLabels)
            if ctFolder == False: item.setProperty('IsPlayable', 'true')
            item.setProperty('fanart_image', self.fanart)
            xbmcplugin.addDirectoryItem(self.handle, sys.argv[0] + ctUrl, item, ctFolder) 
            self.log("ctTitle: %s"  % ctTitle) 
            self.log("ctUrl: %s"  % ctUrl) 
            self.log("ctIcon: %s"  % ctIcon) 
        
        xbmcplugin.setContent(self.handle, 'episodes')
        if self.view_mode and view: 
            xbmc.executebuiltin('Container.SetViewMode("515")')
        else:
            xbmc.executebuiltin('Container.SetViewMode("503")')
        xbmcplugin.endOfDirectory(self.handle)
        
    def get_client(self):
        self.log("-get_client:")
        
        req = self.portal + '?token=%s&query=%s' % (self.token, 'get_client_info')
        resp = self.getPage({"link": req})
        if resp != None:
            if self.debug: print resp      
  
    def get_settings(self):
        self.log("-get_settings:")
        
        req = self.portal + '?token=%s&query=%s' % (self.token, 'get_settings')
        resp = self.getPage({"link": req})
        if resp != None:
            if self.debug: print resp   
                    
    def get_tstatus(self):
        self.log("-get_tstatus:")
        
        req = self.portal + '?token=%s&query=%s' % (self.token, 'get_token_status')
        resp = self.getPage({"link": req})
        if resp != None:
            if self.debug: print resp     

    def set_settings(self, ts='0'):
        self.log("-set_settings:")
        
#        key = 'dc|bitrate|tshift'
#        value = '%s|%s|%s' % (self.ss, self.br, ts)
        key = 'bitrate|tshift'
        value = '%s|%s' % (self.br, ts)
        req = self.portal + '?token=%s&query=%s&key="%s"&value="%s"' % (self.token, 'set_settings', key, value)
        resp = self.getPage({"link": req})
        if resp != None:
            self.log('--resp:%s' % resp)
            
    def m_main(self):
        self.log("-m_main:")
        if self.uid == "":
            if not self.m_set(): return
            
        self.authorize()
        if self.token == '':
            return
        self.set_settings(self.tsd)

#        self.get_tstatus()
#        self.get_client()
#        self.get_settings()
        
        ct_main = [('?mode=%s&token=%s&portal=%s&icon=%s' % ('cat', self.token, QT(self.portal), self.path_icons_tv,), self.path_icons_tv,   True, {'title': self.language(2000)} ),
#                  ('?mode=%s&token=%s&portal=%s&ts=%s' % ('cat', self.token, QT(self.portal), self.tsd),   self.path_icons_td,   True, {'title': self.language(2001)}),
                   ('?mode=%s&token=%s&portal=%s&icon=%s' % ('arch', self.token, QT(self.portal), self.path_icons_ts), self.path_icons_ts,   True, {'title': self.language(2002)}),
                   ('?mode=%s&token=%s&portal=%s&icon=%s' % ('kino', self.token, QT(self.portal), self.path_icons_kino), self.path_icons_kino, True, {'title': self.language(1001)}),
                   ('?mode=%s&token=%s&portal=%s&icon=%s' % ('set', self.token, QT(self.portal), self.path_icons_info), self.path_icons_info, True, {'title': self.language(2003)}) ]
                                          
        self.list_items(ct_main, True)
        
        self.cached_rst(self.profile_chan)
        self.cached_rst(self.profile_epg)

    def m_cat(self, nmode='tv'):
        self.log("-m_cat:")

        ct_cat = []    

        resp = self.cached_get('tv')

        if resp != '':
            a_cat = common.parseDOM(resp, "array", attrs={"name": "categories"})
            for cat in a_cat:
                a_title = common.parseDOM(cat, "item", attrs={"name": "title"})
                a_numb = common.parseDOM(cat, "item", attrs={"name": "number"})
                a_comb = zip(a_title, a_numb)
                for title, numb in a_comb:
                    params = '?mode=%s&cat=%s&token=%s&portal=%s' % (nmode, numb, self.token, QT(self.portal))
                    if self.ts != '': params += ('&ts=%s' % self.ts)
                    ct_cat.append((params, self.cicon, True, {'title': title}))

            self.list_items(ct_cat, True)
            
    def m_tv(self):
        self.log("-m_tv:")

        ct_chan = []    
        resp = self.cached_get('tv')
        if resp != None:
            if self.ts != '':
                d_epg = self.epg2dict(self.cached_get('dtv'))
            else:
                d_epg = self.epg2dict(self.cached_get('etv'))
            a_chan = common.parseDOM(resp, "array", attrs={"name": "channels"})
            for chan in a_chan:
                a_raw = common.parseDOM(chan, "row")
                for raw in a_raw:
                    cats = common.parseDOM(raw, "array", attrs={"name": "categories"})[0]
                    cat = common.parseDOM(cats, "item")[0]
                    if cat == self.cat:
                        has_passwd = common.parseDOM(raw, "item", attrs={"name": "has_passwd"})[0]
                        title = common.parseDOM(raw, "item", attrs={"name": "title"})[0]
                        number = common.parseDOM(raw, "item", attrs={"name": "number"})[0]
#                        has_record = common.parseDOM(raw, "item", attrs={"name": "has_record"})[0]
                        a_icon45 = common.parseDOM(raw, "item", attrs={"name": "icon_45_45"})
                        a_icon100 = common.parseDOM(raw, "item", attrs={"name": "icon_100_100"})
                        if len(a_icon100) > 0:
                            icon = a_icon100[0]
                        elif len(a_icon45) > 0:
                            icon = a_icon45[0]
                        else:
                            icon = self.path_icons_tv

                        plot = ''
                        try:
                            lepg = d_epg[number]
                            for ebgn, eend, ename, edescr, pid, rec in lepg:
                                plot += '[B][COLOR FF0084FF]%s-%s[/COLOR] [COLOR FFFFFFFF] %s[/COLOR][/B][COLOR FF999999]\n%s[/COLOR]\n' % (ebgn, eend, ename, edescr)
                        except: pass

                        ct_chan.append(('?mode=%s&token=%s&portal=%s&numb=%s&pwd=%s&icon=%s' % ('tvplay', self.token, self.portal, number, has_passwd, icon), icon, False, {'title': title, 'plot':plot}))

            self.list_items(ct_chan, True)            


    def tv_play(self):
        self.log("-tv_play:")
        
        if self.has_rec == '0': return
        
        if self.has_pwd == '1': pcode = common.getUserInput(self.language(11005), '', True)
        
        resp = None
        self.authorize()
        if self.get_auth == False:
            req = self.portal + '?token=%s&query=%s' % (self.token, 'get_url')

            if self.pid == '' and self.lid == '':
                key = "number"
                value = self.numb
            elif self.lid == '':
                key = "pid"
                value = self.pid
            else:
                key = "lid"
                value = self.lid
            if self.has_pwd == '1':
                key += "|passwd"
                value += '|' + hashlib.md5( self.token + hashlib.md5(pcode).hexdigest()).hexdigest()
            req += '&key="%s"&value="%s"' % (key, value)
            resp = self.getPage({"link": req})

        if resp != None:
            url = common.parseDOM(resp, "item", attrs={"name": "url"})[0]
            item = xbmcgui.ListItem(path = url)
            xbmcplugin.setResolvedUrl(self.handle, True, item)
            self.log("-play_url:%s" % url)
 
                

    def m_arch(self):
        self.log("-m_arch:")
        self.m_cat(nmode='atv')

    def m_atv(self):
        self.log("-m_atv:")
        ct_chan = []    
        resp = self.cached_get('tv')
        if resp != None:
            a_chan = common.parseDOM(resp, "array", attrs={"name": "channels"})
            for chan in a_chan:
                a_raw = common.parseDOM(chan, "row")
                for raw in a_raw:
                    cats = common.parseDOM(raw, "array", attrs={"name": "categories"})[0]
                    cat = common.parseDOM(cats, "item")[0]
                    if cat == self.cat:
                        has_record = common.parseDOM(raw, "item", attrs={"name": "has_record"})[0]
                        if has_record == '1':
                            has_passwd = common.parseDOM(raw, "item", attrs={"name": "has_passwd"})[0]
                            title = common.parseDOM(raw, "item", attrs={"name": "title"})[0]
                            number = common.parseDOM(raw, "item", attrs={"name": "number"})[0]
                            a_icon45 = common.parseDOM(raw, "item", attrs={"name": "icon_45_45"})
                            a_icon100 = common.parseDOM(raw, "item", attrs={"name": "icon_100_100"})
                            if len(a_icon100) > 0:
                                icon = a_icon100[0]
                            elif len(a_icon45) > 0:
                                icon = a_icon45[0]
                            else:
                                icon = self.path_icons_tv

                            ct_chan.append(('?mode=%s&token=%s&portal=%s&numb=%s&pwd=%s&rec=%s&icon=%s' % ('adate', self.token, self.portal, number, has_passwd, has_record, icon), icon, True, {'title': title}))

            self.list_items(ct_chan, True)   
            
                    
    def m_adate(self):
        self.log("-m_adate:")
        
        dweek = {   0: self.language(20001),
                    1: self.language(20002),
                    2: self.language(20003),
                    3: self.language(20004),
                    4: self.language(20005),
                    5: self.language(20006),
                    6: self.language(20007)
                }

        ct_date = [] 
        dts = time.localtime()
        dnow = int(time.mktime((dts.tm_year, dts.tm_mon, dts.tm_mday, 0, 0, 0, 0, 0, 0)))
        for dt in range(dnow+(24*60*60), dnow - (14*24*60*60), -(24*60*60)):
            lt = time.localtime(dt)
            title = time.strftime("%x ", lt) + dweek[lt.tm_wday]
            ct_date.append(('?mode=%s&token=%s&portal=%s&numb=%s&pwd=%s&icon=%s&dt=%s' % 
            ('aepg', self.token, self.portal, self.numb, self.has_pwd, self.cicon, dt), self.cicon, True, {'title': title}))
            
        self.list_items(ct_date, True)

    def m_aepg(self):
        self.log("-m_aepg:")

        ct_chan = []    
        d_epg = self.epg2dict(self.cached_get('atv'), False)
        lepg = d_epg[self.numb]
        for ebgn, eend, ename, edescr, pid, rec in lepg:
            title = '%s-%s %s' % (ebgn, eend, ename)
            plot = '[COLOR FF999999]%s[/COLOR]' % (edescr)
            if rec != '1': title = '[COLOR FFdc5310]%s[/COLOR]' % (title)


            ct_chan.append(('?mode=%s&token=%s&portal=%s&numb=%s&pwd=%s&icon=%s&pid=%s&rec=%s' % ('tvplay', self.token, self.portal, self.numb, self.has_pwd, self.cicon, pid, rec), self.cicon, False, {'title': title, 'plot':plot}))

        self.list_items(ct_chan, False)   
                 
    def m_set(self):
        self.log("-m_set:")
        self.addon.openSettings()
        if self.uid == "": return False
        
        self.authorize()
        if self.get_auth == False:
            self.set_settings(self.tsd)
            self.get_settings()
        else:
            self.error('Authorization failed')

        self.cached_rst(self.profile_chan)
        self.cached_rst(self.profile_epg)        
        self.params = ''
        self.main()
        
    def m_kino(self):
        self.log("-m_kino:")
        
        ct_main = [('?mode=%s&token=%s&portal=%s&icon=%s' % ('search', self.token, QT(self.portal), self.path_icons_kino), self.path_icons_kino, True, {'title': self.language(1002)}),
                   ('?mode=%s&token=%s&portal=%s&icon=%s' % ('genres', self.token, QT(self.portal), self.path_icons_kino), self.path_icons_kino, True, {'title': self.language(1003)}),
                   ('?mode=%s&token=%s&portal=%s&icon=%s&offset=%s' % ('all', self.token, QT(self.portal), self.path_icons_kino, '0'), self.path_icons_kino,    True, {'title': self.language(1004)}) ]
                                          
        self.list_items(ct_main, True)

    def m_search(self):
        self.log("-m_kino:")

        if self.word == '':
            self.word = common.getUserInput('', '')
            self.offset = '0'
        
        if self.word != '':
            self.authorize()
            if self.get_auth == False:
                key = 'word|offset|count'
                value = '%s|%s|%s' % (self.word, self.offset, '12')
                req = self.portal + '?token=%s&query=%s' % (self.token, 'get_cinema_search')
                req += '&key="%s"&value="%s"' % (key, value)
                resp = self.getPage({"link": req})
                
                if resp != None:
                    ct_search = []
                    a_raw = common.parseDOM(resp, "row")
                    for raw in a_raw:
                        title = common.parseDOM(raw, "item", attrs={"name": "title"})[0]
                        small_desc = common.parseDOM(raw, "item", attrs={"name": "small_desc"})[0]
                        imdb_rate = common.parseDOM(raw, "item", attrs={"name": "imdb_rate"})[0]
                        file_count = common.parseDOM(raw, "item", attrs={"name": "file_count"})[0]
                        kp_rate = common.parseDOM(raw, "item", attrs={"name": "kp_rate"})[0]
                        fid = common.parseDOM(raw, "item", attrs={"name": "fid"})[0]
                        year = common.parseDOM(raw, "item", attrs={"name": "year"})[0]
                        small_cover = common.parseDOM(raw, "item", attrs={"name": "small_cover"})[0]

    
                        ct_search.append(('?mode=%s&token=%s&portal=%s&fid=%s' % ('film', self.token, self.portal, fid), small_cover, True,
                         {'title': title, 
                          'plot': '%s IMDB: %s Kinopoisk:%s\n%s' % (year, imdb_rate, kp_rate, small_desc),
                          'year':year} ))

                    if len(a_raw) >= 12:
                        ct_search.append(('?mode=%s&token=%s&portal=%s&word=%s&offset=%s' % ('search', self.token, self.portal, self.word, str(int(self.offset) + 12)), '', True, {'title': self.language(20008)}))
                    self.list_items(ct_search, True) 

    def m_genres(self):
        self.log("-m_genres:")
        
        resp = None
        self.authorize()
        if self.get_auth == False:
            req = self.portal + '?token=%s&query=%s' % (self.token, 'get_cinema_genre_info')
            resp = self.getPage({"link": req})

        if resp != None:
            ct_genres = []
            genres = common.parseDOM(resp, "array", attrs={"name": "genres"})[0]
            a_raw = common.parseDOM(genres, "row")
            for raw in a_raw:
                cnt = common.parseDOM(raw, "item", attrs={"name": "count"})[0]
                title = common.parseDOM(raw, "item", attrs={"name": "title"})[0]
                number = common.parseDOM(raw, "item", attrs={"name": "number"})[0]

                ct_genres.append(( '?mode=%s&token=%s&portal=%s&numb=%s&offset=%s&icon=%s' % ('all', self.token, self.portal, number, '0', self.cicon), 
                self.cicon, True, {'title': '[B]%s [/B][COLOR FF999999](%s)[/COLOR]' % (title, cnt)} ))

            self.list_items(ct_genres, True)   

        
    def m_all(self):
        self.log("-m_kino:")
        
        resp = None
        self.authorize()
        if self.get_auth == False:
            key = 'offset|count'
            value = '%s|%s' % (self.offset, '12')
            if self.numb != '':
                key += '|num_genre'
                value += '|%s' % (self.numb)
            req = self.portal + '?token=%s&query=%s' % (self.token, 'get_cinema_films')
            req += '&key="%s"&value="%s"' % (key, value)
            resp = self.getPage({"link": req})
            
            if resp != None:
                ct_search = []
                a_raw = common.parseDOM(resp, "row")
                for raw in a_raw:
                    title = common.parseDOM(raw, "item", attrs={"name": "title"})[0]
                    small_desc = common.parseDOM(raw, "item", attrs={"name": "small_desc"})[0]
                    imdb_rate = common.parseDOM(raw, "item", attrs={"name": "imdb_rate"})[0]
                    file_count = common.parseDOM(raw, "item", attrs={"name": "file_count"})[0]
                    kp_rate = common.parseDOM(raw, "item", attrs={"name": "kp_rate"})[0]
                    fid = common.parseDOM(raw, "item", attrs={"name": "fid"})[0]
                    year = common.parseDOM(raw, "item", attrs={"name": "year"})[0]
                    small_cover = common.parseDOM(raw, "item", attrs={"name": "small_cover"})[0]


                    ct_search.append(('?mode=%s&token=%s&portal=%s&fid=%s' % ('film', self.token, self.portal, fid), small_cover, True,
                     {'title': title, 
                      'plot': '%s IMDB: %s Kinopoisk:%s\n%s' % (year, imdb_rate, kp_rate, small_desc),
                      'year':year} ))
                if len(a_raw) >= 12:
                    req = '?mode=%s&token=%s&portal=%s&offset=%s' % ('all', self.token, self.portal, str(int(self.offset) + 12))
                    if self.numb != '': req += '&numb=%s' % self.numb
                    ct_search.append((req, '', True, {'title': self.language(20008)}))
                self.list_items(ct_search, True) 

 
    def m_film(self):
        self.log("-f_play:")
        
        resp = None
        self.authorize()
        if self.get_auth == False:

            req = self.portal + '?token=%s&query=%s' % (self.token, 'get_cinema_desc')
            key = "fid"
            value = self.fid
            req += '&key="%s"&value="%s"' % (key, value)
            resp = self.getPage({"link": req})
        
        if resp != None:
            ct_films = []
            a_files = common.parseDOM(resp, "array", attrs={"name": "files"})
            desc = common.parseDOM(resp, "item", attrs={"name": "full_desc"})[0]
            icon = common.parseDOM(resp, "item", attrs={"name": "big_cover"})[0]
            rest = resp
            rest = rest.replace(common.parseDOM(resp, "array", attrs={"name": "producers"})[0].encode('utf8'), '@@')
            rest = rest.replace(common.parseDOM(resp, "array", attrs={"name": "genres"})[0].encode('utf8'), '@@')
            rest = rest.replace(common.parseDOM(resp, "array", attrs={"name": "actors"})[0].encode('utf8'), '@@')
            title = common.parseDOM(rest, "item", attrs={"name": "title"})[-1]
            for efile in a_files:
                a_quals = common.parseDOM(resp, "array", attrs={"name": "qualities"})
                for quals in a_quals:
                    a_lid = common.parseDOM(quals, "item", attrs={"name": "lid"})
                    a_qual= common.parseDOM(quals, "item", attrs={"name": "quality_number"})
                    a_comb = zip(a_lid, a_qual)
                    for lid, qual in a_comb:
                        ct_films.append(('?mode=%s&token=%s&portal=%s&lid=%s' % ('tvplay', self.token, self.portal, lid), icon, False,
                                {'title': 'Q%s-%s' % (qual, title), 
                                 'plot': desc} ))
                        
            self.list_items(ct_films, False) 
                                                
#            url = common.parseDOM(resp, "item", attrs={"name": "url"})[0]
#            item = xbmcgui.ListItem(path = url)
#            xbmcplugin.setResolvedUrl(self.handle, True, item)
#            self.log("-play_url:%s" % url)                          
            

                                

    def get_text(self, prompt='', hidden = False):
        kbd = xbmc.Keyboard()
        kbd.setDefault('')
        if hidden: kbd.setHiddenInput(True)
        kbd.setHeading(prompt)
        kbd.doModal()
        keyword = None
        if kbd.isConfirmed():
                keyword = kbd.getText()
        return keyword

    # *** Add-on helpers
    def log(self, message):
        if self.debug:
            print "[%s LOG]: %s" % (common.plugin, message.encode('utf8'))

    def error(self, message):
        print "[%s ERROR]: %s" % (common.plugin, message)

    def showErrorMessage(self, msg):
        print msg
        xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("ERROR", msg, str(10 * 1000)))

    def encode(self, string):
        return string.decode('cp1251').encode('utf-8')
        
rodina = RodinaTV()
rodina.main()        