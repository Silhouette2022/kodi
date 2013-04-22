# -*- coding: utf-8 -*-
#!/usr/bin/python
# Writer (c) 2012, Silhouette, E-mail: SIlhouette2012@gmail.com
# Rev. 0.4.8



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


logos = {'pervii-kanal':'pervyi_kanal',
            'rossiya-1':'rossiia_1',
            'ntv':'ntv',
            'sts':'sts',
            'rossiya-2':'rossiia_2',
            'perec':'perets',
            'rossiya-k':'rossiia_k',
            'ren':'ren_tv',
            'rossiya-24':'rossiia_24',
            'karusel':'karusel',
            '5kanal':'piatyi_kanal',
            'tv5kanal':'piatyi_kanal',
            'disney':'disney_channel',
            'domashnii':'domashnii',
            'tvc': 'tvts',
            'zvezda': 'zvezda',
            'u': 'iu-tv',
            'tnt': 'tnt',
            'tv3': 'tv-3',
            'mtv': 'mtv-russia'}
    
      
def Decode(param):
        hash1 = ("3", "U", "I", "a", "V", "x", "s", "8", "z", "2", "7", "W", "w", "G", "B", "X", "b", "9", "4", "R", "k", "J", "e", "5", "g", "=")
        hash2 = ("Q", "H", "o", "1", "0", "T", "d", "n", "v", "i", "l", "Z", "Y", "f", "p", "M", "y", "N", "6", "D", "t", "L", "m", "c", "u", "j")


        try:
            #-- define variables
            loc_3 = [0,0,0,0]
            loc_4 = [0,0,0]
            loc_2 = ''

            #-- define hash parameters for decoding
            dec = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='

            #-- decode
            for i in range(0, len(hash1)):
                re1 = hash1[i]
                re2 = hash2[i]

                param = param.replace(re1, '___')
                param = param.replace(re2, re1)
                param = param.replace('___', re2)

            i = 0
            while i < len(param):
                j = 0
                while j < 4 and i+j < len(param):
                    loc_3[j] = dec.find(param[i+j])
                    j = j + 1

                loc_4[0] = (loc_3[0] << 2) + ((loc_3[1] & 48) >> 4);
                loc_4[1] = ((loc_3[1] & 15) << 4) + ((loc_3[2] & 60) >> 2);
                loc_4[2] = ((loc_3[2] & 3) << 6) + loc_3[3];

                j = 0
                while j < 3:
                    if loc_3[j + 1] == 64:
                        break

                    loc_2 += unichr(loc_4[j])

                    j = j + 1

                i = i + 4;
        except:
            loc_2 = ''

        return loc_2

def getURL(url):
    dbg_log('getURL = %s'%url)
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
    try:
      import YaTv
      tvp=YaTv.GetPr()
      xbmcplugin.setContent(int(sys.argv[1]), 'episodes')#movies episodes tvshows
    except:
      pass
        
    
    
    dbg_log('-KTV_prls:')
    dbg_log('url = %s'%url)
    http = getURL(url)
    pr_ls = re.compile('<li><a class="(.+?)" href="(.+?)"><span>(.+?)</span></a></li>').findall(http)
    
    if len(pr_ls):
        for eng,href,descr in pr_ls:
            name = descr
            try:
                logo = xbmc.translatePath( __addon__.getAddonInfo('path') + '\\resources\\logos\\' + logos[eng] + '.png')
            except:
                logo = ''
            dbg_log(name)
            dbg_log(logo)
            try:
                name=descr.replace("Россия К","Культура").replace("Дисней","Канал Disney").replace("Перец","ПЕРЕЦ").replace("Рен ТВ","РЕН ТВ").replace("ТВЦ","ТВ Центр")
                descr = tvp[name]["plot"]
                tbn=tvp[name]["img"]
                item.setProperty('fanart_image', tbn)

            except:
                tbn = logo
            
            item = xbmcgui.ListItem(name, iconImage=logo, thumbnailImage=logo)
            uri = sys.argv[0] + '?mode=PLAY'
            uri += '&url='+urllib.quote_plus(url + href)
            item.setInfo( type='video', infoLabels={'title': name, 'plot': descr})
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item)

    xbmcplugin.endOfDirectory(pluginhandle)    
    
def KTV_play(url, name, thumbnail, plot):
    dbg_log('-KTV_play:')
    dbg_log('url = %s'%url)
    plnk = re.sub('-online','',url)
    
    try:
        response    = getURL(plnk + '/player.jsx')
    except:
        response    = getURL(url)
    
    ef_ls = re.compile('"file":"(.+?)"').findall(response)
    #print ef_ls
    if len(ef_ls):
        url_ls = re.compile('rtmp:(.+?).stream').findall(Decode(ef_ls[0]))
        if len(url_ls):
            i = 0
        for ur in url_ls:
            hurl = 'http:' + url_ls[i] + '.stream'
            dbg_log('hrl = %s'%hurl)
            try:            
              http = urllib2.urlopen(hurl, None, 5)
            except:
              i += 1
              dbg_log('--not playing')
              continue
            
            rtmp_streamer = re.sub('http','rtmp',hurl)
            furl = rtmp_streamer
            furl += ' swfUrl=%s'%(KTV_url + '/uppod.swf')
            furl += ' pageUrl=%s'%KTV_url
            furl += ' tcUrl=%s'%rtmp_streamer
            furl += ' flashVer=\'WIN 11,2,202,235\''
            
            xbmc.log('furl = %s'%furl)
            
            item = xbmcgui.ListItem(path = furl)
            xbmcplugin.setResolvedUrl(pluginhandle, True, item)

            dbg_log('--playing') 

        
def KTV_chls(url):
    dbg_log('-KTV_chls:')
    dbg_log('url = %s'%url)

    try:
        http = getURL(url)
    except:
        xbmcplugin.endOfDirectory(pluginhandle)
        return

    http = getURL(url)
    ch_ls = re.compile('href="' + KTV_arch +'(.+?)"><span><b>(.+?)</b>').findall(http)
    #print ch_ls
    for arlnk, description in ch_ls:
        title = description
        is_folder = True
        try:
            thumbnail = xbmc.translatePath( __addon__.getAddonInfo('path') + '\\resources\\logos\\' + logos[arlnk[1:]] + '.png')
        except:
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

def KTV_dates(furl, thumbnail, dyear):
    dbg_log('-KTV_dates:')
    dbg_log('furl = %s'%furl)
    dbg_log('thumbnail = %s'%thumbnail)
    
    url = re.sub('~','-',furl)
    http = getURL(KTV_url + KTV_arch + url + dyear)
    oneline = re.sub('[\r\n]', '', http)
    dt_ls = re.compile('<a href="' + KTV_arch + url + '/([A-Za-z0-9/_-]+?)">\s+?<span>').findall(oneline)
    pr_ls = re.compile('<a href="' + KTV_arch + url + '/([0-9]+?)">\s+?<img src="/images/arrow_left.gif"/>').findall(oneline)
    if len(dt_ls):
        http = getURL(KTV_time)
        cdate = re.compile('"date":"(.+?)"').findall(http)[0]
        for i in range(len(dt_ls) - 1, -1, -1):
            #print i
            descr = dt_ls[i]
            dbg_log(descr)
            if descr <= cdate:
                item = xbmcgui.ListItem(descr, iconImage=thumbnail, thumbnailImage=thumbnail)
                uri = sys.argv[0] + '?mode=GDLS'
                #uri += '&url='+urllib.quote_plus(KTV_url + KTV_arch + furl)
                uri += '&url='+urllib.quote_plus(url)
                uri += '&cdate='+urllib.quote_plus(descr)
                uri += '&thumbnail='+urllib.quote_plus(thumbnail)
                xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
                
    if len(pr_ls):
        uri = sys.argv[0] + '?mode=DTLS'
        uri += '&url='+urllib.quote_plus(url)
        uri += '&dyear='+urllib.quote_plus('/' + pr_ls[0])
        uri += '&thumbnail='+urllib.quote_plus(thumbnail)
        item=xbmcgui.ListItem(pr_ls[0], iconImage=thumbnail, thumbnailImage=thumbnail)
        xbmcplugin.addDirectoryItem(pluginhandle,uri,item,True)

    xbmcplugin.endOfDirectory(pluginhandle)
    
    

def KTV_guide(furl, thumbnail, cdate):
    dbg_log('-KTV_guide:')
    dbg_log('furl = %s'%furl)
    dbg_log('thumbnail = %s'%thumbnail)
    dbg_log('cdate = %s'%cdate)
        
    url = re.sub('~','-',furl)
    http = getURL(KTV_url + KTV_arch + url + '/' + cdate)
    #print http
    oneline = re.sub('[\r\n]', '', http)
    tr_ls = re.compile('<tr align="top">(.+?)</tr>').findall(oneline)
    
    if len(tr_ls):
        tm_ls = []
        #surl = re.sub(KTV_url, '', url  + '/' + cdate)
        surl = KTV_arch  + url + '/' + cdate 
        dbg_log('surl = %s'%surl)
        for tr in tr_ls:
            tm_ls.append(re.search('<td valign="top">(.+?)</td>', tr).group(1))
            gd_ls = re.compile('<a href="' + surl + '/(.+?)">(.+?) +?</a>').findall(oneline)

        i = 0
        #print gd_ls
        if len(gd_ls):
            for href,descr in gd_ls:
                name=tm_ls[i] + '-' + re.sub('\&#034;' ,'\"', descr.strip())
                dbg_log(name)
                item = xbmcgui.ListItem(name, iconImage=thumbnail, thumbnailImage=thumbnail)
                uri = sys.argv[0] + '?mode=PLAR'
                uri += '&url='+urllib.quote_plus(KTV_url + KTV_arch + '/player' + url + '/' + href + '.jsx')
                item.setInfo( type='video', infoLabels={'title': name, 'plot': descr})
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(pluginhandle, uri, item)
                dbg_log(uri)
                i += 1

    xbmcplugin.endOfDirectory(pluginhandle)    
    
def KTV_plarch(url, name, thumbnail, plot):

    http = getURL(url)

    fl_ls = re.compile('"file":"(.+?)"').findall(http)
    #print fl_ls
    
    if len(fl_ls):
        url_ls = re.compile('http:(.+?).flv').findall(Decode(fl_ls[0]))
        if len(url_ls):
            i = 0
        for ur in url_ls:
            furl = 'http:' + url_ls[i] + '.flv'
            xbmc.log('furl = %s'%furl)
            try:            
              http = urllib2.urlopen(furl, None, 10)
            except:
              i += 1
              dbg_log('--not playing')
              continue

            item = xbmcgui.ListItem(path = furl)
            xbmcplugin.setResolvedUrl(pluginhandle, True, item)
            dbg_log('--playing') 
    
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
dyear=''
cdate=''
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
    dyear=urllib.unquote_plus(params['dyear'])
    dbg_log('-DYEAR:'+ dyear + '\n')
except: pass
try: 
    cdate=urllib.unquote_plus(params['cdate'])
    dbg_log('-CDATE:'+ cdate + '\n')
except: pass



if mode == 'PLAR': KTV_plarch(url, name, thumbnail, plot)
elif mode == 'PLAY': KTV_play(url, name, thumbnail, plot)
elif mode == 'PRLS': KTV_prls(KTV_url)
elif mode == 'CHLS': KTV_chls(KTV_url + KTV_arch)
elif mode == 'DTLS': KTV_dates(url, thumbnail, dyear)
elif mode == 'GDLS': KTV_guide(url, thumbnail, cdate)
elif mode == None: KTV_start()

dbg_log('CLOSE:')

