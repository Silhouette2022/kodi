#!/usr/bin/python
# -*- coding: utf-8 -*-
# Writer (c) 2018, Silhouette, E-mail: 
# Rev. 0.0.1


import urllib,urllib2, os, re,sys, json,cookielib, base64, socket
import xbmcplugin,xbmcgui,xbmcaddon
from BeautifulSoup import BeautifulSoup
import requests
# from videohosts import moonwalk
import lib.moonwalk as moonwalk

__settings__ = xbmcaddon.Addon(id='plugin.video.kinoha.tv')


dbg = 0

socket.setdefaulttimeout(120)

pluginhandle = int(sys.argv[1])

start_pg = "http://kinoha.tv"
page_pg = start_pg + "/page/"
find_pg = "http://yandex.ru/search/site?searchid=2285403&text="

supported = {'kinoha.tv', 'moonwalk.cc', 'moonwalk.co', 'youtube.com'}

def getSite(s):

    try: full = re.compile('//(.*?)/').findall(s)[0]
    except: 
        try: full = re.compile('(.*?)/').findall(s)[0]
        except:
            try: full = re.compile('//(.*?)').findall(s)[0]
            except: full = s
    parts = full.split('.')
    psz = len(parts)
    if psz == 4:
      site = full
    elif psz > 1:
        site = '%s.%s'%(parts[psz - 2], parts[psz - 1])
    else: site = full
    
    return site  

def dbg_log(line):
    if dbg: xbmc.log(line)

def req_url(url, opts = None, cookies = None, params = None, data = None):
    dbg_log("req_url=>%s"%url)
    dbg_log("_params=>%s"%str(params))
    

    headers = {'User-Agent' : 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:42.0) Gecko/20100101 Firefox/42.0',
               'Accept' : '*/*',
               'Accept-Language' : 'ru,en;q=0.9'
               }
    if opts: 
        headers.update(opts)
        dbg_log("_opts=>%s"%str(opts))
        
    if data :
        dbg_log("_data=>%s"%str(data))
        r = requests.post(url, headers=headers, cookies = cookies, params = params, data = data)
    else:
        r = requests.get(url, headers=headers, cookies = cookies, params = params)
        
    return r

def KNH_list(url, page, type, fdata, cook):
    dbg_log('-KNH_list:' + '\n')
    dbg_log('- url:'+  url + '\n')
    dbg_log('- page:'+  page + '\n')
    dbg_log('- type:'+  type + '\n')
    dbg_log('- fdata:'+  fdata + '\n')
    
    
  
    if type == 'ctlg':
        n_url = url + 'page/' + page + '/'
        pdata = None
    elif fdata != '':
        n_url = url + fdata
        pdata = None
    else:
        n_url = url + page + '/'
        pdata = None

                
        
    dbg_log('- n_url:'+  n_url + '\n')
    dbg_log('- pdata:'+  str(pdata) + '\n')
    
    if type != 'unis' and type != 'unds':
        xbmcplugin.setContent(int(sys.argv[1]), 'episodes')#movies episodes tvshows
        
    if cook : cookies = json.loads(cook)
    else: cookies = None
    
    req = req_url(n_url, cookies = cookies, data=pdata)
    http = req.content
    dbg_log('- cook:'+  str(req.cookies) + '\n')
    i = 0
    unis_res = []
    
    
    if type == '':
        ext_ls = [('<КАТАЛОГ>', '?mode=ctlg'),
                  ('<ПОИСК>', '?mode=find')]
        for ctTitle, ctMode  in ext_ls:
            item = xbmcgui.ListItem(ctTitle)
            uri = sys.argv[0] + ctMode
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
            dbg_log('- uri:'+  uri + '\n')    


    if type == 'find' or type == 'unis' or type == 'unds':
#         print http
        entrys = BeautifulSoup(http).findAll('h3')
    else:        
        entrys = BeautifulSoup(http).findAll('div',{"class":"shortstory"})

    for eid in entrys:
        xbmc.log(str(eid))
        if type == 'find' or type == 'unis' or type == 'unds':
            hrtt = re.compile('href="(.*?)".*?<span>(.*?)</span>').findall(str(eid))[0]
#             print hrtt
            href = hrtt[0]
            title = hrtt[1].replace('<b>', '').replace('</b>', '') 
            plot = ''
            try: img = start_pg + re.compile('<img src="(.*?)"').findall(re.sub('\thumbs', '',str(eid)))[0]
            except: img = ''
        else:
            href = re.compile('<a href="(.*?)" style=').findall(str(eid))[0]
            plots = BeautifulSoup(str(eid)).findAll('div',{"class":"shortimg"})
#            print plots            
            try:
                plot = re.compile('</a>(.*?)<br />').findall(re.sub('[\n\r\t]', ' ',str(plots[0])))[0]
            except:
                plot = ''
            try:
                img = start_pg + re.compile('<img src="(.*?)"').findall(re.sub('\thumbs', '',str(eid)))[0]
            except:
                img = ''
            try:
                title = re.compile('title="(.*?)" /></a>').findall(str(eid))[0]
            except:
                title = re.compile('alt="(.*?)"').findall(str(eid))[0]
                


        dbg_log('-HREF %s'%href)
        dbg_log('-TITLE %s'%title)
        dbg_log('-IMG %s'%img)
        dbg_log('-PLOT %s'%plot)

        if type != 'unis':
            item = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
            item.setInfo( type='video', infoLabels={'title': title, 'plot': plot})
            uri = sys.argv[0] + '?mode=title' \
            + '&url=' + urllib.quote_plus(href)
            if type != 'unds': uri += '&cook=' + json.dumps(req.cookies.get_dict())
#             item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True) #False)  
            dbg_log('- uri:'+  uri + '\n')
            i = i + 1
        else:
          try: unis_res.append({'title':  title, 'url': href, 'image': img, 'plugin': 'plugin.video.kinoxa-x.ru'})
          except: pass

    if type == 'unis':
      try: UnifiedSearch().collect(unis_res)
      except: pass
    else:
        if type != 'unds' and i :
          item = xbmcgui.ListItem('<NEXT PAGE>')
          uri = sys.argv[0] + '?page=' + str(int(page) + 1) + '&url=' + urllib.quote_plus(url) + '&type=' + type + '&find=' + urllib.quote_plus(fdata) + '&cook=' + urllib.quote_plus(cook)
          xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
          dbg_log('- uri:'+  uri + '\n')
          if type != 'find':
              item = xbmcgui.ListItem('<NEXT PAGE +5>')
              uri = sys.argv[0] + '?page=' + str(int(page) + 5) + '&url=' + urllib.quote_plus(url) + '&type=' + type + '&find=' + urllib.quote_plus(fdata) + '&cook=' + urllib.quote_plus(cook)
              xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
              dbg_log('- uri:'+  uri + '\n')        
     
        xbmcplugin.endOfDirectory(pluginhandle) 

def KNH_title(url):
    dbg_log('-NKH_title:'+ '\n')
    dbg_log('- url:'+  url + '\n')
    
    req = req_url(url)
    http = req.content
    
    fullimg = BeautifulSoup(http).find('div',{"class":"fullimg"})
    imgs = BeautifulSoup(str(fullimg))
    img = start_pg + imgs.a['href']
    name = imgs.img['title'].encode('utf8')
#     print imgs.text.encode('utf8')
    try:
        plot = re.compile('<!--TEnd-->(.*?)<br />').findall(re.sub('[\n\r\t]', ' ',str(fullimg)))[0]
    except:
        plot = ''
    
    i = 1
    wdic = { '' : 0}
    iframes = re.compile('<iframe src="(.*?)"').findall(http)
    for iframe in iframes:
        try: web = getSite(iframe)
        except: web = ' '
        if web in wdic:
            t = wdic[web] + 1
            wdic[web] = t
        else: wdic[web] = 1
        
        if web[0].isdigit():
            title = '[[COLOR FFFFFF00]%s-%s[/COLOR]] %s'%(str(wdic[web]),web,name)
        elif web not in supported:
            title = '[[COLOR FFFF0000]%s-%s[/COLOR]] %s'%(str(wdic[web]),web,name)
        else:
            title = '[%s-%s] %s'%(str(wdic[web]),web,name)
                  
        item = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
        item.setInfo( type='video', infoLabels={'title': title, 'plot': plot})
        uri = sys.argv[0] + '?mode=play' \
        + '&url=' + urllib.quote_plus(iframe)\
        + '&ref=' + urllib.quote_plus(url)
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, False)  
        dbg_log('- uri:'+  uri + '\n')
        i = i + 1
    
    xbmcplugin.endOfDirectory(pluginhandle)
        
        
def KNH_show(url):
    dbg_log('-KNH_show:' + '\n')
    dbg_log('- url:'+  url + '\n')
    
    item = xbmcgui.ListItem('Play Video')
    uri = sys.argv[0] + '?mode=play&url=' + urllib.quote_plus(url)
    item.setProperty('IsPlayable', 'true')
    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, False)  
    dbg_log('- uri:'+  uri + '\n')
    xbmcplugin.endOfDirectory(pluginhandle)
   

def get_moonwalk(url, ref):
    dbg_log('-get_moonwalk:'+ '\n')
    dbg_log('- url:'+  url + '\n')    
    dbg_log('- ref:'+  ref + '\n') 

    
    manifest_links, subtitles, season, episode = moonwalk.get_playlist(url)
#     values, attrs = moonwalk.get_access_attrs(http, url)
#     print values
#     print attrs
#     print manifest_links
    
    r0 = [str(key) for key in manifest_links.keys()]
    dbg_log('- r0:'+  str(r0) + '\n')
    i = xbmcgui.Dialog().select('Video Quality', r0)

    return manifest_links[int(r0[i])]
        
def KNH_play(url, ref):
    dbg_log('-NKH_play:'+ '\n')
    dbg_log('- url:'+  url + '\n')
    

    link = None
    
    if "kinoha" or "moonwalk" in url:
        link = get_moonwalk(url, ref)
    elif "youtube" in url:
        
        videoId = re.findall('youtube.com/embed/(.*?)[\"\'\?]', url)[0]
        link = 'plugin://plugin.video.youtube/play/?video_id=' + videoId
        dbg_log('-youtube: %s \n'%link)
    else:
        link = get_moonwalk(url, ref)

    if link != None:
        item = xbmcgui.ListItem(path = link)
        xbmcplugin.setResolvedUrl(pluginhandle, True, item)

def KNH_ctlg(url):
    dbg_log('-KNH_ctlg:' + '\n')
    dbg_log('- url:'+  url + '\n')
               
    catalog  = [

            ("/film-2017/", "Фильмы 2017 года"),
            ("/film-2016/", "Фильмы 2016 года"),
            ("/film-2015/", "Фильмы 2015 года"),
            ("/film-2014/", "Фильмы 2014 года"),
            ("/film-2013/", "Фильмы 2013 года"), 
                            
            ("/biografii/", "Биографии"),
            ("/boeviki/", "Боевики"),
            ("/westerni/", "Вестерны"),
            ("/voennie/", "Военные"),
            ("/detektivi/", "Детективы"),
            ("/detskie/", "Детские"),
            ("/documentalnoe/", "Документальные"),
            ("/drami/", "Драмы"),
            ("/history/", "Исторические"),
            ("/comedy/", "Комедии"),
            ("/criminal/", "Криминал"),
            ("/melodramy/", "Мелодрамы"),
            ("/multiki/", "Мультфильмы"),
            ("/muzikly/", "Мюзиклы"),
            ("/rus/", "Отечественные"),
            ("/priklutcheniya/", "Приключения"),
            ("/semeynie/", "Семейные"),
            ("/sport/", "Cпортивные"),
            ("/trilleri/", "Триллеры"),
            ("/ujasi/", "Ужасы"),
            ("/fantastic/", "Фантастика"),
            ("/fantazy/", "Фэнтези"),

            ("/rus-serial/", "Сериалы Русские"),
            ("/zarubejnie/", "Сериалы Зарубежные")]
               
               
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
    
def uni2cp(ustr):
    raw = ''
    uni = unicode(ustr, 'utf8')
    uni_sz = len(uni)
    for i in range(uni_sz):
        raw += ('%%%02X') % ord(uni[i].encode('cp1251'))
    return raw  
        
def KNH_find(cook):
    dbg_log('-KNH_find:'+ '\n')
    
    kbd = xbmc.Keyboard()
    kbd.setHeading('ПОИСК')
    kbd.doModal()
    if kbd.isConfirmed():
        stxt = kbd.getText()
        furl = find_pg
        dbg_log('- furl:'+  furl + '\n')
        KNH_list(furl, '1', 'find', stxt, cook)

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
mode = ''
url = ''
find = ''
ref = ''
cook = ''

try:
    mode=params['mode']
    dbg_log('-MODE:'+ mode + '\n')
except: pass
try: 
    url=urllib.unquote_plus(params['url'])
    dbg_log('-URL:'+ url + '\n')
except: pass  
try: 

    ref=urllib.unquote_plus(params['ref'])
    dbg_log('-REF:'+ ref + '\n')

except: pass 
try: 
    page=urllib.unquote_plus(params['page'])
    dbg_log('-PAGE:'+ page + '\n')
except: page = '1'
try: 
    type=urllib.unquote_plus(params['type'])
    dbg_log('-TYPE:'+ type + '\n')
except: pass
try: 
    find=urllib.unquote_plus(params['find'])
    dbg_log('-FIND:'+ find + '\n')
except: pass
try:
    cook=urllib.unquote_plus(params['cook'])
    dbg_log('-COOK:'+ cook + '\n')
except: pass

keyword = params['keyword'] if 'keyword' in params else None
usearch = params['usearch'] if 'usearch' in params else None
if usearch: type = 'unds'

if url=='':
    url = page_pg

if mode == '': KNH_list(url, page, type, find, cook)
elif mode == 'title': KNH_title(url)
elif mode == 'ctlg': KNH_ctlg(url)
elif mode == 'play': KNH_play(url, ref)
elif mode == 'find': KNH_find(cook)
elif mode == 'show': KNH_show(url)
elif mode == 'search': 
    url = find_pg
    KNH_list(url, '1', type, urllib.unquote_plus(keyword), cook)
    
#elif mode == 'list': KNH_list(url, page)


