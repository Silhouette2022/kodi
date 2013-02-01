# -*- coding: utf-8 -*-
#!/usr/bin/python
# Writer (c) 2012, Silhouette, E-mail: SIlhouette2012@gmail.com
# Rev. 0.4.0



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

dbg = 1
def dbg_log(line):
  if dbg: xbmc.log(line)
  
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
    dbg_log('-KTV_prls:')
    dbg_log('url = %s'%url)
    
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
    dbg_log('-KTV_play:')
    dbg_log('url = %s'%url)
    plnk = re.sub('-online','',url)
    response    = getURL(plnk + '/player.jsx')
    
    ef_ls = re.compile('"file":"(.+?)"').findall(response)
    #print ef_ls
    if (len(ef_ls) < 2):
        return
    else:
        rtmp_file = Decode(ef_ls[1])
        dbg_log('rtmp_file = %s'%rtmp_file)
        st_ls =rtmp_file.split(' ')
        #print st_ls
        if len(st_ls):
            rtmp_streamer = st_ls[0]
            rtmp_file = rtmp_streamer
        else:
            return       
      
        if 0:
          rtmp_file   = re.compile('"file":"http://(.+?)/playlist').findall(response)[0]
          dbg_log(rtmp_file)
          st_ls = rtmp_file.split('/')
          if len(st_ls):
              rtmp_streamer = 'http://' + st_ls[0] + '/' + st_ls[1]
          else:
              return
        
        furl = rtmp_file
        furl += ' swfUrl=%s'%(KTV_url + '/uppod.swf')
        furl += ' pageUrl=%s'%KTV_url
        furl += ' tcUrl=%s'%rtmp_streamer
        furl += ' flashVer=\'WIN 11,2,202,235\''
        
      
    
        dbg_log(furl)

        xbmc.log('furl = %s'%furl)
        item = xbmcgui.ListItem(path = furl)
        xbmcplugin.setResolvedUrl(pluginhandle, True, item)
             
        
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
                uri += '&url='+urllib.quote_plus(KTV_url + KTV_arch + furl + '/' + descr)
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
    
    

def KTV_guide(furl, thumbnail):
    dbg_log('-KTV_guide:')
    dbg_log('furl = %s'%furl)
    dbg_log('thumbnail = %s'%thumbnail)
        
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
                uri += '&url='+urllib.quote_plus(furl + '/' + href)
                item.setInfo( type='video', infoLabels={'title': name, 'plot': descr})
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(pluginhandle, uri, item)
                dbg_log(uri)
                i += 1

    xbmcplugin.endOfDirectory(pluginhandle)    
    
def KTV_plarch(url, name, thumbnail, plot):

    http = getURL(url)
    oneline = re.sub('[\r\n]', '', http)

    #"file":"1UDV5RIzJvoTXb6TORwgXxoQJ=oVX2NeOZwb9=07WSa=WR7tJx3QOx3kOREv9Sat9eLewiFtXZ0tOfoz5f0bse7BJZkhyeFdJvoYXxozXxozXx3zXRAkXRHgWeTi"
    fl_ls = re.compile('"file":"(.+?)"').findall(oneline)
    #print fl_ls
    #print Decode(fl_ls[0]).encode('utf8')
    
    if len(fl_ls):
        furl = Decode(fl_ls[0])
        xbmc.log('furl = %s'%furl)
        item = xbmcgui.ListItem(path = furl)
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
dyear=''

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




if mode == 'PLAR': KTV_plarch(url, name, thumbnail, plot)
elif mode == 'PLAY': KTV_play(url, name, thumbnail, plot)
elif mode == 'PRLS': KTV_prls(KTV_url)
elif mode == 'CHLS': KTV_chls(KTV_url + KTV_arch)
elif mode == 'DTLS': KTV_dates(url, thumbnail, dyear)
elif mode == 'GDLS': KTV_guide(url, thumbnail)
elif mode == None: KTV_start()

dbg_log('CLOSE:')

