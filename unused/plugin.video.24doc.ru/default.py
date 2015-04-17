#!/usr/bin/python
# -*- coding: utf-8 -*-
# Writer (c) 2013, Silhouette, E-mail:
# Rev. 0.2.0


import urllib,urllib2,re,sys
import xbmcplugin,xbmcgui,xbmcaddon
from BeautifulSoup import BeautifulSoup


dbg = 0

__addon__    = xbmcaddon.Addon(id='plugin.video.24doc.ru') 
pluginhandle = int(sys.argv[1])


def get_logo(key):
    logos = {'Арт':'art',
            'Эко':'eko',
            'Ино':'ino',
            'Люди':'ludi',
            'Полит':'polit',
            'Россия':'rus'}
      
    try:
        logo = xbmc.translatePath( __addon__.getAddonInfo('path') + '\\resources\\' + logos[key] + '.png')
    except: 
        logo = xbmc.translatePath( __addon__.getAddonInfo('path') + '\\icon.png')
    
    return logo
            
start_pg = "http://24doc.ru"
proj_pg = start_pg + "/project"
online_pg = start_pg + "/movies"
page_pg = "?page="

def dbg_log(line):
    if dbg: print line

def get_url(url, data = None, cookie = None, save_cookie = False, referrer = None):
    dbg_log('-getURL:'+  url + '\n')
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

# *******************************************************************  
# *******************************************************************  
# *******************************************************************  
def D24_start():
    
    dbg_log('-D24_start')

    name='Фильмы-Онлайн'
    item = xbmcgui.ListItem(name)
    uri = sys.argv[0] + '?mode=films&url=' + urllib.quote_plus(online_pg)
    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

    name='Анонсы/Preview'
    item = xbmcgui.ListItem(name)
    uri = sys.argv[0] + '?mode=pall&url=' + urllib.quote_plus(proj_pg)
    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  

    xbmcplugin.endOfDirectory(pluginhandle)  

   
def D24_pall(url, page):
    dbg_log('-ND24_proj:' + '\n')
    dbg_log('- url:'+  url + '\n')

    http = get_url(url + page_pg + page)
    prj = BeautifulSoup(http).findAll('ul',{"class":"projects"})

    i = 0
    if len(prj):
        link_ls = re.compile('<a class="link" href="(.*?)">(.*?)</a>').findall(str(prj[0]))
        img = xbmc.translatePath( __addon__.getAddonInfo('path') + '\\icon.png')
        for href, title in link_ls:
            item = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
            uri = sys.argv[0] + '?mode=pview' + '&url=' + urllib.quote_plus(href)\
             + '&name=' + urllib.quote_plus(title)
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
            dbg_log('- uri:'+  uri + '\n')
            i += 1
            
    if i:
        item = xbmcgui.ListItem('<NEXT PAGE>')
        uri = sys.argv[0] + '?mode=pall&page=' + str(int(page) + 1) + '&url=' + urllib.quote_plus(url)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
        dbg_log('- uri:'+  uri + '\n')
        
    xbmcplugin.endOfDirectory(pluginhandle)
    

def D24_pview(url, name):     
    dbg_log('-D24_view:'+ '\n')
    dbg_log('- url:'+  url + '\n')
        
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')#movies episodes tvshows
        
    http = get_url(start_pg + url)
    oneline = re.sub('[\n\r\t]',' ',http)
    img_ls = re.compile('<div class="preview_play"></div> *?<a href=".*?"> *?<img src="(.*?)" alt').findall(oneline)
    lnk_ls = re.compile('<div class="tv_show_desc"> *?<a href="(.*?)">(.*?)</a>').findall(oneline)
    plot_ls = re.compile('<div class="about_video_toggle"> *?(.*?) *?</div>').findall(oneline)

    if lnk_ls == []:
        lnk_ls = [('', '[COLOR FFE13723]НЕТ ВИДЕО [/COLOR]')]
        img_ls = re.compile('"background-image:url\(\'(.*?)\'\)').findall(oneline)
        
    i = 0
    for href,dscr in lnk_ls:
        if len(img_ls) > i: img = re.sub(' ','%20', start_pg + img_ls[i])
        else: img = '' 

        title = dscr.strip() + '-' + name
        if len(plot_ls):
            plot = plot_ls[0].replace('<p>', '').replace('</p>', '').replace('<br />', '')
        else:
            plot = title
        
        item = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
        uri = sys.argv[0] + '?mode=pplay' \
        + '&url=' + urllib.quote_plus(start_pg + href)
        
        item.setInfo( type='video', infoLabels={'title': title, 'plot': plot})
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item)  
        dbg_log('- uri:'+  uri + '\n')
        i += 1
    xbmcplugin.endOfDirectory(pluginhandle)
    

def D24_pplay(url):     
    dbg_log('-D24_pplay:'+ '\n')
    dbg_log('- url:'+  url + '\n')

    http = get_url(url)
    src_ls = re.compile('<source src="(.*?)"').findall(http)
    if len(src_ls):
        item = xbmcgui.ListItem(path = start_pg + src_ls[0])
        xbmcplugin.setResolvedUrl(pluginhandle, True, item)


def D24_fplay(url):     
    dbg_log('-D24_fplay:'+ '\n')
    dbg_log('- url:'+  url + '\n')

    item = xbmcgui.ListItem(path = url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)
        

def D24_films(url, page):
    dbg_log('-ND24_films:' + '\n')
    dbg_log('- url:'+  url + '\n')

    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')#movies episodes tvshows
    
    http = get_url(url + page_pg + page)
    prj = BeautifulSoup(http).findAll('div',{"class":"video_block"})

    i = 0
    for i in xrange(len(prj)):
        oneline = re.sub('[\n\r\t]',' ',str(prj[i]))
        link_ls = re.compile('a href="(.*?)" title="(.*?)".*?data-description="(.*?)" data-id=".*?" data-video="(.*?)"').findall(oneline)
        img_ls = re.compile('<img width=".*?" height=".*?" src="(.*?)" />').findall(oneline)
        for href, title, plot, video in link_ls:
            if len(img_ls): img = start_pg + img_ls[0]
            else:  img = xbmc.translatePath( __addon__.getAddonInfo('path') + '\\icon.png')
            
            item = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
            uri = sys.argv[0] + '?mode=fplay' \
            + '&url=' + urllib.quote_plus(start_pg + video)
            
            item.setInfo( type='video', infoLabels={'title': title, 'plot': plot})
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item)  
            dbg_log('- uri:'+  uri + '\n')

            
    if i:
        item = xbmcgui.ListItem('<NEXT PAGE>')
        uri = sys.argv[0] + '?mode=films&page=' + str(int(page) + 1) + '&url=' + urllib.quote_plus(url)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
        dbg_log('- uri:'+  uri + '\n')
        
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

#if url=='':
#    url = proj_pg

if mode == '': D24_start()
elif mode == 'pall': D24_pall(url, page)
elif mode == 'pview': D24_pview(url, name)
elif mode == 'pplay': D24_pplay(url)
elif mode == 'films': D24_films(url, page)
elif mode == 'fplay': D24_fplay(url)


