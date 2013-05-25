#!/usr/bin/python
# -*- coding: utf-8 -*-
# Writer (c) 2013, Silhouette, E-mail:
# Rev. 0.1.1


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
proj_pg = start_pg + "/projects"

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

# *******************************************************************  
# *******************************************************************  
# *******************************************************************  
  
def D24_start(url):
    dbg_log('-D24_start:' + '\n')
    dbg_log('- url:'+  url + '\n')

    http = get_url(url)
    nav = BeautifulSoup(http).findAll('ul',{"class":"content-nav"})

    if len(nav):
        prj_ls = re.compile('<a class="link" href="(.*?)"><span class="bg"><span>(.*?)</span>(.*?)</span></a>').findall(str(nav[0]))
        for href, title1, title2 in prj_ls:
            img = get_logo(title1)
            if title2 != '': title1 += '-'+title2
            item = xbmcgui.ListItem(title1, iconImage=img, thumbnailImage=img)
            uri = sys.argv[0] + '?mode=proj' + '&url=' + urllib.quote_plus(href)\
            + '&img=' + urllib.quote_plus(img)
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
            dbg_log('- uri:'+  uri + '\n')
        
    xbmcplugin.endOfDirectory(pluginhandle)
    

def D24_proj(url, img):
    dbg_log('-ND24_proj:' + '\n')
    dbg_log('- url:'+  url + '\n')

    http = get_url(start_pg + url)
    prj = BeautifulSoup(http).findAll('ul',{"class":"projects"})

    if len(prj):
        link_ls = re.compile('<a class="link" href="(.*?)">(.*?)</a>').findall(str(prj[0]))
        for href, title in link_ls:
            item = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
            uri = sys.argv[0] + '?mode=view' + '&url=' + urllib.quote_plus(href)\
             + '&name=' + urllib.quote_plus(title)
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
            dbg_log('- uri:'+  uri + '\n')
        
    xbmcplugin.endOfDirectory(pluginhandle)

def D24_view(url, name):     
    dbg_log('-D24_view:'+ '\n')
    dbg_log('- url:'+  url + '\n')
        
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')#movies episodes tvshows
        
    http = get_url(start_pg + url)
    cont = BeautifulSoup(http).findAll('div',{"class":"content-holder"})

    if len(cont):
        img_ls = re.compile('<img alt=".*?" height=".*?" src="(.*?)" width=".*?" />').findall(str(cont[0]))
        if len(img_ls): img = re.sub(' ','%20', start_pg + img_ls[0])
        else: img = '' 
        print img
        p_ls = re.compile('<p>(.*?)</p>').findall(re.sub('[\n\r\t]',' ',str(cont[0])))
        plot = ''
        for pi in p_ls: plot += pi
        plot = re.sub('<br />','\n', plot)
        
        http = get_url(start_pg + url + '/videos')
        prl = BeautifulSoup(http).findAll('ul',{"class":"project-list"})

        if len(prl):
#        <div class="img-holder"><img alt="" height="138" src="/uploads/video/.thumbs/dd90084412067907f8aad3d19115ed05_d6a76b.jpg" width="184" /></div>
#        <h2><a class="link" href="/project/4544/video/1806">Трилогия 9.11 (18+)</a></h2>
            link_ls = re.compile('<a class="link" href="(.*?)">(.*?)</a>').findall(str(prl[0]))
            for href,descr in link_ls:
                http = get_url(start_pg + href)
                
                #<div class="dm_flow_player {&quot;clip&quot;:{&quot;url&quot;:&quot;\/uploads\/video\/60a96e9d8aacd97e3f224e59a84fa9e4.flv&quot;,&quot;autoPlay&quot;:true,&quot;scaling&quot;:&quot;fit&quot;},&quot;plugins&quot;:{&quot;controls&quot;:true},&quot;player_web_path&quot;:&quot;\/dmFlowPlayerPlugin\/swf\/lib\/flowplayer-3.1.5.swf&quot;,&quot;mimeGroup&quot;:&quot;video&quot;}" style="width: 592px; height: 378px; display: block;"></div></div>
                #"url":"\/uploads\/video\/60a96e9d8aacd97e3f224e59a84fa9e4.flv"
                flow_ls = re.compile('<div class="dm_flow_player(.*?)"></div>').findall(http)
                if len(flow_ls):
                    flv = re.sub('\\\/', '/', re.sub('&quot;','\"', flow_ls[0]))
                    url_ls = re.compile('"url":"(.*?)"').findall(flv)
                    if len(url_ls):
                        item = xbmcgui.ListItem(name + '-' + descr, iconImage=img, thumbnailImage=img)
                        uri = sys.argv[0] + '?mode=play' \
                        + '&url=' + urllib.quote_plus(start_pg + url_ls[0])
                        
                        item.setInfo( type='video', infoLabels={'title': name, 'plot': plot})
                        item.setProperty('IsPlayable', 'true')
                        xbmcplugin.addDirectoryItem(pluginhandle, uri, item)  
                        dbg_log('- uri:'+  uri + '\n')

    xbmcplugin.endOfDirectory(pluginhandle)


def D24_play(url):     
    dbg_log('-D24_play:'+ '\n')
    dbg_log('- url:'+  url + '\n')
    
    item = xbmcgui.ListItem(path = url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)

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
    url = proj_pg

if mode == '': D24_start(url)
elif mode == 'proj': D24_proj(url, imag)
elif mode == 'view': D24_view(url, name)
elif mode == 'play': D24_play(url)



