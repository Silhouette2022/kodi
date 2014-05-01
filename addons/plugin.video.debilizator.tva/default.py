# -*- coding: utf-8 -*-
#!/usr/bin/python
# Writer (c) 2012, Silhouette, E-mail: silhouette2022@gmail.com
# Rev. 0.7.6



import urllib,urllib2,re,sys,os,time
import xbmcplugin,xbmcgui,xbmcaddon

pluginhandle = int(sys.argv[1])
__addon__       = xbmcaddon.Addon(id='plugin.video.debilizator.tva') 
#fanart    = xbmc.translatePath( __addon__.getAddonInfo('path') + 'fanart.jpg')
#xbmcplugin.setPluginFanart(pluginhandle, fanart)

DTV_url = 'http://www.debilizator.tv'

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
        xbmcplugin.setContent(int(sys.argv[1]), 'episodes')#movies episodes tvshows
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
        print 'DTVA - except1'
        xbmcplugin.endOfDirectory(pluginhandle)
        return
    oneline = re.sub( '\n', ' ', http)
    #print oneline
    chndls = re.compile('div class="halfblock"> *?<a href="(.*?)/" title=(.*?)</div> *?</div>').findall(oneline)
    #print chndls
    for chndel in chndls:
        #print chndel
        chells = re.compile('<img class="chlogo" src="(.*?)" alt="(.*?)" title="(.*?)" />').findall(chndel[1])
        #print chells
        title = chells[0][1]
        if prls == 'PRLS':
            is_folder = False
        else:
            is_folder = True
        description = ''
        thumbnail = chells[0][0].replace('/mini', '')
        if prls == 'PRLS':
            uri = sys.argv[0] + '?mode=PLAY'
        else:
            uri = sys.argv[0] + '?mode=DTLS'
        uri += '&url='+urllib.quote_plus(url + chndel[0])
        uri += '&name='+urllib.quote_plus(title)
        #uri += '&plot='+urllib.quote_plus(description)
        uri += '&thumbnail='+urllib.quote_plus(thumbnail)

        ptls = re.compile('<div class="prtime">(.*?)</div> *?<div class="prdesc" title=".*?">(.*?)</div>').findall(chndel[1])
        #print ptls
        ptlsln = len(ptls)

        if prls == 'PRLS':
            i = 1
            while ptlsln - i + 1:
                prtm = ptls[ptlsln - i][0]
                prds = ptls[ptlsln - i][1]
                #prxt = ptls[ptlsln - i][2]
                prxt = ''

                prtmst = time.strptime(msktmls[0][1] + ' ' + prtm, "%Y-%d-%m %H:%M")
                
                try:
                    nprtm = toLcTm(tzdf, prtmst)
                except:
                    nprtm = prtm
                i += 1
                description = "[B][COLOR FF0084FF]" + nprtm + "[/COLOR] [COLOR FFFFFFFF]" + prds + "[/COLOR][/B][COLOR FF999999]" + chr(10) + prxt + "[/COLOR]" + chr(10) + description
                    
        if ptlsln == 0: ptlsln = 1
        description = re.sub( '&quot;','\"',re.sub( '\(\.\.\.\)', '', description))
        if ptlsln:
            dbg_log(title)
            item=xbmcgui.ListItem(title, iconImage=thumbnail, thumbnailImage=thumbnail)
            item.setInfo( type='video', infoLabels={'title': title, 'plot': description})
            if prls == 'PRLS':
                item.setProperty('IsPlayable', 'true')
            #item.setProperty('fanart_image',thumbnail)
            xbmcplugin.addDirectoryItem(pluginhandle,uri,item,is_folder)
            dbg_log(uri)
    xbmcplugin.endOfDirectory(pluginhandle)

def DTV_play(url, name, thumbnail):
    dbg_log('-DTV_play')
    import os
    
    response = getURL(url, save_cookie = True)
    mycookie = re.search('<cookie>(.+?)</cookie>', response).group(1)
    ref = re.search("swfobject.embedSWF\('(.+?)',", response).group(1)
    response = getURL(DTV_url + '/crossdomain.xml', cookie = mycookie, referrer = ref)

    if True:
        response = getURL(DTV_url + '/config/', cookie = mycookie, referrer = ref)
        streamer_ls   = re.compile('<src>(.*?).m3u8</src>').findall(response)
    else:
        response = getURL(DTV_url + '/maclist/', cookie = mycookie, referrer = ref)
        streamer_ls   = re.compile('mvideo.src="(.*?).m3u8').findall(response)
        
#    if len(streamer_ls):
#        file_ls   = re.compile('(.*?)playlist').findall(streamer_ls[0])
#        if len(file_ls):
#            eurl = '|Referer=' + urllib.quote_plus(ref)
#            eurl += '&User-Agent=' + urllib.quote_plus('Opera/9.80')
#            furl = streamer_ls[0] + '.m3u8' #+ eurl
#            response = getURL(furl, cookie = mycookie, referrer = ref)
#            print response
#            gf = open('got.m3u8', 'w')
#            gf.write(response)
#            gf.close()
            
#            gf = open('got.m3u8', 'r')
#            lf = open('live.m3u8', 'w')
#            for line in gf:
#                if line!='' and line[0]!='#':
#                    lf.write(file_ls[0] + line[:-2] + eurl + '\n\n')
#                else:
#                    lf.write(line)
                    
#            gf.close()
#            lf.close()
                    
                
            
#            item = xbmcgui.ListItem(path = 'live.m3u8')
#            item.setProperty('mimetype', 'video/mpg')
#            xbmcplugin.setResolvedUrl(pluginhandle, True, item)
#            return

    if len(streamer_ls):
        file_ls   = re.compile('(.*?)playlist').findall(streamer_ls[0])
        if len(file_ls):
            furl = streamer_ls[0] + '.m3u8'
            response = getURL(furl, cookie = mycookie, referrer = ref)
            print response

            sPlayList   = xbmc.PlayList(xbmc.PLAYLIST_VIDEO) 
            sPlayer     = xbmc.Player()
            sPlayList.clear()
            
            ts_ls   = re.compile('(.*?).ts').findall(response)

            eurl = '|Referer=' + urllib.quote_plus(ref)
            eurl += '&User-Agent=' + urllib.quote_plus('Opera/9.80')

            i = 0
            for ts in ts_ls:
                furl = file_ls[0] + ts + '.ts'
                furl += eurl
                xbmc.log('furl = %s'%furl)
                item = xbmcgui.ListItem(path = furl)
                sPlayList.add(furl, item, i)
                i = i + 1

                
            sPlayer.play(sPlayList)



def DTV_dates(url, thumbnail):
    dbg_log('-DTV_dates')

    item = xbmcgui.ListItem('Today', iconImage=thumbnail, thumbnailImage=thumbnail)
    uri = sys.argv[0] + '?mode=ARLS'
    uri += '&url='+urllib.quote_plus(url)
    uri += '&thumbnail='+urllib.quote_plus(thumbnail)
    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
            
    http = getURL(url, save_cookie = True, referrer = DTV_url)
    mycookie = re.search('<cookie>(.+?)</cookie>', http).group(1)
    #print http
    dtls = re.compile('<td style="(.*?)"><a href="(.*?)">(.*?)</a></td>').findall(http)
    print dtls
    if len(dtls):
        for style, href, descr in dtls:
            item = xbmcgui.ListItem(descr, iconImage=thumbnail, thumbnailImage=thumbnail)
            uri = sys.argv[0] + '?mode=ARLS'
            uri += '&url='+urllib.quote_plus(DTV_url + href)
            uri += '&name='+urllib.quote_plus(url)
            uri += '&thumbnail='+urllib.quote_plus(thumbnail)
            uri += '&cook='+urllib.quote_plus(mycookie)
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  

    xbmcplugin.endOfDirectory(pluginhandle)
    
    

def DTV_archs(url, name2, thumbnail, mycook):
    dbg_log('DTV_archs')
    http = getURL(url, save_cookie = True, cookie = mycook, referrer = url)
    mycookie = re.search('<cookie>(.+?)</cookie>', http).group(1)
    
    oneline = re.sub( '\n', ' ', http)
#    print oneline

    dtls = re.compile('<a class="prdescfull"  title="(.*?)" href="(.*?)">(.*?)</a>').findall(oneline)
    print dtls
    if len(dtls):
        for plot1, src, descr in dtls:
            name=descr.replace('&quot;', '\"').replace('  ',' ')
            plot=plot1.replace('&quot;', '\"').replace('  ',' ')
            item = xbmcgui.ListItem(name, iconImage=thumbnail, thumbnailImage=thumbnail)
            uri = sys.argv[0] + '?mode=PLAR'
            uri += '&url='+urllib.quote_plus(DTV_url + src)
            uri += '&name='+urllib.quote_plus(name2)
            uri += '&cook='+urllib.quote_plus(mycookie)
            item.setInfo( type='video', infoLabels={'title': name, 'plot': plot})
            item.setProperty('IsPlayable', 'true')
            #item.setProperty('fanart_image',thumbnail)
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item)
            dbg_log('uri:' + uri + '\n')  


    xbmcplugin.endOfDirectory(pluginhandle)    

def DTV_plarch(url, name, mycook):

    if True:
        DTV_plarch1(url, name, mycook)
    elif False:
        DTV_plarch2(url, name, mycook)
    else:
        DTV_plarch3(url, name, mycook)
        
def DTV_plarch1(url, name, mycook):
    
    response = getURL(url, save_cookie = True, cookie = mycook)
    mycookie = re.search('<cookie>(.+?)</cookie>', response).group(1)
    ref = re.search("swfobject.embedSWF\('(.+?)',", response).group(1)
    response = getURL(DTV_url + '/crossdomain.xml', cookie = mycookie, referrer = ref)

    response = getURL(DTV_url + '/config/', cookie = mycookie, referrer = ref)
    streamer_ls   = re.compile('<src>(.*?).m3u8</src>').findall(response)
    print streamer_ls
    if len(streamer_ls):
        file_ls   = re.compile('(.*?)playlist').findall(streamer_ls[0])
        print file_ls
        if len(file_ls):
            furl = streamer_ls[0] + '.m3u8'
            response = getURL(furl, cookie = mycookie, referrer = ref)
            print response
            sPlayList   = xbmc.PlayList(xbmc.PLAYLIST_VIDEO) 
            sPlayer     = xbmc.Player()
            sPlayList.clear()
            
            ts_ls   = re.compile('(.*?).ts').findall(response)
            print ts_ls
            eurl = '|Referer=' + urllib.quote_plus(ref)
#            eurl += '&User-Agent=' + urllib.quote_plus('Opera/9.80 (Windows NT 6.1; WOW64; Edition United Kingdom Local) Presto/2.12.388 Version/12.15')
            eurl += '&User-Agent=' + urllib.quote_plus('Opera/9.80')

            i = 0
            for ts in ts_ls:
                furl = file_ls[0] + ts + '.ts'
                furl += eurl
                xbmc.log('furl = %s'%furl)
                item = xbmcgui.ListItem(path = furl)
                if i==0:
                    xbmcplugin.setResolvedUrl(pluginhandle, True, item)
                sPlayList.add(furl, item, i)
                i = i + 1

                
            sPlayer.play(sPlayList)
            
                
def DTV_plarch2(url, name, mycook):
    
    response = getURL(url, save_cookie = True, cookie = mycook)
    mycookie = re.search('<cookie>(.+?)</cookie>', response).group(1)
    ref = re.search("swfobject.embedSWF\('(.+?)',", response).group(1)

    response = getURL(DTV_url + '/crossdomain.xml', cookie = mycookie, referrer = ref)
    response = getURL(DTV_url + '/config/', cookie = mycookie, referrer = ref)
    streamer_ls   = re.compile('<src>(.*?).m3u8</src>').findall(response)

    if len(streamer_ls):
        file_ls   = re.compile('(.*?)playlist').findall(streamer_ls[0])
        if len(file_ls):
            furl = streamer_ls[0] + '.m3u8'
            response = getURL(furl, cookie = mycookie, referrer = ref)

            ts_ls   = re.compile('(.*?).ts').findall(response)

            #stack://http://video1 , http://video2

            eurl = '|Referer=' + urllib.quote_plus(ref)
            eurl += '&User-Agent=' + urllib.quote_plus('Opera/9.80 (Windows NT 6.1; WOW64; Edition United Kingdom Local) Presto/2.12.388 Version/12.15')
            
            sPlayList   = xbmc.PlayList(xbmc.PLAYLIST_VIDEO) 
            sPlayer     = xbmc.Player()
            sPlayList.clear()
            
            furl = 'stack://'
            i = 0
            for ts in ts_ls:
                furl += file_ls[0] + ts + '.ts'
                furl += eurl + ' , '
                i += 1
#                if i > 5: break
            ffurl = furl[0:-3]    
            xbmc.log('ffurl = %s'%ffurl)
            item = xbmcgui.ListItem(path = ffurl)
            item.setProperty('mimetype', 'video/mpg')
            xbmcplugin.setResolvedUrl(pluginhandle, True, item)

def DTV_plarch3(url, name, mycook):
    
    response = getURL(url, save_cookie = True, cookie = mycook)
    mycookie = re.search('<cookie>(.+?)</cookie>', response).group(1)
    ref = re.search("swfobject.embedSWF\('(.+?)',", response).group(1)

    response = getURL(DTV_url + '/crossdomain.xml', cookie = mycookie, referrer = ref)
    response = getURL(DTV_url + '/config/', cookie = mycookie, referrer = ref)
    streamer_ls   = re.compile('<src>(.*?).m3u8</src>').findall(response)

    if len(streamer_ls):
        file_ls   = re.compile('(.*?)playlist').findall(streamer_ls[0])
        if len(file_ls):
            furl = streamer_ls[0] + '.m3u8'
            response = getURL(furl, cookie = mycookie, referrer = ref)

            ts_ls   = re.compile('(.*?).ts').findall(response)

            #stack://http://video1 , http://video2

            eurl = '|Referer=' + urllib.quote_plus(ref)
            eurl += '&User-Agent=' + urllib.quote_plus('Opera/9.80 (Windows NT 6.1; WOW64; Edition United Kingdom Local) Presto/2.12.388 Version/12.15')
            
            sPlayList   = xbmc.PlayList(xbmc.PLAYLIST_VIDEO) 
            sPlayer     = xbmc.Player()
            sPlayList.clear()
            
            i = 0
            j = 0
            splay=False
            for ts in ts_ls:
            
                print i
                if ((i%6) == 0):  
                    furl = 'stack://'
                furl += (file_ls[0] + ts + '.ts')
                furl += (\
                eurl + \
                ' , ')
                
                print 'furl = %s'%furl
                    
                if ((i+1)%6 == 0):  
#                if True:  
                    ffurl = furl[0:-3]       
                    xbmc.log('ffurl = %s'%ffurl)
                    item = xbmcgui.ListItem(path = ffurl)
                    item.setProperty('mimetype', 'video/mpg')
                    sPlayList.add(ffurl, item, j)

                    j += 1
                    break

                    
                i += 1

                
#            sPlayer.play(sPlayList)
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




if mode == 'PLAY': DTV_play(url, name, thumbnail)
elif mode == 'PLAR': DTV_plarch(url, name, cook)
elif mode == 'PRLS': DTV_online(DTV_url, mode)
elif mode == 'CHLS': DTV_online(DTV_url, mode)
elif mode == 'DTLS': DTV_dates(url, thumbnail)
elif mode == 'ARLS': DTV_archs(url, name, thumbnail, cook)
elif mode == None: DTV_start()

dbg_log('CLOSE:')

