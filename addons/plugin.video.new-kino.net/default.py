#!/usr/bin/python
# -*- coding: utf-8 -*-
# Writer (c) 2012, Silhouette, E-mail: 
# Rev. 0.5.1


import urllib,urllib2,re,sys
import xbmcplugin,xbmcgui,xbmcaddon
from BeautifulSoup import BeautifulSoup

dbg = 0

pluginhandle = int(sys.argv[1])

start_pg = "http://new-kino.net/"
page_pg = "page/"
find_pg = "http://new-kino.net/?do=search&subaction=search&story="
search_start = "&search_start="

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

def NKN_start(url, page, cook):
    dbg_log('-NKN_start:' + '\n')
    dbg_log('- url:'+  url + '\n')
    dbg_log('- page:'+  page + '\n')
    dbg_log('- cook:'+  cook + '\n')    
    ext_ls = [('<КАТАЛОГ>', '?mode=ctlg'),
              ('<ПОИСК>', '?mode=find')]
    if url.find(find_pg) != -1:
        n_url = url + search_start + page
    else:
        n_url = url + page_pg + page + '/'
        
    dbg_log('- n_url:'+  n_url + '\n')
    horg = get_url(n_url, cookie = cook, save_cookie = True)
    if cook=='':
        cook = re.search('<cookie>(.+?)</cookie>', horg).group(1)
    i = 0
    
    for ctTitle, ctMode  in ext_ls:
        item = xbmcgui.ListItem(ctTitle)
        uri = sys.argv[0] + ctMode + '&cook=' + urllib.quote_plus(cook)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
        dbg_log('- uri:'+  uri + '\n')    
    

    http = re.sub('<br />', '', horg)
    hrefs = re.compile('<a href="(.*?)(#|">|" >)(.*?)</a></h4>').findall(http)

    if len(hrefs):
        news_id = re.compile("news-id-[0-9]")
        news = BeautifulSoup(http).findAll('div',{"id":news_id})
        
        if (len(hrefs) == len(news)):
            for sa in news:

                href = hrefs[i][0]
                dbg_log('-HREF %s'%href)
                infos = re.compile('<img src="/(.*?)" alt="(.*?)" title="(.*?)" /></a><!--TEnd--></div>(.*?)</div>').findall(str(sa))
                for logo, alt, title, plot in infos:
                    img = start_pg + logo
                    dbg_log('-TITLE %s'%title)
                    dbg_log('-IMG %s'%img)
                    dbg_log('-PLOT %s'%plot)

                    item = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
                    item.setInfo( type='video', infoLabels={'title': title, 'plot': plot})
                    uri = sys.argv[0] + '?mode=view' \
                    + '&url=' + urllib.quote_plus(href) + '&img=' + urllib.quote_plus(img) \
                     + '&name=' + urllib.quote_plus(title)+ '&cook=' + urllib.quote_plus(cook)
                    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
                    dbg_log('- uri:'+  uri + '\n')
                    i = i + 1
                
    if i:
        item = xbmcgui.ListItem('<NEXT PAGE>')
        uri = sys.argv[0] + '?page=' + str(int(page) + 1) + '&url=' + urllib.quote_plus(url)+ '&cook=' + urllib.quote_plus(cook)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
        dbg_log('- uri:'+  uri + '\n')
        item = xbmcgui.ListItem('<NEXT PAGE +10>')
        uri = sys.argv[0] + '?page=' + str(int(page) + 10) + '&url=' + urllib.quote_plus(url)+ '&cook=' + urllib.quote_plus(cook)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
        dbg_log('- uri:'+  uri + '\n')        
 
    xbmcplugin.endOfDirectory(pluginhandle) 


def NKN_view(url, img, name, cook):     
    dbg_log('-NKN_view:'+ '\n')
    dbg_log('- url:'+  url + '\n')
    dbg_log('- img:'+  img + '\n')
    dbg_log('- name:'+  name + '\n')
        
    http = get_url(url, cookie = cook)
    news_id = re.compile("news-id-[0-9]")
    news = BeautifulSoup(http).findAll('div',{"id":news_id})

    for sa in news:    
        #print str(sa)
        flvars = re.compile('<param name="flashvars" value="(.*?)"').findall(str(sa))
        #print urllib.unquote_plus(flvars[0])
        files = re.compile('file=(.*?)"').findall(str(sa))

        i = 1
        for file in files:
            if len(files) > 1:
                title = str(i) + ' - ' + name
            else:
                title = name
            i += 1

            item = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
            uri = sys.argv[0] + '?mode=play' \
            + '&url=' + urllib.quote_plus(file) + '&cook=' + urllib.quote_plus(cook)
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item)  
            dbg_log('- uri:'+  uri + '\n')

        xbmcplugin.endOfDirectory(pluginhandle)




def NKN_play(url, cook):     
    dbg_log('-NKN_play:'+ '\n')
    dbg_log('- url:'+  url + '\n')
    
    item = xbmcgui.ListItem(path = url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)

def NKN_ctlg(url, cook):
    dbg_log('-NKN_ctlg:' + '\n')
    dbg_log('- url:'+  url + '\n')

    catalog = [("komedii/", "Комедии"),
               ("boeviki/", "Боевики"),
               ("trillery/", "Триллеры"),
               ("detektivnye/", "Детективные"),
               ("voennye/", "Военные"),
               ("otechestvennye/", "Отечественные"),
               ("istoricheskie/", "Исторические"),
               ("semejjnye/", "Семейные"),
               ("prikljuchencheskie/", "Приключенческие"),
               ("animacionnye/", "Анимационные"),
               ("dokumentalnye/", "Документальные"),
               ("serialy/", "Сериалы"),
               ("fantasticheskie/", "Фантастические"),
               ("misticheskie/", "Мистические"),
               ("uzhasy/", "Ужасы"),
               ("fjentezi/", "Фэнтези"),
               ("dramy/", "Драмы"),
               ("melodramy/", "Мелодрамы"),
               ("kriminalnye/", "Криминальные"),
               ("jumor/", "Юмор"),
               ("oskar/", "Премия Оскар")]
               
    for ctLink, ctTitle  in catalog:
        item = xbmcgui.ListItem(ctTitle)
        uri = sys.argv[0] \
        + '?url=' + urllib.quote_plus(start_pg + ctLink) + '&cook=' + urllib.quote_plus(cook)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
        dbg_log('- uri:'+  uri + '\n')
        
    xbmcplugin.endOfDirectory(pluginhandle)

def uni2cp(ustr):
    raw = ''
    uni = unicode(ustr, 'utf8')
    uni_sz = len(uni)
    for i in range(uni_sz):
        raw += ('%%%02X') % ord(uni[i].encode('cp1251'))
    return raw  

def NKN_find(cook):     
    dbg_log('-NKN_find:'+ '\n')
    dbg_log('- cook:'+  cook + '\n')      
    
    kbd = xbmc.Keyboard()
    kbd.setHeading('ПОИСК')
    kbd.doModal()
    if kbd.isConfirmed():
        stxt = uni2cp(kbd.getText())
        furl = find_pg + stxt
        dbg_log('- furl:'+  furl + '\n')
        NKN_start(furl, '1', cook)

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


cook = ''
mode=''
url=''
ordr='0'
dir='0'
off='0'
gnrs=''
imag=''
name=''

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
    imag=urllib.unquote_plus(params['img'])
    dbg_log('-IMaG:'+ imag + '\n')
except: pass 
try: 
    name=urllib.unquote_plus(params['name'])
    dbg_log('-NAME:'+ name + '\n')
except: pass 
try: 
    cook=urllib.unquote_plus(params['cook'])
    dbg_log('-COOK:'+ cook + '\n')
except: pass

if url=='':
    url = start_pg

if mode == '': NKN_start(url, page, cook)
elif mode == 'ctlg': NKN_ctlg(url, cook)
elif mode == 'view': NKN_view(url, imag, name, cook)
elif mode == 'play': NKN_play(url, cook)
elif mode == 'find': NKN_find(cook)



