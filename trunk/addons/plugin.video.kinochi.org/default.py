# -*- coding: utf-8 -*-
#!/usr/bin/python
# Writer (c) 2012, Silhouette, E-mail: otaranda@hotmail.com
# Rev. 0.3.0

import urllib,urllib2,re,sys,os,time
import xbmcplugin,xbmcgui,xbmcaddon
import json

pluginhandle = int(sys.argv[1])
__addon__       = xbmcaddon.Addon(id='plugin.video.inetcom.tv') 
#fanart    = xbmc.translatePath( __addon__.getAddonInfo('path') + 'fanart.jpg')
#xbmcplugin.setPluginFanart(pluginhandle, fanart)

KNO_url = 'http://kinochi.org'
KNO_fmtk = '/modules/filmoteka/'
KNO_pic1 = '/data/pic/id'
KNO_pic2 = '/t.jpg'
KNO_view = '/modules/view/'

AFID = '&f='
APAGE = '&page='
FIND_all = '7fffff'

ACT = 'act='
ACT_get = ACT + 'get'
ACT_lnk = ACT + 'getlink'

AHASH = '&hash[]='
HASH_fmtk = AHASH + 'filmoteka'
HASH_view = AHASH + 'view'
HASH_flv = HASH_view + AHASH
HASH_find = AHASH + FIND_all + AHASH

AGETPAGE = ACT_get + APAGE
AGETLINK = ACT_lnk + AFID
AGETVIEW = ACT_get + HASH_view + AHASH

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

def addVLDItem(title, uri, folder = True, icon = None, thumbn = None, info = None):
    dbg_log('-addVLDItem')
    dbg_log('- title:'+  title + '\n')
    dbg_log('- uri:'+  uri + '\n')
    dbg_log('- folder:'+  str(folder) + '\n')
    dbg_log('- icon:'+  str(icon) + '\n')
    dbg_log('- thumbn:'+  str(thumbn) + '\n')
    dbg_log('- info:'+  str(info) + '\n')
    
    item = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=thumbn)
    item.setInfo( type='video', infoLabels={'title': title, 'plot': info})
    if folder == False:
        item.setProperty('IsPlayable', 'true')
    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, folder)


def KNO_start(page, sfind, fval, cook):
    
    dbg_log('-KNO_start')

    if page == '0':
        http = get_url(KNO_url)
        
    ext_ls = [('<ФИЛЬТР>', '?mode=filt'),
              ('<ПОИСК>', '?mode=find')]
   
#    if page == "0" and sfind == "":
    for ctTitle, ctMode  in ext_ls:
        item = xbmcgui.ListItem(ctTitle)
        uri = sys.argv[0] + ctMode + '&fval=' + urllib.quote_plus(fval) + '&cook=' + urllib.quote_plus(cook)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
        dbg_log('- uri:'+  uri + '\n')
        
        
    if sfind == "":
        hpost = AGETPAGE + page + HASH_fmtk + AHASH + fval
    else:
        hpost = AGETPAGE + page + HASH_fmtk + AHASH + fval + AHASH + sfind
    dbg_log('- hpost:'+  hpost + '\n')
    http = get_url(KNO_url + KNO_fmtk, data = hpost, referrer = KNO_url)

    jdata = json.loads(http)

    i = 0
    for it in jdata:
      if it == 'list':
          for ent in jdata[it]:
              if ent[u'access'] == 'free':
                  name = re.sub('&nbsp;', ' ', ent[u'title'])
                  name = re.sub('</span>', ' ', name)
                  name = re.sub('<span style="white-space: nowrap">', ' ', name)
                  id = ent[u'id']
                  logo = KNO_url + KNO_pic1 + id + KNO_pic2
                  
                  info_ls = re.compile('\\"about\\":\\"(.+?)\\"').findall(ent[u'info'])
                  if len(info_ls):
                      info = info_ls[0]
                  else:
                      info = name
                  
                  
                  dbg_log(id)
                  #dbg_log(name.encode('utf8'))
                  #dbg_log(info.encode('utf8'))
                  #dbg_log(logo)
                  
                  item = xbmcgui.ListItem(name, iconImage=logo, thumbnailImage=logo)
                  item.setInfo( type='video', infoLabels={'title': name, 'plot': info})
                  uri = sys.argv[0] + '?mode=list'
                  uri += '&id='+id + '&page='+page
                  xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
                  dbg_log('- uri:'+  uri + '\n')
                  i = i + 1
                  
    if i:
        item = xbmcgui.ListItem('<NEXT PAGE>')
        uri = sys.argv[0] + '?page=' + str(int(page) + 1) + '&sfind=' + urllib.quote_plus(sfind) + '&fval=' + urllib.quote_plus(fval)#+ '&cook=' + urllib.quote_plus(cook)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
        dbg_log('- uri:'+  uri + '\n')
        item = xbmcgui.ListItem('<NEXT PAGE +10>')
        uri = sys.argv[0] + '?page=' + str(int(page) + 10) + '&sfind=' + urllib.quote_plus(sfind) + '&fval=' + urllib.quote_plus(fval) #+ '&cook=' + urllib.quote_plus(cook)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
        dbg_log('- uri:'+  uri + '\n')  

    xbmcplugin.endOfDirectory(pluginhandle)
  



def KNO_list(id, cook):
    dbg_log('-KNO_list')
    
    hpost = AGETVIEW + id
    dbg_log('- hpost:'+  hpost + '\n')
    http = get_url(KNO_url + KNO_view, data = hpost, referrer = KNO_url)
    #print http
    jd = json.loads(http)

    try:
        if jd['playlist'] != "": pl = 1
    except: pl = 0
    
    logo = KNO_url + KNO_pic1 + id + KNO_pic2
    if pl == 0:
        name = jd['title']
        info_ls = re.compile('\\"about\\":\\"(.+?)\\"').findall(jd['info'])
        if len(info_ls):
            info = info_ls[0]
        else:
            info = name

        item = xbmcgui.ListItem(name, iconImage=logo, thumbnailImage=logo)
        item.setInfo( type='video', infoLabels={'title': name, 'plot': info})
        uri = sys.argv[0] + '?mode=play'
        uri += '&id=' + urllib.quote_plus(id) + '&fid=' + urllib.quote_plus('id' + id + '.flv')
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item)
        dbg_log('- uri:'+  uri + '\n')
    else:
        lnks_ls = re.compile('{\\"url\\":\\"(.+?)\\", \\"pic\\":\\"(.+?)\\", \\"title\\":\\"(.+?)\\"}').findall(jd['playlist'])
        if len(lnks_ls):
            for url,pic,title in lnks_ls:
                name = title
                item = xbmcgui.ListItem(name, iconImage=logo, thumbnailImage=logo)
                item.setInfo( type='video', infoLabels={'title': name, 'plot': name})
                uri = sys.argv[0] + '?mode=play'
                uri += '&id=' + urllib.quote_plus(id) + '&fid=' + urllib.quote_plus(url)
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(pluginhandle, uri, item)
                dbg_log('- uri:'+  uri + '\n')
        

    xbmcplugin.endOfDirectory(pluginhandle)


def KNO_find(page, fval, cook):     
    dbg_log('-KNO_find:'+ '\n')
    dbg_log('- page:'+  page + '\n')      
    
    kbd = xbmc.Keyboard()
    kbd.setHeading('ПОИСК')
    kbd.doModal()
    if kbd.isConfirmed():
        stxt = kbd.getText()
        dbg_log('- stxt:'+  stxt + '\n')
        KNO_start('0', stxt, fval, cook)

def KNO_filt(fval):
    dbg_log('-KNO_filt:'+ '\n')
    dbg_log('- filt:'+ fval + '\n') 
    
    genre_ls = [('КОМЕДИЯ', 2097152),
                ('ПРИКЛЮЧЕНИЯ', 1048576),
                ('ФАНТАСТИКА', 524288),
                ('ИСТОРИЯ', 262144),
                ('БОЕВИК', 131072),
                ('ДЕТЕКТИВ', 65536),
                ('УЖАСЫ', 32768),
                ('ДРАМА', 16384),
                ('ТРИЛЛЕР', 8192),
                ('НАШЕ КИНО', 4096),
                ('МУЛЬТФИЛЬМ', 2048),
                ('СПОРТ', 1024),
                ('ДОКУМЕНТАЛЬНОЕ', 512),
                ('КРИМИНАЛ', 256),
                ('ФЕНТЕЗИ', 128),
                ('ВЕСТЕРН', 64)]
                
    film_ls = [('ФИЛЬМ', 16),
                ('СЕРИАЛ', 32)]
#                ('CamRip', 8),
#                ('TeleSync', 4),
#                ('DVD Screener', 2),
#                ('DVD Rip', 1)]
                
#    for fTitle, eVal  in genre_ls:
#        if int(fval,16) & eVal:
#            entry = "[COLOR FF00FF00]" + fTitle + "[/COLOR]"
#            nval = hex(int(fval,16) ^ eVal)
#        else:
#            entry = "[COLOR FFFF0000]" + fTitle + "[/COLOR]"
#            nval = hex(int(fval,16) | eVal)

    if fval == FIND_all:
        list_ls = film_ls
    else:
        list_ls = genre_ls

    for fTitle, eVal  in list_ls:
        if fval == FIND_all:
            nval = hex(int(fval,16) ^ eVal) 
        else:
            nval = hex((int(fval,16) & int('3f',16)) | eVal | 4194304)

        entry = fTitle
        item = xbmcgui.ListItem(entry)
        uri = sys.argv[0] + '?fval=' + urllib.quote_plus(nval)
            
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
        dbg_log('- uri:'+  uri + '\n')
    
    xbmcplugin.endOfDirectory(pluginhandle)

def KNO_play(id, fid):
    dbg_log('-KNO_play')

    hpost = AGETLINK + fid + HASH_flv + id
    dbg_log(hpost)
    http = get_url(KNO_url + KNO_view, data = hpost, referrer = KNO_url)
    jdf = json.loads(http)

    vlink = KNO_url + jdf['url']
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
page='0'
id=''
fid=''
name=''
cook=''
sfind=''
fval=FIND_all
mode=None

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
    page=params['page']
    dbg_log('-PAGE:'+ page + '\n')
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
    fid=urllib.unquote_plus(params['fid'])
    dbg_log('-FID:'+ fid + '\n')
except: pass
try:
    name=urllib.unquote_plus(params['name'])
    dbg_log('-NAME:'+ name + '\n')
except: pass
try:
    sfind=urllib.unquote_plus(params['sfind'])
    dbg_log('-SFIND:'+ sfind + '\n')
except: pass
try:
    fval=urllib.unquote_plus(params['fval'])
    dbg_log('-FVAL:'+ fval + '\n')
except: pass

if mode == None: KNO_start(page, sfind, fval, cook)
elif mode == 'play': KNO_play(id, fid)
elif mode == 'list': KNO_list(id, cook)
elif mode == 'find': KNO_find(page, fval, cook)
elif mode == 'filt': KNO_filt(fval)

dbg_log('CLOSE:')

