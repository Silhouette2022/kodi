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

KNO_url = 'http://kinochi.org/'
KNO_fmtk = '/modules/filmoteka/'
KNO_pic1 = '/data/pic/id'
KNO_pic2 = '/t.jpg'
KNO_view = '/modules/view/'

ACT_get = 'act=get&page='
HASH_fmtk = '&hash[]=filmoteka'

HASH_view = 'act=get&hash[]=view&hash[]='

ACT_glnk = 'act=getlink&f='
HASH_flv = '&hash[]=view&hash[]='

HASH_find = '&hash[]=7fffff&hash[]='
#act=get&page=0&hash%[]=filmoteka&hash[]=7fffff&hash[]=recall

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


def KNO_start(page, sfind, cook):
    
    dbg_log('-KNO_start')

    if page == '0':
        http = get_url(KNO_url)
        
    ext_ls = [('<КАТАЛОГ>', '?mode=ctlg'),
              ('<ПОИСК>', '?mode=find')]
   
    if page == "0" and sfind == "":
        for ctTitle, ctMode  in ext_ls:
            item = xbmcgui.ListItem(ctTitle)
            uri = sys.argv[0] + ctMode + '&cook=' + urllib.quote_plus(cook)
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
            dbg_log('- uri:'+  uri + '\n')
        
        
    if sfind == "":
        hpost = ACT_get + page + HASH_fmtk
    else:
        hpost = ACT_get + page + HASH_fmtk + HASH_find + sfind
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
                  dbg_log(name.encode('utf8'))
                  dbg_log(info.encode('utf8'))
                  dbg_log(logo)
                  
                  item = xbmcgui.ListItem(name, iconImage=logo, thumbnailImage=logo)
                  item.setInfo( type='video', infoLabels={'title': name, 'plot': info})
                  uri = sys.argv[0] + '?mode=list'
                  uri += '&id='+id + '&page='+page
                  xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
                  dbg_log('- uri:'+  uri + '\n')
                  i = i + 1
                  
    if i:
        item = xbmcgui.ListItem('<NEXT PAGE>')
        uri = sys.argv[0] + '?page=' + str(int(page) + 1) + '&sfind=' + urllib.quote_plus(sfind) #+ '&cook=' + urllib.quote_plus(cook)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
        dbg_log('- uri:'+  uri + '\n')
        item = xbmcgui.ListItem('<NEXT PAGE +10>')
        uri = sys.argv[0] + '?page=' + str(int(page) + 10) + '&sfind=' + urllib.quote_plus(sfind) #+ '&cook=' + urllib.quote_plus(cook)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
        dbg_log('- uri:'+  uri + '\n')  

    xbmcplugin.endOfDirectory(pluginhandle)
  



def KNO_list(id, cook):
    dbg_log('-KNO_list')
    
    hpost = HASH_view + id
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


def KNO_find(page, cook):     
    dbg_log('-KNO_find:'+ '\n')
    dbg_log('- page:'+  page + '\n')      
    
    kbd = xbmc.Keyboard()
    kbd.setHeading('ПОИСК')
    kbd.doModal()
    if kbd.isConfirmed():
        stxt = kbd.getText()
        dbg_log('- stxt:'+  stxt + '\n')
        KNO_start('0', stxt, cook)


def KNO_play(id, fid):
    dbg_log('-KNO_play')

    hpost = ACT_glnk + fid + HASH_flv + id
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

if mode == 'play': KNO_play(id, fid)
if mode == 'list': KNO_list(id, cook)
if mode == 'find': KNO_find(page, cook)
elif mode == None: KNO_start(page, sfind, cook)

dbg_log('CLOSE:')

