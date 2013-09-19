#!/usr/bin/python
# -*- coding: utf-8 -*-
# Writer (c) 2013, Silhouette, E-mail: 
# Rev. 0.3.0


import urllib,urllib2,re,sys
import xbmcplugin,xbmcgui,xbmcaddon
from BeautifulSoup import BeautifulSoup

try:
  # Import UnifiedSearch
  sys.path.append(os.path.dirname(__file__)+ '/../plugin.video.unified.search')
  from unified_search import UnifiedSearch
except: pass

__settings__ = xbmcaddon.Addon(id='plugin.video.kinoxa-x.ru')
use_translit = __settings__.getSetting('translit')

try:  
  import Translit as translit
  translit = translit.Translit()  
except: use_translit = 'false'



dbg = 0

pluginhandle = int(sys.argv[1])

start_pg = "http://www.kinoxa-x.ru"
page_pg = start_pg + "/load/0-"
fdpg_pg = ";t=0;md=;p="
find_pg = start_pg + "/search/?q="

def gettranslit(msg):
    if use_translit == 'true': 
        return translit.rus(msg)
    else: return msg
    

def dbg_log(line):
    if dbg: print line

def get_url(url, data = None, cookie = None, save_cookie = False, referrer = None):
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
        if setcookie:
            setcookie = re.search('([^=]+=[^=;]+)', setcookie).group(1)
            link = link + '<cookie>' + setcookie + '</cookie>'
    
    response.close()
    return link

def KNX_list(url, page, type):
    dbg_log('-KNX_list:' + '\n')
    dbg_log('- url:'+  url + '\n')
    dbg_log('- page:'+  page + '\n')
    dbg_log('- type:'+  type + '\n')
        
    if type == 'ctlg':
        n_url = url + '-' + page + '-2'
    else:
        n_url = url + page
        
    dbg_log('- n_url:'+  n_url + '\n')
    
    if type != 'unis':
        xbmcplugin.setContent(int(sys.argv[1]), 'episodes')#movies episodes tvshows
    
    http = get_url(n_url)
    i = 0
    
    if type == '':
        ext_ls = [('<КАТАЛОГ>', '?mode=ctlg'),
                  ('<ПОИСК>', '?mode=find')]
        for ctTitle, ctMode  in ext_ls:
            item = xbmcgui.ListItem(ctTitle)
            uri = sys.argv[0] + ctMode
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
            dbg_log('- uri:'+  uri + '\n')    
    

    if type == 'find' or type == 'unis':
        entrys = BeautifulSoup(http).findAll('div',{"class":"eTitle"})
        msgs = BeautifulSoup(http).findAll('div',{"class":"eMessage"})
        unis_res = []
    else:
        entry_id = re.compile("entryID[0-9]")
        entrys = BeautifulSoup(http).findAll('div',{"id":entry_id})

    for eid in entrys:
        
        if type == 'find' or type == 'unis':
            films = re.compile('<a href="(.*?)">(.*?)</a>').findall(str(eid))
            plots = re.compile('style=".*?">(.*?)</div>').findall(re.sub('[\n\r\t]', ' ',str(msgs[i])))
        else:
            films = re.compile('<a href="(.*?)"><h[0-9] style=".*?">(.*?)</h[0-9]></a>').findall(str(eid))
            plots = re.compile('<span class="kr-opis-rol">(.*?)</noindex>').findall(re.sub('[\n\r\t]', ' ',str(eid)))
            imgs = re.compile('<img src="(.*?)"').findall(str(eid))

        for href, title in films:
            title = re.sub('<.*?>', '',title)
            try: img = imgs[0]
            except: img = ''
            try: plot = re.sub('<.*?>', '',plots[0])
            except: plot = title
            dbg_log('-TITLE %s'%title)
            dbg_log('-IMG %s'%img)
            dbg_log('-PLOT %s'%plot)

            if type != 'unis':
                item = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
                item.setInfo( type='video', infoLabels={'title': title, 'plot': plot})
                uri = sys.argv[0] + '?mode=play' \
                + '&url=' + urllib.quote_plus(href)
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(pluginhandle, uri, item, False)  
                dbg_log('- uri:'+  uri + '\n')
                i = i + 1
            else:
              try:
                  unis_res.append({'title':  title, 'url': href, 'image': img, 'plugin': 'plugin.video.kinoxa-x.ru'})
              except: pass

    if type == 'unis':
      try: UnifiedSearch().collect(unis_res)
      except:  pass
    else:
      if i :
          item = xbmcgui.ListItem('<NEXT PAGE>')
          uri = sys.argv[0] + '?page=' + str(int(page) + 1) + '&url=' + urllib.quote_plus(url) + '&type=' + type
          xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
          dbg_log('- uri:'+  uri + '\n')
          if type != 'find':
              item = xbmcgui.ListItem('<NEXT PAGE +5>')
              uri = sys.argv[0] + '?page=' + str(int(page) + 5) + '&url=' + urllib.quote_plus(url) + '&type=' + type
              xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
              dbg_log('- uri:'+  uri + '\n')        
     
      xbmcplugin.endOfDirectory(pluginhandle) 



def KNX_list2(url, page):
    dbg_log('-KNX_list:' + '\n')
    dbg_log('- url:'+  url + '\n')
    dbg_log('- page:'+  page + '\n')


    n_url = url + page
        
    dbg_log('- n_url:'+  n_url + '\n')
    
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')#movies episodes tvshows
    
    http = get_url(n_url)
    i = 0
    
    entrys = BeautifulSoup(http).findAll('div',{"class":"eTitle"})
    msgs = BeautifulSoup(http).findAll('div',{"class":"eMessage"})

    for eid in entrys:

        films = re.compile('<a href="(.*?)">(.*?)</a>').findall(str(eid))
        plots = re.compile('style=".*?">(.*?)</div>').findall(re.sub('[\n\r\t]', ' ',str(msgs[i])))
        
        for href, title in films:
            img = ''
            title = re.sub('<.*?>', '',title)
            try: plot = re.sub('<.*?>', '',plots[0])
            except: plot = title
            dbg_log('-TITLE %s'%title)
            dbg_log('-PLOT %s'%plot)

            item = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
            item.setInfo( type='video', infoLabels={'title': title, 'plot': plot})
            uri = sys.argv[0] + '?mode=play' \
            + '&url=' + urllib.quote_plus(href)
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, False)  
            dbg_log('- uri:'+  uri + '\n')
            i = i + 1
                
    if i:
        item = xbmcgui.ListItem('<NEXT PAGE>')
        uri = sys.argv[0] + '?mode=list&page=' + str(int(page) + 1) + '&url=' + urllib.quote_plus(url)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
        dbg_log('- uri:'+  uri + '\n')
      
 
    xbmcplugin.endOfDirectory(pluginhandle) 
    
def KNX_play(url):     
    dbg_log('-NKN_play:'+ '\n')
    dbg_log('- url:'+  url + '\n')
    
    http = get_url(url)
    iframes = re.compile('<iframe src="(.*?)"').findall(http)
    
    if len(iframes):
        http = get_url(iframes[1])
        flvs = re.compile('src="http(.*?)"').findall(http)
        hrefs = re.compile('<a href="(.*?)">').findall(http)

        if len(flvs):
            item = xbmcgui.ListItem(path = "http" + flvs[0])
            xbmcplugin.setResolvedUrl(pluginhandle, True, item)
        elif len(hrefs):
            item = xbmcgui.ListItem(path = "http" + hrefs[0])
            xbmcplugin.setResolvedUrl(pluginhandle, True, item)

def KNX_ctlg(url):
    dbg_log('-KNX_ctlg:' + '\n')
    dbg_log('- url:'+  url + '\n')
               
    catalog  = [( "/load/sortirovka_po_godam/filmy_2013_goda/68", '2013 год'),
                ( "/load/sortirovka_po_godam/filmy_2012_goda/65", '2012 год'),
                ( "/load/sortirovka_po_godam/filmy_2011_goda/51", '2011 год'),
                ( "/load/sortirovka_po_godam/filmy_2010_goda/52", '2010 год'),
                ( "/load/sortirovka_po_godam/filmy_2009_goda/53", '2009 год'),
                ( "/load/kategorii/filmy_v_3d/67", 'Фильмы в 3D'),
                ( "/load/kategorii/komedii/30", 'Комедии'),
                ( "/load/kategorii/boeviki/31", 'Боевики'),
                ( "/load/kategorii/dramy/32", 'Драмы'),
                ( "/load/kategorii/uzhasy/33", 'Ужасы'),
                ( "/load/kategorii/fantastika/34", 'Фантастика'),
                ( "/load/kategorii/trillery/35", 'Триллеры'),
                ( "/load/kategorii/detektivy/36", 'Детективы'),
                ( "/load/kategorii/dokumentalnye/37", 'Документальные'),
                ( "/load/kategorii/multfilmy/38", 'Мультфильмы'),
                ( "/load/kategorii/mistika/39", 'Мистика'),
                ( "/load/kategorii/sovetskie_filmy/69", 'Советские фильмы'),
                ( "/load/kategorii/semejnye/40", 'Семейные'),
                ( "/load/kategorii/sportivnye/41", 'Спортивные'),
                ( "/load/kategorii/melodramy/42", 'Мелодрамы'),
                ( "/load/kategorii/russkie_serialy/43", 'Русские сериалы'),
                ( "/load/kategorii/zarubezhnye_serialy/64", 'Зарубежные сериалы'),
                ( "/load/kategorii/trejlery/44", 'Трейлеры'),
                ( "/load/kategorii/fehntezi/46", 'Фэнтези'),
                ( "/load/kategorii/prikljuchenija/47", 'Приключения'),
                ( "/load/kategorii/istoricheskie/48", 'Исторические'),
                ( "/load/kategorii/vestern/49", 'Вестерн'),
                ( "/load/kategorii/animeh/56", 'Аниме'),
                ( "/load/kategorii/kriminal/60", 'Криминал'),
                ( "/load/kategorii/voennye/61", 'Военные'),
                ( "/load/kategorii/goblinskij_perevod/55", 'Гоблинский перевод'),
                ( "/load/kategorii/poznaem_mir/57", 'Познаем мир'),
                ( "/load/kategorii/biografija/58", 'Биография'),
                ( "/load/kategorii/xxx/59", 'XXX'),
                ( "/load/kategorii/jumoristicheskie_peredachi/62", 'Юмористические передачи'),
                ( "/load/kategorii/teleshou/63", 'Передачи'),
                ( "/load/kategorii/filmy_v_vysokom_kachestve_hd/54", 'В высоком качестве HD')]
               
               
    for ctLink, ctTitle  in catalog:
        item = xbmcgui.ListItem(ctTitle)
        uri = sys.argv[0] \
        + '?url=' + urllib.quote_plus(start_pg + ctLink) + '&type=ctlg&page=1'
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
        dbg_log('- uri:'+  uri + '\n')
        
    xbmcplugin.endOfDirectory(pluginhandle)

def uni2enc(ustr):
    raw = ''
    uni = unicode(ustr, 'utf8')
    uni_sz = len(uni)
    for i in xrange(len(ustr)):
        raw += ('%%%02X') % ord(ustr[i])        
    return raw
    
def KNX_find():     
    dbg_log('-KNX_find:'+ '\n')
    
    kbd = xbmc.Keyboard()
    kbd.setHeading('ПОИСК')
    kbd.doModal()
    if kbd.isConfirmed():
        stxt = uni2enc(gettranslit(kbd.getText()))
        furl = find_pg + stxt + fdpg_pg
        dbg_log('- furl:'+  furl + '\n')
        KNX_list(furl, '1', 'find')

def lsChan():
    xbmcplugin.endOfDirectory(pluginhandle)

def get_params():
    param=[]
    #print sys.argv[2]
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


type = ''
mode=''
url=''

try:
    mode=params['mode']
    dbg_log('-MODE:'+ mode + '\n')
except: pass
try: 
    url=urllib.unquote_plus(params['url'])
    dbg_log('-URL:'+ url + '\n')
except: pass  
try: 
    page=urllib.unquote_plus(params['page'])
    dbg_log('-PAGE:'+ page + '\n')
except: page = '1'
try: 
    type=urllib.unquote_plus(params['type'])
    dbg_log('-TYPE:'+ type + '\n')
except: pass

keyword = params['keyword'] if 'keyword' in params else None
unified = params['unified'] if 'unified' in params else None

if url=='':
    url = page_pg

if mode == '': KNX_list(url, page, type)
elif mode == 'ctlg': KNX_ctlg(url)
elif mode == 'play': KNX_play(url)
elif mode == 'find': KNX_find()
elif mode == 'search': 
    url = find_pg + uni2enc(gettranslit(keyword)) + fdpg_pg
    KNX_list(url, '1', 'unis')
    
#elif mode == 'list': KNX_list(url, page)


