# -*- coding: utf-8 -*-
#!/usr/bin/python
# Writer (c) 2012, Silhouette, E-mail: otaranda@hotmail.com
# Rev. 0.1.4



import urllib,urllib2,re,sys,os,time
import xbmcplugin,xbmcgui,xbmcaddon

pluginhandle = int(sys.argv[1])
__addon__       = xbmcaddon.Addon(id='plugin.video.inetcom.tv') 
#fanart    = xbmc.translatePath( __addon__.getAddonInfo('path') + 'fanart.jpg')
#xbmcplugin.setPluginFanart(pluginhandle, fanart)

INC_url = 'http://inetcom.tv'
INC_ch = '/channel/all'


dbg = 0
def dbg_log(line):
  if dbg: xbmc.log(line)

def get_url(url, data = None, cookie = None, save_cookie = False, referrer = None):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Opera/9.80 (X11; Linux i686; U; ru) Presto/2.7.62 Version/11.00')
    req.add_header('Accept', 'text/html, application/xml, application/xhtml+xml, */*')
    req.add_header('Accept-Language', 'ru,en;q=0.9')
    if cookie: req.add_header('Cookie', cookie)
    if referrer: req.add_header('Referer', referrer)
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

        
def INC_prls(url):
    dbg_log('INC_prls')
    
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
            uri = sys.argv[0] + '?mode=PLAY'
            uri += '&url='+urllib.quote_plus(INC_url + href) + '&cook=' + urllib.quote_plus(mycookie)
            item.setInfo( type='video', infoLabels={'title': name, 'plot': descr})
            item.setProperty('IsPlayable', 'true')
            dbg_log(uri)
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item)

    xbmcplugin.endOfDirectory(pluginhandle)    
    
def INC_play(url, name, thumbnail, plot, mycookie):
    dbg_log('-INC_play')
    response    = get_url(url, cookie = mycookie, referrer = INC_url + INC_ch)
    lnks_ls   = re.compile("lnks = \['(.+?)'\];").findall(response)

    if len(lnks_ls):
        dbg_log(lnks_ls[0])
        item = xbmcgui.ListItem(path =  lnks_ls[0])
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
name=''
plot=''
cook=''
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
    cook=urllib.unquote_plus(params['cook'])
    dbg_log('-COOK:'+ cook + '\n')
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






if mode == 'PLAY': INC_play(url, name, thumbnail, plot, cook)
elif mode == None: INC_prls(INC_url + INC_ch)

dbg_log('CLOSE:')

