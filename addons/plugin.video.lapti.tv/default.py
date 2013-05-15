# -*- coding: utf-8 -*-
#!/usr/bin/python
# Writer (c) 2012, Silhouette, E-mail: SIlhouette2012@gmail.com
# Rev. 0.2.0



import urllib,urllib2,re,sys,os,time
import xbmcplugin,xbmcgui,xbmcaddon
from StringIO import StringIO
import gzip

pluginhandle = int(sys.argv[1])
__addon__       = xbmcaddon.Addon(id='plugin.video.lapti.tv') 
#fanart    = xbmc.translatePath( __addon__.getAddonInfo('path') + 'fanart.jpg')
#xbmcplugin.setPluginFanart(pluginhandle, fanart)

LTV_url = 'http://www.lapti.tv'
LTV_arch = '/archive'
LTV_time = 'http://www.lapti.tv/current-time'
#LTV_url_arch = LTV_url + LTV_arch

dbg = 0
def dbg_log(line):
  if dbg: xbmc.log(line)

def getMskTime():
    try:
      msktmht = getURL('http://time.jp-net.ru/');
      msktmls = re.compile('<h1 align=\'center\'>(.*?): (.*?)</h1>').findall(msktmht)
      msktmst = time.strptime(msktmls[0][1] + ' ' + msktmls[1][1], "%Y-%d-%m %H:%M:%S")
      mskitime = time.mktime(msktmst)
      return mskitime
    except:
      return 0

wds =  {0:'Пн',
        1:'Вт',
        2:'Ср',
        3:'Чт',
        4:'Пт',
        5:'Сб',
        6:'Вс'}
            
logos = {'onechanel':'pervyi_kanal',
            'rus1chanel':'rossiia_1',
            'ntvchanel':'ntv',
            'stschanel':'sts',
            'rus2chanel':'rossiia_2',
            'perec':'perets',
            'ruskchanel':'rossiia_k',
            'rentvchanel':'ren_tv',
            'rus24chanel':'rossiia_24',
            'karuselchanel':'karusel',
            'tv5chanel':'piatyi_kanal',
            'disneychanel':'disney_channel',
            'homechanel':'domashnii',
            'tvcentrchanel': 'tvts',
            'zvezda': 'zvezda',
            'uchanel': 'iu-tv',
            'tnt': 'tnt',
            'tv3chanel': 'tv-3',
            'mtvchanel': 'mtv-russia'}
            
chnames = {'onechanel':'Первыи_канал',
            'rus1chanel':'Россия_1',
            'ntvchanel':'НТВ',
            'stschanel':'СТС',
            'rus2chanel':'Россия_2',
            'perec':'Перец',
            'ruskchanel':'Россия_К',
            'rentvchanel':'РЕН_ТВ',
            'rus24chanel':'Россия_24',
            'karuselchanel':'Карусель',
            'tv5chanel':'5_Канал',
            'disneychanel':'Disney_Chanel',
            'homechanel':'Домашний',
            'tvcentrchanel': 'ТВЦ',
            'zvezda': 'Звезда',
            'uchanel': 'Ю_ТВ',
            'tnt': 'ТНТ',
            'tv3chanel': 'ТВ-3',
            'mtvchanel': 'МТВ'}
    
      
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

def ungzipResp(page):
    encoding = page.info().get("Content-Encoding")    
    content = page.read()
    if encoding in ('gzip', 'x-gzip', 'deflate'):
        if encoding == 'deflate':
            data = StringIO.StringIO(zlib.decompress(content))
        else:
            data = gzip.GzipFile('', 'rb', 9, StringIO.StringIO(content))
        content = data.read()

    return content
		
def getURL(url, data = None, cookie = None, save_cookie = False, referer = None, xReqW = None):
    #print url
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 5.1; rv:20.0) Gecko/20100101 Firefox/20.0')
    req.add_header('Accept', 'text/html, */*')
    req.add_header('Accept-Language', 'en-US,en')
    req.add_header('Accept-Encoding', 'gzip, deflate')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
    req.add_header("Connection", "Keep-Alive")
    if cookie: req.add_header('Cookie', cookie)
    if referer: req.add_header('Referer', referer)
    if xReqW: req.add_header('X-Requested-With', xReqW)
    if data: 
        response = urllib2.urlopen(req, data, timeout=30)
    else:
        response = urllib2.urlopen(req, timeout=30)
    link=response.read()
    if response.info().get('Content-Encoding') == 'gzip':
        buf = StringIO(link)
        f = gzip.GzipFile(fileobj=buf)
        link = f.read()    
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
    
def LTV_prls(url):
    dbg_log('-LTV_prls:')
    dbg_log('url = %s'%url)

    http = getURL(url)
    #print http
    pr_ls = re.compile('<li><a class="(.+?)" href="(.+?)"></a></li>').findall(http)
    #print pr_ls
    if len(pr_ls):
        repeat = ''
        for eng,href in pr_ls:
            if repeat == '': repeat = eng
            elif repeat == eng: break
              
            try:
                name = chnames[eng]
                descr = name
            except:
                name = eng
                descr = name
            try:
                logo = xbmc.translatePath( __addon__.getAddonInfo('path') + '\\resources\\logos\\' + logos[eng] + '.png')
            except:
                logo = ''
            dbg_log(name)
            dbg_log(logo)
            tbn = logo
            
            item = xbmcgui.ListItem(name, iconImage=logo, thumbnailImage=logo)
            uri = sys.argv[0] + '?mode=DTLS'
            uri += '&url='+urllib.quote_plus(url + href)
            uri += '&thumbnail='+urllib.quote_plus(logo)
            item.setInfo( type='video', infoLabels={'title': name, 'plot': descr})
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)


    xbmcplugin.endOfDirectory(pluginhandle)    
    
def LTV_play(url):
    dbg_log('-LTV_play:')
    dbg_log('url = %s'%url)

    rtmp_file = url
    st_ls =rtmp_file.split(' ')
    #print st_ls
    if len(st_ls):
        rtmp_streamer = st_ls[0]
        rtmp_file = rtmp_streamer
        
        furl = rtmp_file
        furl += ' swfUrl=%s'%(LTV_url + '/uppod.swf')
        furl += ' pageUrl=%s'%LTV_url
        furl += ' tcUrl=%s'%rtmp_streamer
        furl += ' flashVer=\'WIN 11,2,202,235\''

        dbg_log(furl)

        xbmc.log('furl = %s'%furl)
        item = xbmcgui.ListItem(path = furl)
        xbmcplugin.setResolvedUrl(pluginhandle, True, item)
             
def LTV_guideOLD(furl, thumbnail):
    dbg_log('-LTV_guide:')
    dbg_log('furl = %s'%furl)
        
    http = getURL(furl, save_cookie = True)
    try:
      mycookie = re.search('<cookie>(.+?)</cookie>', http).group(1)
    except:
      mycookie = ''

    
    ef_ls = re.compile('"file":"(.+?)"').findall(http)
    #print ef_ls
    if len(ef_ls):
        rtmp_file = Decode(ef_ls[0])
        name = '-Live-'
        descr = '-Live-'
        item = xbmcgui.ListItem(name, iconImage=thumbnail, thumbnailImage=thumbnail)
        uri = sys.argv[0] + '?mode=PLAY'
        uri += '&url='+urllib.quote_plus(rtmp_file)
        item.setInfo( type='video', infoLabels={'title': name, 'plot': descr})
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item)

    sys_ls = re.compile('<input type="hidden" name="sys" id="(.+?)" value="(.+?)">').findall(http)
    str_ls = re.compile('<input type="hidden" name="stream" id="(.+?)" value="(.+?)">').findall(http)
    
    cpos = 0
    if len(sys_ls) > 0 and len(str_ls) > 0:
        prog_ls = re.compile('<span id="prog(.+?)"><span class="now-top"></span><span class="now-middle"><span class="time" rel="(.+?)">(.+?)</span> <span class="tvname"><span class="name">(.+?)</span>').findall(http)
        hide_ls = re.compile("showhide\('prog(.+?)',(.+?),(.+?)\);").findall(http)
        if len(prog_ls) == len(hide_ls):
          #for prog,rel,stm,descr in prog_ls:
          for i in range(len(prog_ls) - 1, -1, -1):
              prog = prog_ls[i][0]
              rel = prog_ls[i][1]
              stm = prog_ls[i][2]
              descr = prog_ls[i][3]
              name=stm + '-' + descr
              if hide_ls[i][2] == '2':
                  name = '[COLOR FFFF0000]' + name + '[/COLOR]'
                  if cpos == 0: cpos = len(prog_ls) - i
              dbg_log(name)
              item = xbmcgui.ListItem(name, iconImage=thumbnail, thumbnailImage=thumbnail)
              uri = sys.argv[0] + '?mode=PLAR'
              
              #POST start=1366995600&timeng=undefined&chanel=http://www.lapti.tv/pervii-kanal-online.html&sys=1TV&stream=first              
              uri += '&url='+urllib.quote_plus(LTV_url + '/src/ajaxplayer.php')
              uri += '&pdata='+urllib.quote_plus('start=' + rel + '&timeng=1367263800&chanel=' + furl + '&sys=' + sys_ls[0][1] + '&stream=' + str_ls[0][1])
              uri += '&cookie='+urllib.quote_plus(mycookie)
              item.setInfo( type='video', infoLabels={'title': name, 'plot': descr})
              item.setProperty('IsPlayable', 'true')
              xbmcplugin.addDirectoryItem(pluginhandle, uri, item)
              dbg_log(uri)
              if i > 0 and cmp(stm, prog_ls[i - 1][2]) < 0:
                  item = xbmcgui.ListItem('<----------->')
                  uri = sys.argv[0] + '?mode=GDLS'
                  uri += '&url='+urllib.quote_plus(furl)
                  xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

    xbmcplugin.endOfDirectory(pluginhandle)
#    wnd = xbmcgui.Window(xbmcgui.getCurrentWindowId())
#    wnd.getControl(wnd.getFocusId()).selectItem(cpos)   

def LTV_guide(furl, thumbnail, pdata, pref, psys, pstream, mycookie):
    dbg_log('-LTV_guide:')
    dbg_log('furl = %s'%furl)
        
    http = getURL(LTV_url + '/src/ajax.php', 
                  data = 'nowdate=' + pdata + '&chanel=' + psys + '&sli=3&filter=', 
                  referer = furl, xReqW = 'XMLHttpRequest')

    prog_ls = re.compile('<span  id="prog(.+?)"><span class="now-top"></span><span class="now-middle"><span class="time" rel="(.+?)">(.+?)</span> <span class="tvname"><span class="name">(.+?)</span>').findall(http)
    
    if len(prog_ls):
      for prog, rel, stm, descr in prog_ls:
          name=stm + '-' + descr
          dbg_log(name)

          item = xbmcgui.ListItem(name, iconImage=thumbnail, thumbnailImage=thumbnail)
          uri = sys.argv[0] + '?mode=PLAR'
          
          #POST start=1366995600&timeng=undefined&chanel=http://www.lapti.tv/pervii-kanal-online.html&sys=1TV&stream=first              
          uri += '&url='+urllib.quote_plus(LTV_url + '/src/ajaxplayer.php')
          uri += '&pdata='+urllib.quote_plus('start=' + rel + '&timeng=' + rel + '&chanel=' + pref + '&sys=' + psys + '&stream=' + pstream)
          uri += '&cookie='+urllib.quote_plus(mycookie)
          item.setInfo( type='video', infoLabels={'title': name, 'plot': descr})
          item.setProperty('IsPlayable', 'true')
          xbmcplugin.addDirectoryItem(pluginhandle, uri, item)

    xbmcplugin.endOfDirectory(pluginhandle)


def LTV_dates(furl, thumbnail):
    dbg_log('-LTV_guide:')
    dbg_log('furl = %s'%furl)
    
        
    http = getURL(furl, save_cookie = True)
    try:
      mycookie = re.search('<cookie>(.+?)</cookie>', http).group(1)
    except:
      mycookie = ''

    ef_ls = re.compile('"file":"(.+?)"').findall(http)

    if len(ef_ls):
        rtmp_file = Decode(ef_ls[0])
        name = '-Live-'
        descr = '-Live-'
        item = xbmcgui.ListItem(name, iconImage=thumbnail, thumbnailImage=thumbnail)
        uri = sys.argv[0] + '?mode=PLAY'
        uri += '&url='+urllib.quote_plus(rtmp_file)
        item.setInfo( type='video', infoLabels={'title': name, 'plot': descr})
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item)

    sys_ls = re.compile('<input type="hidden" name="sys" id="(.+?)" value="(.+?)">').findall(http)
    date_ls = re.compile('<input type="hidden" name="prevdata" id="(.+?)" value="(.+?)">').findall(http)
    str_ls = re.compile('<input type="hidden" name="stream" id="(.+?)" value="(.+?)">').findall(http)
    
    cpos = 0
    if len(sys_ls) > 0 and len(date_ls) > 0 and len(str_ls) > 0:
    
#        try:
        iMsk = getMskTime()
        if iMsk:
                dthdr_ls = [(time.strftime("%Y-%m-%d",time.localtime(iMsk - i*3600*24)), 
                            ' ' + wds[time.localtime(iMsk - i*3600*24).tm_wday])  for i in range(20)]
#        except:
            #<span class="titleprogram">30 Апреля 2013 (<span class="nedeasy">Вт</span>)</span>
#            dttp = getURL(LTV_url + '/src/ajax.php', data = 'nowdate=' + date_ls[0][1] + '&chanel=' + sys_ls[0][1] + '&sli=4&filter=', referer = furl, xReqW = 'XMLHttpRequest')
#            dthdr_ls = re.compile('<span class="titleprogram">(.+?)\(<span class=".*?">(.+?)</span>\)</span>').findall(dttp)
        
        for dtname,week in dthdr_ls:
            item = xbmcgui.ListItem(dtname + week, iconImage=thumbnail, thumbnailImage=thumbnail)
            uri = sys.argv[0] + '?mode=GDLS'
            uri += '&url='+urllib.quote_plus(furl)
            uri += '&pdata='+urllib.quote_plus(dtname)
            uri += '&pref='+urllib.quote_plus(furl)
            uri += '&psys='+urllib.quote_plus(sys_ls[0][1])
            uri += '&name='+urllib.quote_plus(str_ls[0][1])
            uri += '&cookie='+urllib.quote_plus(mycookie)
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
    
    xbmcplugin.endOfDirectory(pluginhandle)        

    
def LTV_plarch(url, pdata, cook):

    http = getURL(url, data = pdata, cookie = cook, referer="http://www.lapti.tv/pervii-kanal-online.html", xReqW = 'XMLHttpRequest')

    #"file":"1UDV5RIzJvoTXb6TORwgXxoQJ=oVX2NeOZwb9=07WSa=WR7tJx3QOx3kOREv9Sat9eLewiFtXZ0tOfoz5f0bse7BJZkhyeFdJvoYXxozXxozXx3zXRAkXRHgWeTi"
    fl_ls = re.compile('"file":"(.+?)"').findall(http)
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
pdata=''
pref=''
psys=''
cookie=''
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
    pdata=urllib.unquote_plus(params['pdata'])
    dbg_log('-PDATA:'+ pdata + '\n')
except: pass
try: 
    pref=urllib.unquote_plus(params['pref'])
    dbg_log('-PREF:'+ pref + '\n')
except: pass
try: 
    psys=urllib.unquote_plus(params['psys'])
    dbg_log('-PSYS:'+ psys + '\n')
except: pass
try: 
    cookie=urllib.unquote_plus(params['cookie'])
    dbg_log('-COOKIE:'+ cookie + '\n')
except: pass


if mode == 'PLAR': LTV_plarch(url, pdata, cookie)
elif mode == 'PLAY': LTV_play(url)
elif mode == 'PRLS': LTV_prls(LTV_url)
elif mode == 'DTLS': LTV_dates(url, thumbnail)
elif mode == 'GDLS': LTV_guide(url, thumbnail, pdata, pref, psys, name, cookie)
elif mode == None: LTV_prls(LTV_url)

dbg_log('CLOSE:')

