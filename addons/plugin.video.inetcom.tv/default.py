# -*- coding: utf-8 -*-
#!/usr/bin/python
# Writer (c) 2012, Silhouette, E-mail: otaranda@hotmail.com
# Rev. 0.2.0



import urllib,urllib2,re,sys,os,time
import xbmcplugin,xbmcgui,xbmcaddon
import json

pluginhandle = int(sys.argv[1])
__addon__       = xbmcaddon.Addon(id='plugin.video.inetcom.tv') 
#fanart    = xbmc.translatePath( __addon__.getAddonInfo('path') + 'fanart.jpg')
#xbmcplugin.setPluginFanart(pluginhandle, fanart)

INC_url = 'http://inetcom.tv'
INC_ch = '/channel/all'
INC_pr = '/tvprogram/index'
INC_cat = '/tvprogram/ajaxShowChannels/cat/'
INC_date = '/date/'
INC_ajch = '/tvprogram/ajaxShowChannel/ch/'


dbg = 0
def dbg_log(line):
  if dbg: xbmc.log(line)

def get_url(url, data = None, cookie = None, save_cookie = False, referrer = None, accept = None):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 5.1; rv:16.0) Gecko/20100101 Firefox/16.0')
    if accept == None: req.add_header('Accept', 'text/html, application/xml, application/xhtml+xml, */*')
    if accept == 'json': req.add_header('Accept', 'application/json, text/javascript, */*; q=0.01')
    req.add_header('Accept-Language', 'en-US,en;q=0.5')
    req.add_header('Accept-Encoding', 'gzip, deflate')
    req.add_header('Connection:', 'keep-alive')
    req.add_header('X-Requested-With', 'XMLHttpRequest')
    if referrer: req.add_header('Referer', referrer)
    if cookie: req.add_header('Cookie', cookie)

    if data: 
        response = urllib2.urlopen(req, data)
    else:
        response = urllib2.urlopen(req)
    link=response.read()
    if save_cookie:
        setcookie = response.info().get('Set-Cookie', None)
        if setcookie:
            setcookie = re.search('([^=]+=[^=;]+)', setcookie).group(1)
            link = link + '<cookie>' + setcookie + '</cookie>'
    
    response.close()
    return link


def INC_start():
    
    dbg_log('-INC_start')

    if 1:
        name='Live TV'
        item = xbmcgui.ListItem(name)
        uri = sys.argv[0] + '?mode=live'
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
    
        name='Archives'
        item = xbmcgui.ListItem(name)
        uri = sys.argv[0] + '?mode=chls'
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
    
        xbmcplugin.endOfDirectory(pluginhandle)  
    else:
        DTV_online(DTV_url, 'prls')
        
                
def INC_live(url):
    dbg_log('INC_live')
    
    http = get_url(url, save_cookie = True, referrer = INC_url)
    mycookie = re.search('<cookie>(.+?)</cookie>', http).group(1)
    dbg_log(mycookie)
    oneline = re.sub('[\r\n]', ' ', http)
    pr_ls = re.compile('<tr > +?<td class="col01"><a href="(.+?)"><img src="(.+?)"  alt="(.+?)" /></a></td>').findall(oneline)

    if len(pr_ls):
        for href,logo,descr in pr_ls:
            name = descr
            dbg_log(name)
            item = xbmcgui.ListItem(name, iconImage=INC_url + logo, thumbnailImage=INC_url + logo)
            uri = sys.argv[0] + '?mode=play'
            uri += '&url='+urllib.quote_plus(INC_url + href) + '&cook=' + urllib.quote_plus(mycookie)
            item.setInfo( type='video', infoLabels={'title': name, 'plot': descr})
            item.setProperty('IsPlayable', 'true')
            dbg_log(uri)
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item)

    xbmcplugin.endOfDirectory(pluginhandle)    


def INC_play(url, mycookie):
    dbg_log('-INC_play')
    response = get_url(url, cookie = mycookie, referrer = INC_url + INC_ch)
    lnks_ls = re.compile("lnks = \['(.+?)'\];").findall(response)

    if len(lnks_ls):
        dbg_log(lnks_ls[0])
        item = xbmcgui.ListItem(path =  lnks_ls[0])
        xbmcplugin.setResolvedUrl(pluginhandle, True, item)



def INC_chls():
    dbg_log('-INC_chls')
    http = get_url(INC_url + INC_ch, save_cookie = True, referrer = INC_url)
    mycookie = re.search('<cookie>(.+?)</cookie>', http).group(1)
    dbg_log(mycookie)
    oneline = re.sub('[\r\n]', ' ', http)
    pr_ls = re.compile('<tr > +?<td class="col01"><a href="(.+?)"><img src="(.+?)"  alt="(.+?)" /></a></td>').findall(oneline)
    print pr_ls
    if len(pr_ls):
        for href,logo,name in pr_ls:
            dbg_log(name)
            item = xbmcgui.ListItem(name, iconImage=INC_url + logo, thumbnailImage=INC_url + logo)
            uri = sys.argv[0] + '?mode=dtls'
            uri += '&url='+urllib.quote_plus(INC_url + href) + '&name='+urllib.quote_plus(name)
            uri += '&thumbnail=' + urllib.quote_plus(INC_url + logo)
            uri += '&cook=' + urllib.quote_plus(mycookie)
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
            dbg_log(uri)

    xbmcplugin.endOfDirectory(pluginhandle)


def INC_dtls(url, name, thumbnail, mycookie):
    dbg_log('-INC_dtls')
    response = get_url(url, cookie = mycookie, referrer = INC_url + INC_ch)
    id_ls = re.compile("currentChId=(.+?);").findall(response)
    if len(id_ls) == 0:
        id_ls = re.compile("var current_channel = (.+?);").findall(response)
    if len(id_ls):
        dbg_log(id_ls[0])
        dtls = re.compile('<li class="(.*?)"><a href="(.*?)">..</a><span class="date">').findall(response)
        if len(dtls):
            today = False
            for cl, dt in reversed(dtls):
                if cl == 'active': today = True
                if today:
                    item = xbmcgui.ListItem(dt, iconImage=thumbnail, thumbnailImage=thumbnail)
                    uri = sys.argv[0] + '?mode=prls'
                    uri += '&url='+urllib.quote_plus(INC_url + INC_ajch + id_ls[0] + INC_date + dt)
                    uri += '&name='+urllib.quote_plus(name) + '&pdate='+urllib.quote_plus(dt)
                    uri += '&id='+urllib.quote_plus(id_ls[0]) + '&thumbnail=' + urllib.quote_plus(thumbnail)
                    uri += '&cook=' + urllib.quote_plus(mycookie)
                    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
    
    xbmcplugin.endOfDirectory(pluginhandle)


def INC_prls(url, id, name, pdate, thumbnail, mycookie):
    dbg_log('-INC_prls')
    response = get_url(url, cookie = mycookie, referrer = INC_url + INC_ch)
    jdata = json.loads(response, encoding="cp1251")
    #print json.dumps(jdata, encoding="cp1251")
    
    for it in jdata:
      if it == 'schedules':
          for ent in jdata[it]:
              item = xbmcgui.ListItem(ent[u'startTime'] + '-' + ent[u'title'], iconImage=thumbnail, thumbnailImage=thumbnail)
              uri = sys.argv[0] + '?mode=arpl'
              uri += '&id='+urllib.quote_plus(id) + '&name='+urllib.quote_plus(name)
              uri += '&pdate='+urllib.quote_plus(pdate) + '&ptime='+urllib.quote_plus(ent[u'startTime'])
              item.setInfo( type='video', infoLabels={'title': name, 'plot': name})
              item.setProperty('IsPlayable', 'true')              
              xbmcplugin.addDirectoryItem(pluginhandle, uri, item)

    xbmcplugin.endOfDirectory(pluginhandle)


def INC_arpl(url, id, name, pdate, ptime):
    dbg_log('-INC_arpl')
    vlink = 'http://194.187.205.237' + '/video/' + id + '/' + pdate + '/' + ptime + '_' + name +'.mkv'
    dbg_log(vlink)
    item = xbmcgui.ListItem(path =  vlink)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)
        
        

   
def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]
    return param

params=get_params()
url=None
id=''
name=''
pdate=''
ptime=''
plot=''
cook=''
mode=None
thumbnail=''

dbg_log('OPEN:')

try:
    mode=params['mode']
    dbg_log('-MODE:'+ mode + '\n')
except: pass
try:
    url=urllib.unquote_plus(params['url'])
    dbg_log('-URL:'+ url + '\n')
except: pass
try:
    cook=urllib.unquote_plus(params['cook'])
    dbg_log('-COOK:'+ cook + '\n')
except: pass
try:
    id=urllib.unquote_plus(params['id'])
    dbg_log('-ID:'+ id + '\n')
except: pass
try:
    name=urllib.unquote_plus(params['name'])
    dbg_log('-NAME:'+ name + '\n')
except: pass
try:
    pdate=urllib.unquote_plus(params['pdate'])
    dbg_log('-PDATE:'+ pdate + '\n')
except: pass
try:
    ptime=urllib.unquote_plus(params['ptime'])
    dbg_log('-PTIME:'+ ptime + '\n')
except: pass
try: 
    thumbnail=urllib.unquote_plus(params['thumbnail'])
    dbg_log('-THAMB:'+ thumbnail + '\n')
except: pass
try: 
    plot=urllib.unquote_plus(params['plot'])
    dbg_log('-PLOT:'+ plot + '\n')
except: pass






if mode == 'play': INC_play(url, cook)
elif mode == 'live': INC_live(INC_url + INC_ch)
elif mode == 'chls': INC_chls()
elif mode == 'dtls': INC_dtls(url, name, thumbnail, cook)
elif mode == 'prls': INC_prls(url, id, name, pdate, thumbnail, cook)
elif mode == 'arpl': INC_arpl(url, id, name, pdate, ptime)
elif mode == None: INC_start()

dbg_log('CLOSE:')

