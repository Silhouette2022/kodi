#!/usr/bin/python
# -*- coding: utf-8 -*-
# Writer (c) 2012, Silhouette, E-mail: 
# Rev. 0.4.4


import urllib,urllib2,re,sys
import xbmcplugin,xbmcgui,xbmcaddon

dbg = 0
dbg_gd = 0

pluginhandle = int(sys.argv[1])

start_pg = "http://sonet.by/video/"
main_pg = "#page:0"
#list_pg = "#page:1"
#find_pg = "#page:3"
find_pg = "actions.php?action=simplesearch&what=films"
list_pg = "actions.php?action=filmlist"
gnrs_pg = "actions.php?action=getgenres"

__settings__ = xbmcaddon.Addon(id='plugin.video.sonet.by')
usr_log = __settings__.getSetting('usr_log')
usr_pwd = __settings__.getSetting('usr_pwd')


def dbg_log(line):
    if dbg: print line
    
def raw2uni(raw):
    unis = u''
    raw_sz = len(raw)
    i = 0
    while  i < raw_sz:
        if i < (raw_sz - 6) and raw[i] == '\\' and raw[i + 1]=='u':
            unis += unichr(int(raw[i + 2] + raw[i + 3] + raw[i + 4] + raw[i + 5], 16))
            i += 6
        else:
            unis += raw[i]
            i += 1
    return unis
    
def uni2raw(ustr):
    raw = ''
    uni = unicode(ustr, 'utf8')
    uni_sz = len(uni)
    for i in range(uni_sz):
        raw += ('%%u%04X') % ord(uni[i])
    return raw    

    
def get_url(url, data = None, cookie = None, save_cookie = False, referrer = None):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Opera/9.80 (X11; Linux i686; U; ru) Presto/2.7.62 Version/11.00')
    req.add_header('Accept', 'text/html, application/xml, application/xhtml+xml, */*')
    req.add_header('Accept-Language', 'ru,en;q=0.9')
    if cookie: req.add_header('Cookie', cookie)
    if referrer: req.add_header('Referer', referrer)
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

def SNB_mnpg(url):
    dbg_log('-SNB_mnpg:' + '\n')
    ext_ls = [('<ПОИСК>', find_pg, '?mode=fdpg'),\
             ('<КАТАЛОГ>', list_pg, '?mode=lspg')]


    http = get_url(url, save_cookie = True)
    mycookie = re.search('<cookie>(.+?)</cookie>', http).group(1)
    http = get_url(url, data = "logon=1&login=" + usr_log + "&pass=" + usr_pwd, cookie = mycookie)
    oneline = re.sub( '\n', ' ', http)
    fm_ls = re.compile("<td class='FilmTD'(.*?)\s+<a title='(.*?)' href='#(.*?)'>\s+<img width='(.*?)px' height='(.*?)px' src='(.*?)' border='(.*?)'").findall(oneline)

    if len(fm_ls):
		    
        for ctTitle, ctLink, ctMode  in ext_ls:
            item = xbmcgui.ListItem(ctTitle)
            uri = sys.argv[0] + ctMode \
            + '&url=' + urllib.quote_plus(url) + '&cook=' + urllib.quote_plus(mycookie)
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
            dbg_log('- uri:'+  uri + '\n')

        for tr, title, href, iw, ih, logo, ib in fm_ls:
            #print href + logo + title
            item = xbmcgui.ListItem(title, iconImage=url + logo, thumbnailImage=url + logo)
            uri = sys.argv[0] + '?mode=plpg' \
            + '&url=' + urllib.quote_plus(href) + \
            '&rfr=' + urllib.quote_plus(url) +'&cook=' + urllib.quote_plus(mycookie)
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
            if dbg_gd: dbg_log('- uri:'+  uri + '\n')
 
    xbmcplugin.endOfDirectory(pluginhandle) 
    
def SNB_plpg(url, cook, rfr):     
    dbg_log('-SNB_plpg:'+ '\n')
    fval = url.split(':')

    furl = start_pg + 'actions.php?action=getfilm&' + fval[0] + '=' + fval[1] + '&PHPSESSID=' + cook
    dbg_log('- furl:'+  furl + '\n')
    http = get_url(furl, cookie = cook, referrer = rfr)

    files = re.compile('"files":\[\{(.*?)\}\]').findall(http)
    infos = re.compile('"Description":"(.*?)"').findall(http)
    
    posts = re.compile('"Poster":\["(.*?)"\]').findall(http)
    if len(posts): logo = start_pg + re.sub('\\\/','/',posts[0])
    else:
        posts = re.compile('"BigPosters":\["(.*?)"\]').findall(http)
        if len(posts): logo = start_pg + re.sub('\\\/','/',posts[0])
        else: logo = ''

    if len(files):
        links = re.compile('"ftp":"(.*?)"').findall(files[0])
        titles = re.compile('"Name":"(.*?)"').findall(files[0])
        n_titles = len(titles)
        
        for i in range(len(links)):
            descr = u''
            if( i < n_titles):
                descr = raw2uni(titles[i])
            else:
                descr = str(i + 1)
                
            newlnk = re.sub('\\\/','/',links[i])
 
            item = xbmcgui.ListItem(descr, iconImage=logo)
            uri = sys.argv[0] + '?mode=play' + \
            '&url=' + urllib.quote_plus(newlnk) + '&logo=' + urllib.quote_plus(logo) + '&cook=' + urllib.quote_plus(cook)
    
            title = descr
            thumbnail = logo
            if len(infos): plot = re.sub('<br>','\n', raw2uni(infos[0]))
            else: plot = descr
    
            item.setInfo( type='video', infoLabels={'title': title, 'plot': plot})
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(pluginhandle,uri,item)
            if dbg_gd: dbg_log('- uri:'+  uri + '\n')
           
    xbmcplugin.endOfDirectory(pluginhandle)
    
def SNB_fdpg(url, cook, rfr):     
    dbg_log('-SNB_fdpg:'+ '\n')
    
    kbd = xbmc.Keyboard()
    kbd.setHeading('ПОИСК')
    kbd.doModal()
    if kbd.isConfirmed():
        stxt = uni2raw(kbd.getText())
        furl = url + find_pg + '&text=' + stxt + '&PHPSESSID=' + cook
        dbg_log('- furl:'+  furl + '\n')
        http = get_url(furl, cookie = cook, referrer = rfr)

        lines = re.compile('{"ID":"(.*?)","Name":"(.*?)","OriginalName":"(.*?)","Year":"(.*?)"}').findall(http)

        for fid, fname, forgnm, fyear in lines:
            title = raw2uni(fname + ' (' + forgnm + ') ' + fyear)
            item = xbmcgui.ListItem(raw2uni(title))
            uri = sys.argv[0] + '?mode=plpg' \
            + '&url=' + urllib.quote_plus('film:'+fid) + \
            '&rfr=' + urllib.quote_plus(url) +'&cook=' + urllib.quote_plus(cook)
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
            if dbg_gd: dbg_log('- uri:'+  uri + '\n')

    xbmcplugin.endOfDirectory(pluginhandle)         

def SNB_lspg(url, cook, rfr, ordr, dir, off, gnrs):     
    dbg_log('-SNB_lspg:'+ '\n')
    dir_ls = [('0', '<ПО ВОЗРАСТАНИЮ>', 'DESC'), ('1', '<ПО УБЫВАНИЮ>', 'ASC')]
    ord_ls = [('0', '<ДОБАВЛЕНО>'), ('1', '<ГОД>'), ('5', '<АЛФАВИТ>')]
    dirt =  ''

    if gnrs != '0':
      for i, name, cd in dir_ls:
          if i != dir:
              item = xbmcgui.ListItem(name)
              uri = sys.argv[0] + '?mode=lspg' \
              + '&url=' + urllib.quote_plus(url) \
              + '&gnrs=' + urllib.quote_plus(gnrs) \
              + '&ordr=' + urllib.quote_plus(ordr) \
              + '&dir=' + urllib.quote_plus(i) \
              + '&cook=' + urllib.quote_plus(cook)
              xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
              dbg_log('- uri:'+  uri + '\n')
          else:
              dirt = cd
              
      for cd, name in ord_ls:
          if cd != ordr:
              item = xbmcgui.ListItem(name)
              uri = sys.argv[0] + '?mode=lspg' \
              + '&url=' + urllib.quote_plus(url) \
              + '&gnrs=' + urllib.quote_plus(gnrs) \
              + '&ordr=' + urllib.quote_plus(cd) \
              + '&dir=' + urllib.quote_plus(dir) \
              + '&cook=' + urllib.quote_plus(cook)
              xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
              dbg_log('- uri:'+  uri + '\n')            
    
    if gnrs == '':
        item = xbmcgui.ListItem('<ЖАНР>')
        uri = sys.argv[0] + '?mode=gnpg' \
        + '&url=' + urllib.quote_plus(url) \
        + '&gnrs=' + urllib.quote_plus('0') \
        + '&ordr=' + urllib.quote_plus(ordr) \
        + '&dir=' + urllib.quote_plus(dir) \
        + '&cook=' + urllib.quote_plus(cook)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
        dbg_log('- uri:'+  uri + '\n')
    elif gnrs == '0':
        pass
    
    
    furl = url + list_pg
    if gnrs != '' and gnrs != '0':
        furl +=  '&genre=' + gnrs
    furl += '&order=' + ordr  + '&dir=' + dirt + '&offset=' + off + '&count=20' + '&PHPSESSID=' + cook
    dbg_log('- furl:'+  furl + '\n')
    http = get_url(furl, cookie = cook, referrer = rfr)

    lines = re.compile('{"ID":"(.*?)","Name":"(.*?)","OriginalName":"(.*?)","Year":"(.*?)",(.*?),"Poster":"(.*?)","SmallPoster":"(.*?)",').findall(http)

    for fid, fname, forgnm, fyear, ftrash, flogo, fslogo in lines:
        title = raw2uni(fname + ' (' + forgnm + ') ' + fyear)
        
        if flogo == '': tlogo = start_pg + re.sub('\\\/','/',fslogo)
        else: tlogo = start_pg + re.sub('\\\/','/',flogo)    
        
        logo = re.sub('smallposters','posters',tlogo)     

        item = xbmcgui.ListItem(raw2uni(title),iconImage=tlogo, thumbnailImage=logo)
        uri = sys.argv[0] + '?mode=plpg' \
        + '&url=' + urllib.quote_plus('film:'+fid) + \
        '&rfr=' + urllib.quote_plus(url) +'&cook=' + urllib.quote_plus(cook)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
        if dbg_gd: dbg_log('- uri:'+  uri + '\n')
    
    if len(lines) >= 20:
				item = xbmcgui.ListItem('<NEXT PAGE>')
				uri = sys.argv[0] + '?mode=lspg' \
				+ '&url=' + urllib.quote_plus(url)
				if gnrs != '' and gnrs != '0':
						uri +=  '&gnrs=' + gnrs
				uri += '&ordr=' + ordr \
				+ '&dir=' + dir \
				+ '&off=' + str(int(off) + 20) \
				+ '&cook=' + urllib.quote_plus(cook)

				xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
				dbg_log('- uri:'+  uri + '\n')

    xbmcplugin.endOfDirectory(pluginhandle)  

def SNB_gnpg(url, cook, rfr, ordr, dir, off, gnrs):     
    dbg_log('-SNB_gnpg:'+ '\n')
    
    furl = url + gnrs_pg + '&PHPSESSID=' + cook
    dbg_log('- furl:'+  furl + '\n')
    http = get_url(furl, cookie = cook, referrer = rfr)

    lines = re.compile('{"ID":"(.*?)","Name":"(.*?)","Count":"(.*?)"}').findall(http)

    for fid, fname, fcount in lines:
        if fid != '':
            title = raw2uni(fname + ' (' + fcount + ')')
            item = xbmcgui.ListItem(raw2uni(title))
            uri = sys.argv[0] + '?mode=lspg' \
            + '&url=' + urllib.quote_plus(url) \
            + '&gnrs=' + urllib.quote_plus(fid) \
            + '&ordr=' + urllib.quote_plus(ordr) \
            + '&dir=' + urllib.quote_plus(dir) \
            + '&cook=' + urllib.quote_plus(cook)
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
            dbg_log('- uri:'+  uri + '\n')

    xbmcplugin.endOfDirectory(pluginhandle)  

def SNB_play(url):     
    dbg_log('-SNB_play:'+ '\n')
    item = xbmcgui.ListItem(path = url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)


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
rfr = ''
mode=''
url=''
ordr='0'
dir='0'
off='0'
gnrs=''

try:
    mode=params['mode']
    dbg_log('-MODE:'+ mode + '\n')
except: pass
try: 
    cook=urllib.unquote_plus(params['cook'])
    dbg_log('-COOK:'+ cook + '\n')
except: pass
try: 
    rfr=urllib.unquote_plus(params['rfr'])
    dbg_log('-RFR:'+ rfr + '\n')
except: pass
try: 
    ordr=urllib.unquote_plus(params['ordr'])
    dbg_log('-ORDR:'+ ordr + '\n')
except: pass
try: 
    dir=urllib.unquote_plus(params['dir'])
    dbg_log('-DIR:'+ dir + '\n')
except: pass
try: 
    off=urllib.unquote_plus(params['off'])
    dbg_log('-OFF:'+ off + '\n')
except: pass    
try: 
    url=urllib.unquote_plus(params['url'])
    dbg_log('-URL:'+ url + '\n')
except: pass  
try: 
    gnrs=urllib.unquote_plus(params['gnrs'])
    dbg_log('-GNRS:'+ gnrs + '\n')
except: pass  


if mode == 'fdpg': SNB_fdpg(url, cook, rfr)
elif mode == 'lspg': SNB_lspg(url, cook, rfr, ordr, dir, off, gnrs)
elif mode == 'gnpg': SNB_gnpg(url, cook, rfr, ordr, dir, off, gnrs)
elif mode == 'plpg': SNB_plpg(url, cook, rfr)
elif mode == 'play': SNB_play(url)
elif mode == '': SNB_mnpg(start_pg)


