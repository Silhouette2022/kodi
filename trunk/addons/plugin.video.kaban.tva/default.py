# -*- coding: utf-8 -*-
#!/usr/bin/python
# Writer (c) 2012, Silhouette, E-mail: 
# Rev. 0.2.3



import urllib,urllib2,re,sys,os,time
import xbmcplugin,xbmcgui,xbmcaddon

pluginhandle = int(sys.argv[1])
__addon__       = xbmcaddon.Addon(id='plugin.video.kaban.tva') 
#fanart    = xbmc.translatePath( __addon__.getAddonInfo('path') + 'fanart.jpg')
#xbmcplugin.setPluginFanart(pluginhandle, fanart)

KTV_url = 'http://kaban.tv'
KTV_arch = '/archive'
KTV_time = 'http://kaban.tv/current-time'
#KTV_url_arch = KTV_url + KTV_arch

dbg = 0
def dbg_log(line):
  if dbg: xbmc.log(line)

def getURL(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Opera/9.80 (X11; Linux i686; U; ru) Presto/2.7.62 Version/11.00')
    req.add_header('Accept', 'text/html, application/xml, application/xhtml+xml, */*')
    req.add_header('Accept-Language', 'ru,en;q=0.9')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    return link

def KTV_start():
    
    dbg_log('-KTV_start')

    name='Live TV'
    item = xbmcgui.ListItem(name)
    uri = sys.argv[0] + '?mode=PRLS'
    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

    name='Archives'
    item = xbmcgui.ListItem(name)
    uri = sys.argv[0] + '?mode=CHLS'
    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  

    xbmcplugin.endOfDirectory(pluginhandle)  
    
    #KTV_chls(KTV_url + KTV_arch)
        
def KTV_prls(url):
    dbg_log('KTV_prls')
    
    http = getURL(url)
    pr_ls = re.compile('<li><a class="(.+?)" href="(.+?)"><span>(.+?)</span></a></li>').findall(http)
    
    thumbnail = ''
    if len(pr_ls):
        for eng,href,descr in pr_ls:
            name = descr
            dbg_log(name)
            item = xbmcgui.ListItem(name, iconImage=thumbnail, thumbnailImage=thumbnail)
            uri = sys.argv[0] + '?mode=PLAY'
            uri += '&url='+urllib.quote_plus(url + href)
            item.setInfo( type='video', infoLabels={'title': name, 'plot': descr})
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item)

    xbmcplugin.endOfDirectory(pluginhandle)    
    
def KTV_play(url, name, thumbnail, plot):
    dbg_log('-KTV_play')
    response    = getURL(url)
    rtmp_file   = re.compile('"file":"http://(.+?)/playlist').findall(response)[0]
    dbg_log(rtmp_file)
    st_ls = rtmp_file.split('/')
    if len(st_ls):
        rtmp_streamer = 'http://' + st_ls[0] + '/' + st_ls[1]
    else:
        return
    
    furl = '%s'%('rtmp://' + rtmp_file)
    furl += ' swfUrl=%s'%(KTV_url + '/uppod.swf')
    furl += ' pageUrl=%s'%KTV_url
    furl += ' tcUrl=%s'%rtmp_streamer
    furl += ' flashVer=\'WIN 11,2,202,235\''
    
    dbg_log(furl)

    xbmc.log('furl = %s'%furl)
    item = xbmcgui.ListItem(path = furl)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)
             
        
def KTV_chls(url):
    dbg_log('-KTV_chls')

    try:
        http = getURL(url)
    except:
        xbmcplugin.endOfDirectory(pluginhandle)
        return

    http = getURL(url)
    ch_ls = re.compile('href="' + KTV_arch +'(.+?)"><span><b>(.+?)</b>').findall(http)
    for arlnk, description in ch_ls:
        title = description
        is_folder = True
        thumbnail = ''
        arlnk = re.sub('-','~',arlnk)

        uri = sys.argv[0] + '?mode=DTLS'
        uri += '&url='+urllib.quote_plus(arlnk)
        uri += '&name='+urllib.quote_plus(title)
        uri += '&plot='+urllib.quote_plus(description)
        uri += '&thumbnail='+urllib.quote_plus(thumbnail)
        dbg_log(title)
        item=xbmcgui.ListItem(title, iconImage=thumbnail, thumbnailImage=thumbnail)
        item.setInfo( type='video', infoLabels={'title': title, 'plot': description})
        xbmcplugin.addDirectoryItem(pluginhandle,uri,item,is_folder)
    xbmcplugin.endOfDirectory(pluginhandle)

def KTV_dates(furl, thumbnail):
    dbg_log('-KTV_dates')
    
    url = re.sub('~','-',furl)
    http = getURL(KTV_url + KTV_arch + url)
    oneline = re.sub('[\r\n]', '', http)
    dt_ls = re.compile('<a href="' + KTV_arch + url + '/([A-Za-z0-9/_-]+?)"> +?<span>').findall(oneline)

    if len(dt_ls):
        http = getURL(KTV_time)
        cdate = re.compile('"date":"(.+?)"').findall(http)[0]
        for i in range(len(dt_ls) - 1, 0, -1):
            descr = dt_ls[i]
            dbg_log(descr)
            if descr <= cdate:
                item = xbmcgui.ListItem(descr, iconImage=thumbnail, thumbnailImage=thumbnail)
                uri = sys.argv[0] + '?mode=GDLS'
                uri += '&url='+urllib.quote_plus(KTV_url + KTV_arch + furl + '/' + descr)
                uri += '&thumbnail='+urllib.quote_plus(thumbnail)
                xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  

    xbmcplugin.endOfDirectory(pluginhandle)
    
    

def KTV_guide(furl, thumbnail):
    dbg_log('KTV_guide')
    
    url = re.sub('~','-',furl)
    http = getURL(url)
    oneline = re.sub('[\r\n]', '', http)
    tr_ls = re.compile('<tr align="top">(.+?)</tr>').findall(oneline)
    
    if len(tr_ls):
        tm_ls = []
        surl = re.sub(KTV_url, '', url)
        for tr in tr_ls:
            tm_ls.append(re.search('<td valign="top">(.+?)</td>', tr).group(1))
            gd_ls = re.compile('<a href="' + surl + '/(.+?)">(.+?) +?</a>').findall(oneline)

        i = 0
        if len(gd_ls):
            for href,descr in gd_ls:
                name=tm_ls[i] + '-' + re.sub('\&#034;' ,'\"', descr.strip())
                dbg_log(name)
                item = xbmcgui.ListItem(name, iconImage=thumbnail, thumbnailImage=thumbnail)
                uri = sys.argv[0] + '?mode=PLAR'
                uri += '&url='+urllib.quote_plus(furl + '/' + re.sub(':', '~', tm_ls[i]))
                item.setInfo( type='video', infoLabels={'title': name, 'plot': descr})
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(pluginhandle, uri, item)
                i += 1

    xbmcplugin.endOfDirectory(pluginhandle)    
    
def KTV_plarch(url, name, thumbnail, plot):
    
    furl = re.sub('-', '/', url)
    furl = re.sub('~', '-', furl)

    furl  = re.sub(KTV_url + KTV_arch, 'http://213.186.127.242', furl)
    furl += '.flv'
    xbmc.output('furl = %s'%furl)
    item = xbmcgui.ListItem(path = furl)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)
    
    #213.186.127.242/karusel/2012/05/21/00-00.flv
    #http://www.kaban.tv/archive/pervii-kanal/2012-05-21/414051

    
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
name=''
plot=''
mode=None
#thumbnail=fanart
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
    name=urllib.unquote_plus(params['name'])
    dbg_log('-NAME:'+ name + '\n')
except: pass
try: 
    thumbnail=urllib.unquote_plus(params['thumbnail'])
    dbg_log('-THAMB:'+ thumbnail + '\n')
except: pass
try: 
    plot=urllib.unquote_plus(params['plot'])
    dbg_log('-PLOT:'+ plot + '\n')
except: pass





if mode == 'PLAR': KTV_plarch(url, name, thumbnail, plot)
elif mode == 'PLAY': KTV_play(url, name, thumbnail, plot)
elif mode == 'PRLS': KTV_prls(KTV_url)
elif mode == 'CHLS': KTV_chls(KTV_url + KTV_arch)
elif mode == 'DTLS': KTV_dates(url, thumbnail)
elif mode == 'GDLS': KTV_guide(url, thumbnail)
elif mode == None: KTV_start()

dbg_log('CLOSE:')

