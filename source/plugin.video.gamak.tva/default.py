# -*- coding: utf-8 -*-
#!/usr/bin/python
# Writer (c) 2012, Silhouette, E-mail: silhouette2022@gmail.com
# Rev. 0.0.1



import urllib,urllib2,re,sys,os,time
import xbmcplugin,xbmcgui,xbmcaddon

#import SimpleDownloader as downloader
#downloader = downloader.SimpleDownloader()
#downloader.dbg = True

pluginhandle = int(sys.argv[1])
__addon__       = xbmcaddon.Addon(id='plugin.video.gamak.tva') 
#fanart    = xbmc.translatePath( __addon__.getAddonInfo('path') + 'fanart.jpg')
#xbmcplugin.setPluginFanart(pluginhandle, fanart)

GTV_url = 'http://www.gamak.tv'

dbg = 0

def dbg_log(line):
  if dbg: xbmc.log(line)

def getURL(url, data = None, cookie = None, save_cookie = False, referrer = None):
    dbg_log(url)
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Opera/9.80 (X11; Linux i686; U; ru) Presto/2.7.62 Version/11.00')
    req.add_header('Accept', 'text/html, application/xml, application/xhtml+xml, */*')
    req.add_header('Accept-Language', 'ru,en;q=0.9')
    if cookie: req.add_header('Cookie', cookie)
    if referrer: req.add_header('Referer', referrer)
    if data: 
        response = urllib2.urlopen(req, data, timeout=30)
    else:
        response = urllib2.urlopen(req, timeout=30)
    link=response.read()
    if save_cookie:
        setcookie = response.info().get('Set-Cookie', None)
        #print "Set-Cookie: %s" % repr(setcookie)
        #print response.info()['set-cookie']
        if setcookie:
            try:
              setcookie = response.info()['set-cookie']
            except:
              pass
            link = link + '<cookie>' + setcookie + '</cookie>'
    
    response.close()
    #print response.info()
    return link

def GTV_start():
    
    dbg_log('-GTV_start')

    if 1:
        name='Live TV'
        item = xbmcgui.ListItem(name)
        uri = sys.argv[0] + '?mode=PRLS'
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
    
        name='Archives'
        item = xbmcgui.ListItem(name)
        uri = sys.argv[0] + '?mode=CHLS'
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
    
        xbmcplugin.endOfDirectory(pluginhandle)  
    else:
        GTV_online(GTV_url, 'CHLS')
        
        
def toLcTm(tzd, tmst):
    return time.strftime("%H:%M",time.localtime((time.mktime(tmst) - tzd*3600)))

def GTV_online(url, prls):
    dbg_log('-GTV_online')

    try:
        http = getURL(url)
    except:
        print 'GTVA - except1'
        xbmcplugin.endOfDirectory(pluginhandle)
        return
    
    oneline = re.sub( '\n', ' ', http)
#     print oneline

    chndls = re.compile('<td> *?<a href="(.*?)" title="(.*?)"> *?<img src="(.*?)" alt=".*?" /> *?</a></td>').findall(oneline)
#     print chndls
    for href, title, img in chndls:
        is_folder = True
        description = ''
        thumbnail = img.replace('/mini', '')
        uri = sys.argv[0] + '?mode=ARLS'
        uri += '&url='+urllib.quote_plus(GTV_url + href)
        uri += '&name='+urllib.quote_plus(title)
        #uri += '&plot='+urllib.quote_plus(description)
        uri += '&thumbnail='+urllib.quote_plus(thumbnail)

        dbg_log(title)
        item=xbmcgui.ListItem(title, iconImage=thumbnail, thumbnailImage=thumbnail)
        item.setInfo( type='video', infoLabels={'title': title, 'plot': description})
        #item.setProperty('fanart_image',thumbnail)
        xbmcplugin.addDirectoryItem(pluginhandle,uri,item,is_folder)
#         dbg_log(uri)
        
    xbmcplugin.endOfDirectory(pluginhandle)



def GTV_dates(url, thumbnail):
    dbg_log('-GTV_dates')

    item = xbmcgui.ListItem('Today', iconImage=thumbnail, thumbnailImage=thumbnail)
    uri = sys.argv[0] + '?mode=ARLS'
    uri += '&url='+urllib.quote_plus(url)
    uri += '&thumbnail='+urllib.quote_plus(thumbnail)
    dbg_log('uri = %s'%uri)
    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
            
    http = getURL(url, save_cookie = True, referrer = GTV_url)
    mycookie = re.search('<cookie>(.+?)</cookie>', http).group(1)
    #print http
    dtls = re.compile('<td style="(.*?)"><a href="(.*?)">(.*?)</a></td>').findall(http)
    #print dtls
    if len(dtls):
        for style, href, descr in dtls:
            item = xbmcgui.ListItem(descr, iconImage=thumbnail, thumbnailImage=thumbnail)
            uri = sys.argv[0] + '?mode=ARLS'
            uri += '&url='+urllib.quote_plus(GTV_url + href + '00:00/')
            uri += '&name='+urllib.quote_plus(url)
            uri += '&thumbnail='+urllib.quote_plus(thumbnail)
            uri += '&cook='+urllib.quote_plus(mycookie)
            dbg_log('uri = %s'%uri)
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  

    xbmcplugin.endOfDirectory(pluginhandle)
    
    

def GTV_archs(url, name2, thumbnail, mycook):
    dbg_log('GTV_archs')
    if mycook != '':
        http = getURL(url, save_cookie = True, cookie = mycook, referrer = url)
    else:
        http = getURL(url, save_cookie = True, referrer = url)
        
    mycookie = re.search('<cookie>(.+?)</cookie>', http).group(1)
    
    oneline = re.sub( '\n', ' ', http)
#     print oneline

# <div style="float:left;padding-bottom:10px;">
# <a href="/pervyi_kanal/2015-11-12/00:00/">ТВ программа на предыдущий день</a>
# </div>
    try: href = re.compile('<div style=".*?"> *?<a href="(.*?)"').findall(oneline)[0]
    except: href = None    
    
    if href != None:
        name= ' << Предыдущий день - ' + href[-17:-7] + ' <<'
        item = xbmcgui.ListItem(name, iconImage=thumbnail, thumbnailImage=thumbnail)
        uri = sys.argv[0] + '?mode=ARLS'
        uri += '&url='+urllib.quote_plus(GTV_url + href)
        uri += '&name='+urllib.quote_plus(name2)
        uri += '&thumbnail='+urllib.quote_plus(thumbnail)
        uri += '&cook='+urllib.quote_plus(mycookie)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
#         dbg_log('uri:' + uri + '\n')         

# <td style="vertical-align: top;"><b>00:40</b></td>  <td style="padding-left:1em;">    <a title="Бастионы России (Смоленск) (12+)" href="/rossiia_1/2015-11-13/00:40/">          Бастионы России (Смоленск) (12+)     </a>    </td>
    prls = re.compile('<td style=".*?"><b>(.*?)</b></td> *?<td style=".*?"> *?<a title="(.*?)" href="(.*?)">(.*?)</a>').findall(oneline)
#     print dtls

    for sttm, plot1, src, descr in prls:
        name=sttm + ' - ' + descr.replace('&quot;', '\"').strip()
        plot=plot1.replace('&quot;', '\"').replace('  ',' ')
        item = xbmcgui.ListItem(name, iconImage=thumbnail, thumbnailImage=thumbnail)
        uri = sys.argv[0] + '?mode=PLAR'
        uri += '&url='+urllib.quote_plus(GTV_url + src)
        uri += '&name='+urllib.quote_plus(name2)
        uri += '&cook='+urllib.quote_plus(mycookie)
        item.setInfo( type='video', infoLabels={'title': name, 'plot': plot})
        item.setProperty('IsPlayable', 'true')
        #item.setProperty('fanart_image',thumbnail)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item)
#         dbg_log('uri:' + uri + '\n')  


    xbmcplugin.endOfDirectory(pluginhandle)    

def GTV_plarch(url, name, mycook):
    dbg_log('-GTV_plarch')
    dbg_log('-url=%s'%url)
    response = getURL('%s/maclist/?_=%d' % (GTV_url, (time.time())*1000), cookie = mycook, referrer = url)
    try: src = re.compile('src="(.*?)"').findall(response)[0]
    except: 
        try: src = re.compile('video_src = "(.*?)"').findall(response)[0]
        except: return
    dbg_log('-src=%s'%src)
    
    pls = src.split("-")

    tm0 = time.mktime(time.strptime(url[-17:-7],"%Y-%m-%d"))
    tm1 = time.mktime(time.strptime(url[-17:-1],"%Y-%m-%d/%H:%M"))
    
    try: uri = '%s-%d-%s'%(pls[0],int(pls[1]) + (tm1 - tm0),pls[2])
#     try: uri = '%s-%d-%s'%(pls[0],tml,pls[2])
    except: uri = srs
    dbg_log('-uri=%s'%uri)
    item = xbmcgui.ListItem(path = uri)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)
# http://www.gamak.tv/rossiia_1/2015-11-13/14:00/
# http://37.220.30.202/video/LsK0Jqg0e3nSzzEkTpWE0g/3/playlist-1447362000-14400.m3u8

         
            
        
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
cook=''

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
try: 
    cook=urllib.unquote_plus(params['cook'])
    dbg_log('-COOK:'+ cook + '\n')
except: pass




if mode == 'PLAR': GTV_plarch(url, name, cook)
elif mode == 'CHLS': GTV_online(GTV_url, mode)
elif mode == 'DTLS': GTV_dates(url, thumbnail)
elif mode == 'ARLS': GTV_archs(url, name, thumbnail, cook)
# elif mode == None: GTV_start()
elif mode == None: GTV_online(GTV_url, 'CHLS')

dbg_log('CLOSE:')


