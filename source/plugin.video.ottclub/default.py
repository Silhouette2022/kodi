#!/usr/bin/python
# -*- coding: utf-8 -*-
# Writer (c) 2018, Silhouette, E-mail: 
# Rev. 0.1.2


import urllib,urllib2, os, re, sys
import xbmcplugin,xbmcgui,xbmcaddon
import requests, json
from collections import OrderedDict

dbg = 0

__addon__ = xbmcaddon.Addon(id='plugin.video.ottclub')

ott_url = "http://" + __addon__.getSetting('url')
epg_now = ott_url + "/api/channel_now"
epg_chan = ott_url + "/api/channel/"
ott_img = ott_url + "/images/"
ott_stream = ott_url + "/stream/%s/%s.m3u8"
KEY = __addon__.getSetting('key')
pluginhandle = int(sys.argv[1])

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

def cached_rst(fn):
    dbg_log("-cached_rst:")

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

    return [{'label': 'LiveTV',
            'url': plugin.get_url(action='live')},
            {'label': 'Archive',
            'url': plugin.get_url(action='arch')}]


@plugin.action()
def live():
    dbg_log("-live")
#     req = req_url(epg_now)
    req = cached_get('now')
    try:
        d_epg = json.loads(req, object_pairs_hook=OrderedDict)
    except:
        return []
    

    view_epg = 'true'
    use_percent = 'true'
    use_time = 'true'
    chans =[]
    for id in d_epg:

#         if d_epg[id]['rec'] == '1':
#             dts = time.localtime()
#             dnow = int(time.mktime((dts.tm_year, dts.tm_mon, dts.tm_mday, 0, 0, 0, 0, 0, 0)))
#             uri2 = sys.argv[0] + '?mode=aepg&numb=%s&portal=%s&pwd=%s&rec=%s&icon=%s&dt=%s' % (number, QT(self.portal), has_passwd, has_record, QT(icon), dnow)
#             if self.cat != '': uri2 += '&cat=' + self.cat
#             if self.sort != '': uri2 += '&sort=' + self.sort
#             popup.append((self.lng['go2arch'], 'XBMC.Container.Update(%s)'%uri2,))

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
                      'url': plugin.get_url(action='play', url=id),
                      'is_playable': True})
        
    return chans

@plugin.action()
def play(params):
    """Play video"""
    path = ott_stream%(KEY, params.url)
    extra = ''
    tt = int(time.time())
    if params.archive!= None:
        extra += '?archive=%s'%params.archive
        if params.archive_end!= None:  extra += '&archive_end=%s'%params.archive_end

#     if params.timeshift!= None and params.timenow != None:
#         if extra != "": extra += '&'
#         extra += 'timeshift=%s&timenow=%s'%(params.timeshift, params.timenow)
#     if extra != "": extra = '?' + extra

    return Plugin.resolve_url(path + extra, succeeded=True)

@plugin.action()
def arch():
    dbg_log("-arch")
#     req = req_url(epg_now)
    req = cached_get('now')
    try:
        d_epg = json.loads(req, object_pairs_hook=OrderedDict)
    except:
        return []
    

    view_epg = 'true'
    use_percent = 'true'
    use_time = 'true'
    chans =[]
    for id in d_epg:
      if d_epg[id]['rec'] == '1':
        title = d_epg[id]['channel_name'].encode('utf8')
        chans.append({'label': title,
                      'info': {'video':{'title': title, 'plot': title}},
                      'thumb': ott_img + d_epg[id]['img'],
                      'url': plugin.get_url(action='chan', url=id),
                      'is_playable': False})
        
    return chans

@plugin.action()
def chan(params):
    dbg_log("-chan")
#     req = req_url(epg_now)
    req = cached_get(params.url)
    d_epg = json.loads(req, object_pairs_hook=OrderedDict)
    
    chans =[]
    
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
        tt = time.time()
        if tt < futstart:
#             if (tt - futstart > 330) nd (tt - futstart < duration) :
#                 title = '[COLOR FF00FFFF]' + '%s[/COLOR]' % (title)
#             else:                
                title = '[COLOR FFdc5310]%s[/COLOR]' % (title)
        
        chans.append({'label': title,
                      'info': {'video':{'title': title, 'plot': plot}},
                      'thumb': icon,
                      'url': plugin.get_url(action='play', url=params.url, archive=utstart, archive_end=utstop),
                      'is_playable': True})
        
    return chans


if __name__ == '__main__':
    plugin.run()  # Start plugin
