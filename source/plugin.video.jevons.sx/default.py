#!/usr/bin/python
# -*- coding: utf-8 -*-
# Writer (c) 2015, Silhouette, E-mail: 
# Rev. 0.1.1


import urllib,urllib2,re,sys
import xbmcplugin,xbmcgui,xbmcaddon
import urllib, urllib2, os, re, sys, json, cookielib
from BeautifulSoup import BeautifulSoup


__settings__ = xbmcaddon.Addon(id='plugin.video.jevons.sx')
plugin_path = __settings__.getAddonInfo('path').replace(';', '')
plugin_icon = xbmc.translatePath(os.path.join(plugin_path, 'icon.png'))
context_path = xbmc.translatePath(os.path.join(plugin_path, 'default.py'))

dbg = 0

pluginhandle = int(sys.argv[1])

start_pg = "http://www.jevons.ru"
page_pg = start_pg + "/reviews/"
mail_pg = "http://my.mail.ru/mail/jevons/video/"
vk_start = "http://vk.com"
vk_pg = vk_start + "/videos270805795"

def reportUsage(addonid,action):
    host = 'xbmc-doplnky.googlecode.com'
    tc = 'UA-3971432-4'
    try:
        utmain.main({'id':addonid,'host':host,'tc':tc,'action':action})
    except:
        pass  
         
def resolve(self,url):
	result = xbmcprovider.XBMCMultiResolverContentProvider.resolve(self,url)
	if result:
		# ping befun.cz GA account
		host = 'befun.cz'
		tc = 'UA-35173050-1'
		try:
			utmain.main({'id':__scriptid__,'host':host,'tc':tc,'action':url})
		except:
			print 'Error sending ping to GA'
			traceback.print_exc()
	return result
                

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

def JVS_top():
    dbg_log('-JVS_top:' + '\n')

    xbmcplugin.addDirectoryItem(pluginhandle, sys.argv[0] + '?mode=list&url=' + urllib.quote_plus(page_pg), xbmcgui.ListItem('< WEB >'), True)
    xbmcplugin.addDirectoryItem(pluginhandle, sys.argv[0] + '?mode=mail&url=' + urllib.quote_plus(mail_pg), xbmcgui.ListItem('< MAIL.RU >'), True)
    xbmcplugin.addDirectoryItem(pluginhandle, sys.argv[0] + '?mode=vk&url=' + urllib.quote_plus(vk_pg), xbmcgui.ListItem('< VK.COM >'), True)
     
    xbmcplugin.endOfDirectory(pluginhandle)

def JVS_vk(url):
    dbg_log('-JVS_vk:' + '\n')
    dbg_log('- url:'+  url + '\n')
    
    http = get_url(url)
    
    thumb = BeautifulSoup(http).findAll('div',{"class":"video_row_thumb"})
    info = BeautifulSoup(http).findAll('div',{"class":"video_row_info"}) 
    
    drt = {}
    dri = []
    for t in thumb: 
      try:
        drt[t.a['href']] = re.compile("background-image: url\(\'(.*?)\'\);").findall(t.div['style'])[0]
      except:
        drt[t.a['href']] = ""

    for i in info:
        dri.append((i.a['href'], i.a.string.strip().encode('utf8')))
        
    print drt
    print dri
    for href, title in dri:
        img = drt[href]
        dbg_log('-HREF %s'%href)
        dbg_log('-TITLE %s'%title)
        dbg_log('-IMG %s'%img)

        item = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
        item.setInfo( type='video', infoLabels={'title': title, 'plot': title})
        uri = sys.argv[0] + '?mode=play' + '&url=' + urllib.quote_plus(vk_start + href) + '&name=' + urllib.quote_plus(title)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
        dbg_log('- uri:'+  uri + '\n')

    xbmcplugin.endOfDirectory(pluginhandle) 

def JVS_list(url, page):
    dbg_log('-JVS_list:' + '\n')
    dbg_log('- url:'+  url + '\n')
    dbg_log('- page:'+  page + '\n')
    
    http = get_url(url + page)
    
    i = 0

    entrys = re.compile(' <a title="(.*?)" href="(.*?)">').findall(http)

    for title, href in entrys:
        img = plugin_icon
        dbg_log('-HREF %s'%href)
        dbg_log('-TITLE %s'%title)
        dbg_log('-IMG %s'%img)

        item = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
        item.setInfo( type='video', infoLabels={'title': title, 'plot': title})
        uri = sys.argv[0] + '?mode=show' + '&url=' + urllib.quote_plus(href) + '&name=' + urllib.quote_plus(title)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
        dbg_log('- uri:'+  uri + '\n')
        i = i + 1

    if i :
        item = xbmcgui.ListItem('<NEXT PAGE>')
        uri = sys.argv[0] + '?page=' + str(int(page) + 1)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
        dbg_log('- uri:'+  uri + '\n')
        item = xbmcgui.ListItem('<NEXT PAGE +5>')
        uri = sys.argv[0] + '?page=' + str(int(page) + 5)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
        dbg_log('- uri:'+  uri + '\n')        
     
    xbmcplugin.endOfDirectory(pluginhandle) 
    
def get_VK(url):
    html = get_url(url)
    soup = BeautifulSoup(html, fromEncoding="utf-8")
    
    recs = soup.findAll('param', {'name':'flashvars'})

    for rec in recs:
        fv={}
        for s in rec['value'].split('&'):
            sdd=s.split('=',1)
            try:
                fv[sdd[0]]=sdd[1]
            except:
                fv[sdd[0]]=''
            if s.split('=',1)[0] == 'uid':
                uid = s.split('=',1)[1]
            if s.split('=',1)[0] == 'vtag':
                vtag = s.split('=',1)[1]
            if s.split('=',1)[0] == 'host':
                host = s.split('=',1)[1]
            if s.split('=',1)[0] == 'vid':
                vid = s.split('=',1)[1]
            if s.split('=',1)[0] == 'oid':
                oid = s.split('=',1)[1]
            if s.split('=',1)[0] == 'hd':
                hd = s.split('=',1)[1]
        url = host+'u'+uid+'/videos/'+vtag+'.240.mp4'
        if int(hd)==3:
            url = host+'u'+uid+'/videos/'+vtag+'.720.mp4'
        if int(hd)==2:
            url = host+'u'+uid+'/videos/'+vtag+'.480.mp4'
        if int(hd)==1:
            url = host+'u'+uid+'/videos/'+vtag+'.360.mp4'
    if not touch(url):
        try:
            if int(hd)==3:
                url = fv['cache720']
            if int(hd)==2:
                url = fv['cache480']
            if int(hd)==1:
                url = fv['cache360']
        except:
            print 'Vk parser failed'
            return None
    return url

def touch(url):
    req = urllib2.Request(url)
    try:
        res=urllib2.urlopen(req)
        res.close()
        return True
    except:
        return False            

def get_mailru(url):
    try:
        url = url.replace('/my.mail.ru/video/', '/api.video.mail.ru/videos/embed/')
        url = url.replace('/my.mail.ru/mail/', '/api.video.mail.ru/videos/embed/mail/')
        url = url.replace('/videoapi.my.mail.ru/', '/api.video.mail.ru/')
        result = get_url(url)

        url = re.compile('"metadataUrl" *: *"(.+?)"').findall(result)[0]
        mycookie = get_url(url, save_cookie = True)
        cookie = re.search('<cookie>(.+?)</cookie>', mycookie).group(1)
        h = "|Cookie=%s" % urllib.quote(cookie)

        result = get_url(url)
        result = json.loads(result)
        result = result['videos']

        url = []
        url += [{'quality': '1080p', 'url': i['url'] + h} for i in result if i['key'] == '1080p']
        url += [{'quality': 'HD', 'url': i['url'] + h} for i in result if i['key'] == '720p']
        url += [{'quality': 'SD', 'url': i['url'] + h} for i in result if not (i['key'] == '1080p' or i ['key'] == '720p')]

        if url == []: return None
        return url
    except:
        return None

def JVS_show(url, name):
    nurl = start_pg + url
    dbg_log('-JVS_show:' + '\n')
    dbg_log('- url:'+  nurl + '\n')
    
    http = get_url(nurl)

    entrys = re.compile('<iframe src="(.*?)"').findall(http)
    
    for href in entrys:
        img = plugin_icon
        dbg_log('-HREF %s'%href)
        
        try:
            rsrc = re.compile('//(.*?)/').findall(href)
            print rsrc
            lsrc = rsrc[0].split('.')
            print lsrc
            lens = len(lsrc)
            print lens
            if lens > 1: title = '[%s.%s]~%s'%(lsrc[lens - 2], lsrc[lens -1], name)
            else: title = name
        except: title = name

        if 'http' not in href: href = 'http:' + href 
        item = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
        item.setInfo( type='video', infoLabels={'title': title, 'plot': title})
        uri = sys.argv[0] + '?mode=play' + '&url=' + urllib.quote_plus(href) + '&name=' + urllib.quote_plus(title)
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, False)  
        dbg_log('- uri:'+  uri + '\n')

    xbmcplugin.endOfDirectory(pluginhandle) 
  
def JVS_play(url, title):
    url = url.replace('&amp;', '&')
        
    dbg_log('-JVS_play:'+ '\n')
    dbg_log('- url:'+  url + '\n')
    uri = None
        
    if url.find('videoapi.my.mail.ru') > -1:
        quals = get_mailru(url)
        for d in quals: 
          try:
            if d['quality'] == 'HD' : 
                uri = d['url']
                break
            if d['quality'] == '1080p' : 
                uri = d['url']
                break
            if d['quality'] == 'SD' : 
                uri = d['url']
                break
          except: pass
        
    elif url.find('vkontakte.ru') > -1:
        uri = get_VK(url)
    elif url.find('vk.com') > -1:
        uri = get_VK(url)     
    
    if uri != None:
        uri = urllib.unquote_plus(uri)
        dbg_log('- uri: '+  uri + '\n')
        try: name = title[(title.find('~') + 1):]
        except: name = title
        item = xbmcgui.ListItem(label=name, path = uri)
        xbmcplugin.setResolvedUrl(pluginhandle, True, item)

def uni2enc(ustr):
    raw = ''
    uni = unicode(ustr, 'utf8')
    uni_sz = len(uni)
    for i in xrange(len(ustr)):
        raw += ('%%%02X') % ord(ustr[i])        
    return raw


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
mode = params['mode'] if 'mode' in params else ''
page = params['page'] if 'page' in params else '1'
name = urllib.unquote_plus(params['name']) if 'name' in params else ''
url  = urllib.unquote_plus(params['url']) if 'url' in params else page_pg

#if mode == '': JVS_top()
if mode == '': JVS_list(url, page)
elif mode == 'list': JVS_list(url, page)
elif mode == 'mail': JVS_mail(url)
elif mode == 'vk': JVS_vk(url)
elif mode == 'play': JVS_play(url, name)
elif mode == 'show': JVS_show(url, name)


