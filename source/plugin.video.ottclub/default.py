#!/usr/bin/python
# -*- coding: utf-8 -*-
# Writer (c) 2018, Silhouette, E-mail: 
# Rev. 0.4.2

import urllib,urllib2, os, re, sys
import xbmcplugin,xbmcgui,xbmcaddon
import requests, json
from collections import OrderedDict
import random

dbg = 0

__addon__ = xbmcaddon.Addon(id='plugin.video.ottclub')

ott_url = "http://" + __addon__.getSetting('url')
epg_now = ott_url + "/api/channel_now"
epg_chan = ott_url + "/api/channel/"
ott_img = ott_url + "/images/"
ott_stream = ott_url + "/stream/%s/%s.m3u8"
KEY = __addon__.getSetting('key')
pluginhandle = int(sys.argv[1])

def QT(url): return urllib.quote_plus(url)

def dbg_log(line):
    if dbg: xbmc.log(line)
    
def req_url(url, opts = None, cookies = None, params = None, data = None):
    dbg_log("req_url=>%s"%url)
    dbg_log("_params=>%s"%str(params))
    

    headers = {'User-Agent' : 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:42.0) Gecko/20100101 Firefox/42.0',
               'Accept' : '*/*',
               'Accept-Language' : 'ru,en;q=0.9'
               }
    if opts: 
        headers.update(opts)
        dbg_log("_opts=>%s"%str(opts))
        
    if data :
        dbg_log("_data=>%s"%str(data))
        r = requests.post(url, headers=headers, cookies = cookies, params = params, data = data)
    else:
        r = requests.get(url, headers=headers, cookies = cookies, params = params)
        
    return r

def track(page2, session):
    
    try: uuuid = __addon__.getSetting('uuid')
    except: uuuid = ''

    try:
        if uuuid == '':
            import uuid
            import hashlib
            uuuid = '%s' % hash(uuid.uuid4())
            __addon__.setSetting('uuid', uuuid)
        usr = __addon__.getSetting('url') + '/' + uuuid
        page = __addon__.getSetting('url') + '/' + page2 
        gif = req_url("http://c.statcounter.com/t.php?sc_project=11663901&camefrom="+page+"&u="+usr+"&java=0&security=0f9f0036&sc_random="+session+"&sc_snum=1&invisible=1")
    except:
        dbg_log("http://c.statcounter.com/t.php?sc_project=11663901&camefrom="+page+"&u="+usr+"&java=0&security=0f9f0036&sc_random="+session+"&sc_snum=1&invisible=1")


def uni2enc(ustr):
    raw = ''
    uni = unicode(ustr, 'utf8')
    uni_sz = len(uni)
    for i in xrange(len(ustr)):
        raw += ('%%%02X') % ord(ustr[i])        
    return raw
    
def uni2cp(ustr):
    raw = ''
    uni = unicode(ustr, 'utf8')
    uni_sz = len(uni)
    for i in range(uni_sz):
        raw += ('%%%02X') % ord(uni[i].encode('cp1251'))
    return raw

def cached_rst(type):
    dbg_log("-cached_rst:")
    fn = xbmc.translatePath('special://temp/' + 'ottepg_' + type + '.tmp')

    if os.path.isfile(fn) == True:
        dbg_log("--exist")
        try: os.remove(fn)
        except: pass
        
def cached_get(type):
    dbg_log("-cached_get: %s" % type)
    cache = ''
    
    if type == 'now':
        cquery = epg_now
    else:
        cquery = epg_chan + type
        
    fn = xbmc.translatePath('special://temp/' + 'ottepg_' + type + '.tmp')
    tt = time.time()
    dbg_log("-tt: %s" % tt)
    
    if os.path.isfile(fn) == True:
        dbg_log("--exist")
        try:
            cf = open(fn, 'r')
            dbg_log("--opened")
            slast = cf.readline()
            flast = float(slast)
        except: flast = 0.0
        
        tdelta = 300
        
        if abs(tt - flast) < tdelta:
            dbg_log("--toread")
            try: 
                ctype = cf.readline()
                if ctype.strip() == type:
                    cache = cf.readline()
                    dbg_log("--readline")
            except: pass
        cf.close()
        
    if cache == '':
        dbg_log("--empty")

        req = req_url(cquery)
        resp = req.content

        if resp != None:
            dbg_log("--gotit")
            cf = open(fn, 'w')
            cf.write(str(tt) + '\n')
            cf.write(type + '\n')
            cf.write(resp + '\n')
            cf.close()
            cache = resp
    return cache


from simpleplugin import Plugin
import time, calendar


plugin = Plugin()

@plugin.action()
def root():

    rand = str(random.random())
        
    return [{'label': 'LiveTV',
            'url': plugin.get_url(action='live', rand=rand)},
            {'label': 'Archive',
            'url': plugin.get_url(action='arch', rand=rand)},
            {'label': 'Settings',
            'url': plugin.get_url(action='settings', rand=rand)}]


@plugin.action()
def live(params):
    dbg_log("-live")

    if (params.group == None or params.group == '') and __addon__.getSetting('groups') != 'false':
        return groups(params)
    
    req = cached_get('now')
    try:
        d_epg = json.loads(req, object_pairs_hook=OrderedDict)
    except:
        cached_rst('now')
        return []
    

    view_epg = __addon__.getSetting('view_epg')
    use_percent = __addon__.getSetting('use_percent')
    use_time = __addon__.getSetting('use_time')
    chans =[]
    for id in d_epg:

#         if d_epg[id]['rec'] == '1':
#             dts = time.localtime()
#             dnow = int(time.mktime((dts.tm_year, dts.tm_mon, dts.tm_mday, 0, 0, 0, 0, 0, 0)))
#             uri2 = sys.argv[0] + '?mode=aepg&numb=%s&portal=%s&pwd=%s&rec=%s&icon=%s&dt=%s' % (number, QT(self.portal), has_passwd, has_record, QT(icon), dnow)
#             if self.cat != '': uri2 += '&cat=' + self.cat
#             if self.sort != '': uri2 += '&sort=' + self.sort
#             popup.append((self.lng['go2arch'], 'XBMC.Container.Update(%s)'%uri2,))
        if params.group == None or params.group == "" or params.group == d_epg[id]['category']['class']:

            plot = ''
            title2nd = ''
            t2len = 0
            title = d_epg[id]['channel_name'].encode('utf8')
            utstart = d_epg[id]['time']
            utstop = d_epg[id]['time_to']
            utdur = d_epg[id]['duration']
            ename = d_epg[id]['name'].encode('utf8')
            edescr = d_epg[id]['descr'].encode('utf8')
            cutnow = calendar.timegm(time.gmtime())
            icon = ott_img + d_epg[id]['img']
            utb = time.localtime(int(utstart))
            ute = time.localtime(int(utstop))
            ebgn = '%02d:%02d'%(utb.tm_hour, utb.tm_min)
            eend = '%02d:%02d'%(ute.tm_hour, ute.tm_min)
    #         try:
            if view_epg == 'true' and title2nd == '':
                if use_percent == 'true':
                    pcent = ((cutnow- float(utstart)) * 100) / float(utdur)
                    stmp = '[%d %%]' % pcent
                    t2len += len(stmp) 
                    title2nd = '[COLOR FF00BB66]%s[/COLOR]' % stmp
                if use_time == 'true':
                    utb = time.localtime(int(utstart))
                    ute = time.localtime(int(utstop))
                    stmp = '%s-%s' % (ebgn, eend)
                    t2len += (len(stmp) + 1) 
                    title2nd += ' [COLOR FF0084FF]%s[/COLOR]' % stmp
                title2nd += ' %s' % ename
                t2len += (len(ename) + 1)
            plot += '[B][COLOR FF0084FF]%s-%s[/COLOR] [COLOR FFFFFFFF] %s[/COLOR][/B][COLOR FF999999]\n%s[/COLOR]\n' % (ebgn, eend, ename, edescr)
                    
    #         except: pass
            plot = plot.replace('&quot;','`').replace('&amp;',' & ')
            title2nd = title2nd.replace('&quot;','`').replace('&amp;',' & ')
            if not t2len: t2len = len(title)
            
            chans.append({'label': '[B]%s[/B]\n%s' % (title.ljust(int(t2len * 1.65)), title2nd),
                          'info': {'video':{'title': '[B]%s[/B]\n%s' % (title.ljust(int(t2len * 1.65)), title2nd), 'plot': plot}},
                          'thumb': icon,
                          'url': plugin.get_url(action='play', url=id, rand=params.rand, day=''),
                          'is_playable': True})
            
    try:
        if __addon__.getSetting('view_mode') == 'true': cont = 'episodes'
        else: cont = None
        
        if cont != None and __addon__.getSetting('wide_mode') == 'true': mode = 55
        else: mode = None
        
        if 'confluence' in xbmc.getSkinDir():
            if cont != None and mode == None: mode = 504
            if mode == 55: mode = 51

        chans = plugin.create_listing(chans, view_mode = mode, content = cont)
    except:
        pass
        
    return chans

@plugin.action()
def play(params):
    """Play video"""
    path = ott_stream%(KEY, params.url)
    extra = ''
    
    if params.timeshift!= None and __addon__.getSetting('askts') != 'false':
         i = xbmcgui.Dialog().select('Use timeshift', ['Yes', 'No'])
         if i:
             params.archive = params.timeshift
             params.timeshift = None

    if params.archive!= None:
        extra += '?archive=%s'%params.archive
        if params.archive_end!= None:  extra += '&archive_end=%s'%params.archive_end

    if params.timeshift!= None and params.timenow != None:
        if extra != "": extra += '&'
        else: extra = '?'
        extra += 'timeshift=%s&timenow=%s'%(params.timeshift, params.timenow)
        
    if params.archive!= None: page = 'arch/' + params.url
    else: page = 'live/' + params.url
    track(QT(page), params.rand)

    return Plugin.resolve_url(path + extra, succeeded=True)

@plugin.action()
def groups(params):
    dbg_log("-groups")

    req = cached_get('now')
    try:
        d_epg = json.loads(req, object_pairs_hook=OrderedDict)
    except:
        cached_rst('now')
        return []

    group = OrderedDict()
    
    for id in d_epg:
        if d_epg[id]['category']['class'] not in group:
            print d_epg[id]['category']['class']
            print d_epg[id]['category']['name'].encode('utf8')
            group[d_epg[id]['category']['class']] = d_epg[id]['category']['name'].encode('utf8')

    chans = []
    for key, title in group.iteritems():
        
        chans.append({'label': title,
                      'info': {'video':{'title': title, 'plot': title}},
                      'url': plugin.get_url(action=params.action, group=key, rand=params.rand, day='now'),
                      'is_playable': False})
        
    return chans


@plugin.action()
def arch(params):
    dbg_log("-arch")

    if (params.group == None or params.group == '') and __addon__.getSetting('groups') != 'false':
        return groups(params)

    req = cached_get('now')
    try:
        d_epg = json.loads(req, object_pairs_hook=OrderedDict)
    except:
        cached_rst('now')
        return []

    chans =[]
    for id in d_epg:
        if d_epg[id]['rec'] == '1':
            if params.group == None or params.group == "" or params.group == d_epg[id]['category']['class']:
                title = d_epg[id]['channel_name'].encode('utf8')
                chans.append({'label': title,
                              'info': {'video':{'title': title, 'plot': title}},
                              'thumb': ott_img + d_epg[id]['img'],
                              'url': plugin.get_url(action='chan', url=id, rand=params.rand, day='now'),
                              'is_playable': False})
        
    return chans

@plugin.action()
def chan(params):
    dbg_log("-chan")
#     req = req_url(epg_now)
    req = cached_get(params.url)
    try:
        d_epg = json.loads(req, object_pairs_hook=OrderedDict)
    except:
        cached_rst(params.url)
        return []
    
    chans =[]
    yday = 500 # fake one
    weekDays = ("ПОНЕДЕЛЬНИК","ВТОРНИК","СРЕДА","ЧЕТВЕРГ","ПЯТНИЦА","СУББОТА","ВОСКРЕСЕНЬЕ")
    tt = time.time()
    tl = time.localtime()
    squeeze = __addon__.getSetting('squeeze')
   
    for x in d_epg['epg_data']:
      if x['rec'] == '1':
        plot = ''
        ename = x['name'].encode('utf8')
        utstart = x['time']
        utstop = x['time_to']
        duration = x['duration']
        edescr = x['descr'].encode('utf8')
        icon = ott_img + x['img']
        utb = time.localtime(int(utstart))
        ute = time.localtime(int(utstop))
        ebgn = '%02d:%02d'%(utb.tm_hour, utb.tm_min)
        eend = '%02d:%02d'%(ute.tm_hour, ute.tm_min)
        title = '%s-%s %s' % (ebgn, eend, ename)
        
        plot = '[B][COLOR FF0084FF]%s-%s[/COLOR] [COLOR FFFFFFFF] %s[/COLOR][/B][COLOR FF999999]\n%s[/COLOR]\n' % (ebgn, eend, ename, edescr)
        plot = plot.replace('&quot;','`').replace('&amp;',' & ')
        title = title.replace('&quot;','`').replace('&amp;',' & ')
        
        futstart = float(utstart)
#        tt = time.time()
        if tt < futstart:
            title = '[COLOR FFDC5310]%s[/COLOR]' % (title)
            pl_get_url = plugin.get_url(action='play', url=params.url, rand=params.rand)
        elif tt < utstop:
            title = '[COLOR FF00FFFF]%s[/COLOR]' % (title)
            pl_get_url = plugin.get_url(action='play', url=params.url, timenow=int(tt), timeshift=utstart, rand=params.rand)
        elif __addon__.getSetting('carc') == 'true':
            pl_get_url = plugin.get_url(action='play', url=params.url, archive=utstart, rand=params.rand)
        else:
            pl_get_url = plugin.get_url(action='play', url=params.url, archive=utstart, archive_end=utstop, rand=params.rand) 
        
        if utb.tm_yday != yday:
            yday = utb.tm_yday
            weekday = "   ---  %s %4d-%02d-%02d  ---" % (weekDays[utb.tm_wday], utb.tm_year, utb.tm_mon, utb.tm_mday)
            weekday = '[B]%s[/B]' % (weekday)
            
            if tt < futstart:
                weekday = '[COLOR FFDC5310]%s[/COLOR]' % (weekday)
            elif tt < utstop:
                weekday = '[COLOR FF00FFFF]%s[/COLOR]' % (weekday)
                
            chans.append({'label': weekday,
                      'info': {'video':{'title': weekday, 'plot': weekday}},
                      #'thumb': icon,
                      'url': plugin.get_url(action='chan', url=params.url, rand=params.rand, day=str(utb.tm_yday)),
                      'is_playable': False})
                      
        if squeeze =='false' or (params.day == 'now' and tl.tm_yday == utb.tm_yday) or (params.day == str(utb.tm_yday)):
            chans.append({'label': title,
                      'info': {'video':{'title': title, 'plot': plot}},
                      'thumb': icon,
                      'url': pl_get_url,
                      'is_playable': True})
        
    try:
        if __addon__.getSetting('view_mode') == 'true': cont = 'episodes'
        else: cont = None
        
        if cont != None and __addon__.getSetting('wide_mode') == 'true': mode = 55
        else: mode = None
        
        if 'confluence' in xbmc.getSkinDir():
            if cont != None and mode == None: mode = 501
            if mode == 55: mode = 51

        chans = plugin.create_listing(chans, view_mode = mode, content = cont)
    except:
        pass
        
    return chans

@plugin.action()
def settings(params):
    __addon__.openSettings()
    cached_rst('now')


if __name__ == '__main__':
    plugin.run()  # Start plugin
