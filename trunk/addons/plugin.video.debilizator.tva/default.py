# -*- coding: utf-8 -*-
#!/usr/bin/python
# Writer (c) 2012, Silhouette, E-mail: silhouette2022@gmail.com
# Rev. 0.5.2



import urllib,urllib2,re,sys,os,time
import xbmcplugin,xbmcgui,xbmcaddon

pluginhandle = int(sys.argv[1])
__addon__       = xbmcaddon.Addon(id='plugin.video.debilizator.tva') 
#fanart    = xbmc.translatePath( __addon__.getAddonInfo('path') + 'fanart.jpg')
#xbmcplugin.setPluginFanart(pluginhandle, fanart)

DTV_url = 'http://www.debilizator.tv/'

dbg = 0

def dbg_log(line):
  if dbg: xbmc.log(line)

def getURL(url, data = None, cookie = None, save_cookie = False, referrer = None):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Opera/9.80 (X11; Linux i686; U; ru) Presto/2.7.62 Version/11.00')
    req.add_header('Accept', 'text/html, application/xml, application/xhtml+xml, */*')
    req.add_header('Accept-Language', 'ru,en;q=0.9')
    if cookie: req.add_header('Cookie', cookie)
    if referrer: req.add_header('Referer', referrer)
    if data: 
        response = urllib2.urlopen(req, data,timeout=30)
    else:
        response = urllib2.urlopen(req,timeout=30)
    link=response.read()
    if save_cookie:
        setcookie = response.info().get('Set-Cookie', None)
        #print "Set-Cookie: %s" % repr(setcookie)
        if setcookie:
            setcookie = re.search('([^=]+=[^=;]+)', setcookie).group(1)
            link = link + '<cookie>' + setcookie + '</cookie>'
    
    response.close()
    #print response.info()
    return link

def DTV_start():
    
    dbg_log('-DTV_start')

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
        DTV_online(DTV_url, 'CHLS')
        
        
def toLcTm(tzd, tmst):
    return time.strftime("%H:%M",time.localtime((time.mktime(tmst) - tzd*3600)))

def DTV_online(url, prls):
    dbg_log('-DTV_online')

    if prls == 'PRLS':
        dbg_log('FALSE:')

        try:
            msktmht = getURL('http://time.jp-net.ru/');
            msktmls = re.compile('<h1 align=\'center\'>(.*?): (.*?)</h1>').findall(msktmht)
            msktmst = time.strptime(msktmls[0][1] + ' ' + msktmls[1][1], "%Y-%d-%m %H:%M:%S")
            tzdf = round( (time.mktime(msktmst) - time.mktime(time.localtime())) / (3600))
        except:
            pass

    try:
        http = getURL(url)
    except:
        xbmcplugin.endOfDirectory(pluginhandle)
        return
    oneline = re.sub( '\n', ' ', http)
    chndls = re.compile('<div class="chlogo">(.*?)</div> <!-- (left|right)(up|down)part -->').findall(oneline)
    for chndel, rEL, rEU in chndls:
        chells = re.compile('<a href=(.*?)><img src="(.*?)" alt="(.*?)" title="(.*?)"></div>').findall(chndel)
        description = chells[0][3]
        if prls == 'PRLS':
            title = description
            is_folder = False
        else:
            title = re.sub('Смотрите онлайн ', '', description) #'Смотрите онлайн '
            is_folder = True
        thumbnail = chells[0][1].replace('./', url)
        if prls == 'PRLS':
            uri = sys.argv[0] + '?mode=PLAY'
        else:
            uri = sys.argv[0] + '?mode=DTLS'
        uri += '&url='+urllib.quote_plus(url + chells[0][0])
        uri += '&name='+urllib.quote_plus(title)
        uri += '&plot='+urllib.quote_plus(description)
        uri += '&thumbnail='+urllib.quote_plus(thumbnail)
        ptls = re.compile('<div class="prtime">(.*?)</div><div class="prdesc">(.*?)</div>').findall(chndel)
        ptlsln = len(ptls)
        if prls == 'PRLS':
            i = 1
            while ptlsln - i + 1:
                prtm = ptls[ptlsln - i][0]
                prds = ptls[ptlsln - i][1]
                prtmst = time.strptime(msktmls[0][1] + ' ' + prtm, "%Y-%d-%m %H:%M")
                try:
                    tmdf = time.mktime(msktmst) - time.mktime(prtmst)
                    if (((tmdf < 0) and (tmdf > -12*3600.0)) or (tmdf > 12*3600.0)) and (ptlsln > 1):
                        i += 1
                    else:
                        if i > 1:
                            prtmst2 = time.strptime(msktmls[0][1] + ' ' + ptls[ptlsln - i + 1][0], "%Y-%d-%m %H:%M")
                            prtm = toLcTm(tzdf, prtmst) + '-' + toLcTm(tzdf, prtmst2)
                        else:
                            prtm = toLcTm(tzdf, prtmst)
                        title = prtm + " " + prds
                        break
                except:
                    break

        if ptlsln:
            dbg_log(title)
            item=xbmcgui.ListItem(title, iconImage=thumbnail, thumbnailImage=thumbnail)
            item.setInfo( type='video', infoLabels={'title': title, 'plot': description})
            if prls == 'PRLS':
                item.setProperty('IsPlayable', 'true')
            #item.setProperty('fanart_image',thumbnail)
            xbmcplugin.addDirectoryItem(pluginhandle,uri,item,is_folder)
    xbmcplugin.endOfDirectory(pluginhandle)

def DTV_play(url, name, thumbnail, plot):
    dbg_log('-DTV_play')
    response    = getURL(url)
    
    oneline = re.sub( '[\n\r\t]', ' ', response)
    server_ls   = re.compile('<a href="/select_server.cgi\?(.*?)"><div id="bar[0-9]" style="(.*?)"></div></a> *?<script type="text/javascript"> *?\$\(function\(\) \{ *?var value = (.*?);').findall(oneline)
    if(len(server_ls)):
        min = 999
        new_srv = ""
        for ssHref, ssCrap, ssVal in server_ls:
            if(int(ssVal) < min):
                min = int(ssVal)
                new_srv = ssHref
                
        if(new_srv != ""):
            dbg_log('-NEW_SRV:'+ new_srv + '\n')
            #response = getURL(DTV_url + 'select_server.cgi?' + new_srv)
            response = getURL(url, cookie=new_srv)
    
    player_ls   = re.compile("\'flashplayer\': \'(.*?)\'").findall(response)
    streamer_ls   = re.compile("\'streamer\': \'(.*?)\'").findall(response)
    file_ls   = re.compile("\'file\': \'(.*?)\'").findall(response)
    
    if len(streamer_ls):
      if len(player_ls):
        if len(file_ls) :
          rtmp_streamer = streamer_ls[0]
          rtmp_file = file_ls[0]
          SWFObject = DTV_url + player_ls[0] 
     
          furl  = ''
          furl += '%s/%s'%(rtmp_streamer,rtmp_file)
          furl += ' swfUrl=%s'%SWFObject
          furl += ' pageUrl=%s'%url
          furl += ' tcUrl=%s'%rtmp_streamer
          furl += ' swfVfy=True Live=True'
          xbmc.log('furl = %s'%furl)
          item = xbmcgui.ListItem(path = furl)
          xbmcplugin.setResolvedUrl(pluginhandle, True, item)


def DTV_dates(url, thumbnail):
    dbg_log('-DTV_dates')

    item = xbmcgui.ListItem('Today', iconImage=thumbnail, thumbnailImage=thumbnail)
    uri = sys.argv[0] + '?mode=ARLS'
    uri += '&url='+urllib.quote_plus(url)
    uri += '&thumbnail='+urllib.quote_plus(thumbnail)
    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
            
    http = getURL(url)
    oneline = re.sub( '\n', ' ', http)
    dtls = re.compile('<div id="timeselect">(.*?)</div> <!-- timeselect -->').findall(oneline)
    if len(dtls):
        dtells = re.compile('<a href=(.*?)&time=(.*?)> (.*?) </a>').findall(dtls[0])
        for src, tm, descr in dtells:
            item = xbmcgui.ListItem(descr, iconImage=thumbnail, thumbnailImage=thumbnail)
            uri = sys.argv[0] + '?mode=ARLS'
            uri += '&url='+urllib.quote_plus(url + '&time=' + tm)
            uri += '&thumbnail='+urllib.quote_plus(thumbnail)
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  

    xbmcplugin.endOfDirectory(pluginhandle)
    
    

def DTV_archs(url, thumbnail):
    dbg_log('DTV_archs')
    http = getURL(url)
    oneline = re.sub( '\n', ' ', http)
    dtls = re.compile('<a href=\?(.*?)><div class="prtime">(.*?)</div><div class="prdescfull">(.*?)</div></a>').findall(oneline)
    if len(dtls):
        for src, tm, descr in dtls:
            name=tm + ' ' + descr
            item = xbmcgui.ListItem(name, iconImage=thumbnail, thumbnailImage=thumbnail)
            uri = sys.argv[0] + '?mode=PLAR'
            uri += '&url='+urllib.quote_plus(DTV_url + 'tv.cgi?' + src)
            item.setInfo( type='video', infoLabels={'title': name, 'plot': descr})
            item.setProperty('IsPlayable', 'true')
            #item.setProperty('fanart_image',thumbnail)
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item)
            dbg_log('uri:' + uri + '\n')  


    xbmcplugin.endOfDirectory(pluginhandle)    
    
def DTV_plarch(url, name, thumbnail, plot):
    response    = getURL(url)
    
    oneline = re.sub( '[\n\r\t]', ' ', response)
    server_ls   = re.compile('<a href="/select_server.cgi\?(.*?)"><div id="bar[0-9]" style="(.*?)"></div></a> *?<script type="text/javascript"> *?\$\(function\(\) \{ *?var value = (.*?);').findall(oneline)
    if(len(server_ls)):
        min = 999
        new_srv = ""
        for ssHref, ssCrap, ssVal in server_ls:
            if(int(ssVal) < min):
                min = int(ssVal)
                new_srv = ssHref
                
        if(new_srv != ""):
            dbg_log('-NEW_SRV:'+ new_srv + '\n')
            response = getURL(url, cookie=new_srv)
    
    player_ls   = re.compile("\'flashplayer\': \'(.*?)\'").findall(response)
    file_ls   = re.compile("\'playlistfile\': \'(.*?)\'").findall(response)
    print file_ls
    if (len(player_ls) & len(file_ls)):

        SWFObject = DTV_url + player_ls[0]  
        flashparams = re.sub( '\?', '\&', urllib.unquote_plus(file_ls[0])).split('&')
        dbg_log('=flashparams=')
        if dbg: print flashparams

        for i in range(len(flashparams)):
            if flashparams[i].find('time=') != -1:
                rtmp_time = re.sub('time=', '', flashparams[i])
            elif flashparams[i].find('str=') != -1:
                rtmp_str = re.sub('str=', '', flashparams[i])
            elif flashparams[i].find('ch=') != -1:
                rtmp_ch = re.sub('ch=', '', flashparams[i])
            
        itime = int(rtmp_time)
        rtime = (itime/3600)* 3600 
        dbg_log('itime=' + str(itime))
        dbg_log('rtime=' + str(rtime))
        if itime != rtime:
            stime = str(itime - rtime)
        else:
            stime = ''
        dbg_log('stime=' + str(stime))
        sPlayList   = xbmc.PlayList(xbmc.PLAYLIST_VIDEO) 
        sPlayer     = xbmc.Player()
        sPlayList.clear()
        #http://37.221.160.211:8080/archive/a2.stream.rec/1353808800.mp4?start=0
        for hdelta in range(6):
            furl  = 'http://' + rtmp_str + ':8080/archive/a' + rtmp_ch + '.stream.rec/' + str(rtime + hdelta * 3600) + '.mp4'
#            furl += ' swfUrl=' + SWFObject
#            furl += ' pageUrl=' + url
#            furl += ' tcUrl=rtmp://' + rtmp_str + ':8080/archive'
            if stime != '' and hdelta == 0 :
                furl += '?start=' + stime

            item = xbmcgui.ListItem(path = furl)
            sPlayList.add(furl, item, hdelta)
            if hdelta == 0: item0 = item
            dbg_log('furl = %s'%furl)

        xbmcplugin.setResolvedUrl(pluginhandle, True, item0) 

    sPlayer.play(sPlayList)

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





if mode == 'PLAY': DTV_play(url, name, thumbnail, plot)
elif mode == 'PLAR': DTV_plarch(url, name, thumbnail, plot)
elif mode == 'PRLS': DTV_online(DTV_url, mode)
elif mode == 'CHLS': DTV_online(DTV_url, mode)
elif mode == 'DTLS': DTV_dates(url, thumbnail)
elif mode == 'ARLS': DTV_archs(url, thumbnail)
elif mode == None: DTV_start()

dbg_log('CLOSE:')

