#!/usr/bin/python
# -*- coding: utf-8 -*-
# Writer (c) 2015, Silhouette, E-mail: 
# Rev. 0.6.2


import urllib,urllib2,re,sys
import xbmcplugin,xbmcgui,xbmcaddon
import urllib, urllib2, os, re, sys, json, cookielib
from BeautifulSoup import BeautifulSoup
import YDStreamExtractor





__settings__ = xbmcaddon.Addon(id='plugin.video.jevons.sx')
plugin_path = __settings__.getAddonInfo('path').replace(';', '')
plugin_icon = xbmc.translatePath(os.path.join(plugin_path, 'icon.png'))
context_path = xbmc.translatePath(os.path.join(plugin_path, 'default.py'))

rfpl_icon = xbmc.translatePath(os.path.join(plugin_path, 'rfpl.png'))
jevs_icon = xbmc.translatePath(os.path.join(plugin_path, 'jevs.png'))
pbtv_icon = xbmc.translatePath(os.path.join(plugin_path, 'pbtv.png'))

dbg = 0

pluginhandle = int(sys.argv[1])

start_pg = "http://jevons.ru"
page_pg = start_pg + "/category/futbol-obzori/page/"
mail_pg = "http://my.mail.ru/mail/jevons/video/"
vk_start = "https://vk.com"
vk_videos = "/videos-"
#vk_oid = '76470207'
# vk_pg = vk_start + "/videos-"+ vk_oid + "?section=playlists"
tvg_oid = '22893032'
gt_oid = '76470207'
vk_pg = vk_start + vk_videos #+ vk_oid
vk_alv = '/al_video.php'
rfpl_start = "http://rfpl.me"
rfpl_pg = rfpl_start + "/matche/page/"
pbtv_start = "http://www.pressball.by"
pbtv_pg = pbtv_start + "/tv/search/tag?ajax=yw0&q=222-pressbol-TV&TvVideo_page="
vk_vid = "/video-%s_%s"


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
    if dbg: xbmc.log(line)

def get_url(url, data = None, cookie = None, save_cookie = False, referrer = None):
    dbg_log('-get_url:' + '\n')
    dbg_log('- url:'+  url + '\n')
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

#     xbmcplugin.addDirectoryItem(pluginhandle, sys.argv[0] + '?mode=list&url=' + urllib.quote_plus(page_pg), xbmcgui.ListItem('JEVONS.ru', thumbnailImage=jevs_icon), True)
#    xbmcplugin.addDirectoryItem(pluginhandle, sys.argv[0] + '?mode=mail&url=' + urllib.quote_plus(mail_pg), xbmcgui.ListItem('< MAIL.RU >'), True)
#    xbmcplugin.addDirectoryItem(pluginhandle, sys.argv[0] + '?mode=vk&url=' + urllib.quote_plus(vk_pg), xbmcgui.ListItem('< VK.COM >'), True)
    xbmcplugin.addDirectoryItem(pluginhandle, sys.argv[0] + '?mode=vkalb&oid=' + gt_oid+ '&url=' + urllib.quote_plus(vk_pg + gt_oid), xbmcgui.ListItem('vk.com/GOALTIME', thumbnailImage=rfpl_icon), True)
    xbmcplugin.addDirectoryItem(pluginhandle, sys.argv[0] + '?mode=vkshow&oid=' + tvg_oid+ '&url=' + urllib.quote_plus(vk_videos + tvg_oid), xbmcgui.ListItem('vk.com/TVGOAL', thumbnailImage=rfpl_icon), True)
    xbmcplugin.addDirectoryItem(pluginhandle, sys.argv[0] + '?mode=pbtvtop', xbmcgui.ListItem('PRESSBALL.by', thumbnailImage=pbtv_icon), True)

     
    xbmcplugin.endOfDirectory(pluginhandle)

def JVS_vkalb(url, oid):
    dbg_log('-JVS_vkalb:' + '\n')
    dbg_log('- url:'+  url + '\n')
    
    http = get_url(url)
    ap = re.compile('{"albumsPreload":{(.*?):\[\[(.*?)\]\]}').findall(http)[0]
    entries = re.compile('\[(.*?),(.*?),(.*?),(.*?),(.*?),(.*?),(.*?)\]').findall('['+ap[1]+']')
    
    for en in entries: 
      title = en[0].decode('cp1251').encode('utf-8').strip('"').strip("'").replace('\/','/')
      img = en[2].strip('"').strip("'").replace('\/','/')
      href = en[3].strip('"').strip("'").replace('\/','/')
        
      if href != "":
        xbmcplugin.addDirectoryItem(pluginhandle, sys.argv[0] + '?mode=vkshow&oid=' + oid + '&url=' + urllib.quote_plus(href), xbmcgui.ListItem(title, thumbnailImage=img), True)

      dbg_log('- title:' + title + '\n')
      dbg_log('- img:'+  img + '\n')
      dbg_log('- href:'+  href + '\n')

    xbmcplugin.endOfDirectory(pluginhandle) 

def JVS_vkshow(url, page, oid):
    dbg_log('-JVS_vkshow:' + '\n')
    dbg_log('- url:'+  url + '\n')
    dbg_log('- page:'+  page + '\n')

    http = get_url(vk_start + url)
    
    try:
        sect = url.split('=')[1]
        pdata = 'act=load_videos_silent&al=1&extended=0&offset=0&oid=-' + oid + '&section=' + sect
        hpost = get_url(vk_start + vk_alv, data = pdata, referrer = vk_start + url)
        slist = "list"
    except:
        hpost = http
        slist = "list"

#    print hpost.replace('],[', '],\n[').decode('cp1251').encode('utf-8')
    dbg_log('- slist:'+  slist + '\n')
    if 1:
        pv = re.compile('"' + slist + '":\[\[(.*?)\]\]').findall(hpost)[0]
#        print pv.replace('],[', '],\n[').decode('cp1251').encode('utf-8')
        entries = re.compile('\[(.*?),(.*?),(.*?),(.*?),(.*?),(.*?),(.*?),(.*?),(.*?),(.*?),(.*?)\]').findall('['+pv+']')
        for entry in entries:
#             print entry
            try:
                ht = "/video-%s_%s"%(oid,entry[1])
                href = vk_start + ht
                title = entry[3].decode('cp1251').encode('utf-8').replace('\/', '/').strip('"')
                img = entry[2].replace('\/', '/').strip('"')
#                if entry[19].find('rutube') != -1: href = ''
            except:
                href = ''
                title = ''
                img = rfpl_icon
    
            dbg_log('-HREF %s'%href)
            dbg_log('-TITLE %s'%title)
            dbg_log('-IMG %s'%img)
    
            if href != '':
                item = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
                item.setInfo( type='video', infoLabels={'title': title, 'plot': title})
                uri = sys.argv[0] + '?mode=play' + '&url=' + urllib.quote_plus(href) + '&name=' + urllib.quote_plus(title)
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
                dbg_log('- uri:'+  uri + '\n')
    else:
        rinfos = BeautifulSoup(http).findAll('div',{"class":"video_row_info"})
    
        for rows in rinfos:
            row = BeautifulSoup(str(rows)).findAll('div',{"class":"video_row_info_name"})
    
    #         href = vk_start + re.compile('<a href="(.*?)"').findall(str(row))[0]
    #         title = re.compile('<a *?>(.*?)</a>').findall(str(row))[0].strip()
            try:
                ht = re.compile('<a href="(.*?)"(.*?)">(.*?)</a>').findall(str(row).replace('\n','').replace('\r',''))[0]
                href = vk_start + ht[0]
                title = ht[2].strip()
            except:
                href = ''
                title = ''
            img = rfpl_icon
    
            dbg_log('-HREF %s'%href)
            dbg_log('-TITLE %s'%title)
            dbg_log('-IMG %s'%img)
    
            if href != '':
                item = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
                item.setInfo( type='video', infoLabels={'title': title, 'plot': title})
                uri = sys.argv[0] + '?mode=play' + '&url=' + urllib.quote_plus(href) + '&name=' + urllib.quote_plus(title)
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(pluginhandle, uri, item, False)  
                dbg_log('- uri:'+  uri + '\n')

     
    xbmcplugin.endOfDirectory(pluginhandle) 
    
def JVS_list(url, page):
    dbg_log('-JVS_list:' + '\n')
    dbg_log('- url:'+  url + '\n')
    dbg_log('- page:'+  page + '\n')
    
    http = get_url(url + page + '/')

    i = 0

    entrys = re.compile(' <a title="(.*?)" href="(.*?)">').findall(http)

    for title, href in entrys:
        img = jevs_icon
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
        uri = sys.argv[0] + '?mode=list&page=' + str(int(page) + 1)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
        dbg_log('- uri:'+  uri + '\n')
        item = xbmcgui.ListItem('<NEXT PAGE +5>')
        uri = sys.argv[0] + '?mode=list&page=' + str(int(page) + 5)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
        dbg_log('- uri:'+  uri + '\n')        
     
    xbmcplugin.endOfDirectory(pluginhandle) 

def JVS_pbtvtop():
    dbg_log('-JVS_pbyvtop:' + '\n')
    
    pbtop = [   ("Прессбол-TV", "/tv/search/tag?q=222-pressbol-TV&TvVideo_page="),
                ("Футбол", "/tv/search/tag?q=41-futbol&TvVideo_page="),
                ("Чемпионат Беларуси", "/tv/search/tag?q=319-chempionat-belarusi&TvVideo_page="),
                ("Опять по пятницам", "/tv/search/tag?q=264-opyat'-po-pyatnicam&TvVideo_page="),
                ("На футболе", "/tv/streams/36?TvVideo_page="),
                ("Судите с нами", "/tv/search/tag?q=267-sudite-s-nami&TvVideo_page=") ] 

    for title, url in pbtop:
        xbmcplugin.addDirectoryItem(pluginhandle, sys.argv[0] + '?mode=pbtv&url=' + urllib.quote_plus(pbtv_start + url), xbmcgui.ListItem(title), True)
     
    xbmcplugin.endOfDirectory(pluginhandle)
        
def JVS_pbtv(url, page):
    dbg_log('-JVS_pbtv:' + '\n')
    dbg_log('- url:'+  url + '\n')
    dbg_log('- page:'+  page + '\n')
    
    
    http = get_url(url + page)
    
    i = 0

    panels = BeautifulSoup(http).findAll('div',{"class":"item"})
    
    for panel in panels:
#        print panel
        psoup = BeautifulSoup(str(panel))
        
        sref = str(panel).replace('\r','').replace('\n','')
#        print sref
        try:
            href = re.compile("href='(.*?)'").findall(sref)[0].strip()
        except:
            href = re.compile('href="(.*?)"').findall(sref)[0].strip()
#        href = str(psoup.a['href'])
        salt = str(psoup.img).replace('\r','').replace('\n','')
        try:
            title = re.compile("alt='(.*?)'").findall(salt)[0].strip()
        except:
            title = re.compile('alt="(.*?)"').findall(salt)[0].strip()
            
        img  = pbtv_start + str(psoup.img['src']).replace('\r','').replace('\n','').strip()

        if title != "":
            dbg_log('-HREF %s'%href)
            dbg_log('-IMG %s'%img)
            dbg_log('-TITLE %s'%title)
            
            item = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
            item.setInfo( type='video', infoLabels={'title': title, 'plot': title})
            uri = sys.argv[0] + '?mode=playpbtv' + '&url=' + urllib.quote_plus(href) + '&name=' + urllib.quote_plus(title)
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
            dbg_log('- uri:'+  uri + '\n')
            i = i + 1
    
    next = BeautifulSoup(http).findAll('li',{"class":"next"})

    if next :
        item = xbmcgui.ListItem('<NEXT PAGE>')
        uri = sys.argv[0] + '?page=' + str(int(page) + 1) + '&mode=pbtv&url=' + urllib.quote_plus(url)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
        dbg_log('- uri:'+  uri + '\n')
     
    xbmcplugin.endOfDirectory(pluginhandle)     

def get_rutube(url, videoId=None):
    dbg_log('-get_rutube:' + '\n')
    dbg_log('- url-in:'+  url + '\n')
    c = 0
    if not videoId:
        if 'rutube.ru' in url:
            try: videoId = re.findall('rutube.ru/play/embed/(.*?)"', url)[0]
            except:
                try: videoId = re.findall('rutube.ru/video/(.*?)/', url)[0]
                except: pass

    if videoId:    
        url = 'http://rutube.ru/api/play/options/'+videoId+'?format=json'
        dbg_log('- url-req:'+  url + '\n')
        request = urllib2.Request(url)
        request.add_header('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36')
        try:
            response = urllib2.urlopen(request)
            resp = response.read()
        except:
            pass
           

        jsonDict = json.loads(resp)
        link = urllib.quote_plus(jsonDict['video_balancer']['m3u8'])
           
        return link
    else: 
        return None
        
def get_rutube1(url):
        dbg_log('-get_rutube:' + '\n')
        dbg_log('- url-in:'+  url + '\n')
        if not videoID:
            if 'rutube.ru/play/embed/' in url:
                try: videoId = re.findall('rutube.ru/play/embed/(.*?)"', url)[0]
                except: pass
        if videoID:
            url = 'http://rutube.ru/api/play/options/'+videoId+'?format=json'
            request = urllib2.Request(url)
            request.add_header('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36')
            response = urllib2.urlopen(request)
            resp = response.read()
            jsonDict = json.loads(resp)
            link = urllib.quote_plus(jsonDict['video_balancer']['m3u8'])
            return link
        else: 
            return None
    
    
def get_rutube2(url):
    dbg_log('-get_rutube:' + '\n')
    if not url.startswith('http'): url = 'http:' + url
    dbg_log('- url-in:'+  url + '\n')
    result = get_url(url)
    jdata = urllib.unquote_plus(result).replace('&quot;','"').replace('&amp;','&')
    try: 
#         url = re.compile('"m3u8": "(.*?)"').findall(jdata)[0]
        url = re.compile('href="(.*?)"').findall(jdata)[0].replace('rutube.ru/', 'rutube.ru/api/')
        result = get_url(url)
#         print result
#         url = re.compile('rel="video_src" href="(.*?)"').findall(result)[0]
#         result = get_url(url)
        
#         <meta property="og:video" content="https://video.rutube.ru/8810316" />
#         <meta property="og:video:secure_url" content="https://video.rutube.ru/8810316" />
        try:
            url = re.compile('"og:video" content="(.*?)"').findall(result)[0]
        except:
            try:
                url = re.compile('"og:video:secure_url" content="(.*?)"').findall(result)[0]
            except:
                url = ''
                
                                
        dbg_log('- url-out:'+  url + '\n')
    except: url = None
    return url
        
def get_VK(url):
    dbg_log('-get_VK:' + '\n')
    dbg_log('- url:'+  url + '\n')
    
    html = get_url(url)

    rec = None
    
#     dbg_log("try-1")
#     try: rec = re.compile('var vk = {(.*?)};').findall(html.replace('\n',''))[0]
#     except: pass
#     
#     if rec == None:
#         dbg_log("try-2")
#         try: rec = re.compile('var vars = {(.*?)};').findall(html)[0]
#         except: pass
#         
#     if rec == None:
#         dbg_log("try-3")
#         try: rec = re.compile('var vars = {(.*?)};').findall(urllib.unquote_plus(html))[0]
#         except: pass
        
    if rec == None: 
        dbg_log("try-ajax")
        try: 
            ajax = re.compile('ajax.preload\((.*?)\]\);').findall(html)[0]
            dbg_log(ajax.replace('\/','/').replace('\\"','"'))
            iframe = re.compile('<iframe(.*?)/iframe>').findall(ajax)[0].replace('\/','/').replace('\\"','"')
            dbg_log(iframe)
            src = re.compile('src="(.*?)"').findall(iframe)[0]
            dbg_log(src)
        except:
            src = ''
        if src.find('rutube') > -1: 
                return get_rutube(src+'"');
        else:
            print 'Vk unknown external player'
            return None
    
    fv={}
    print rec
    
    for s in rec.split(','):
        
        print "S=%s"%s

        s0 = s.split(':',1)[0].replace('\\"', '"').strip('"')
        try:
            s1 = s.split(':',1)[1].replace('\\"', '"').strip('"')
        except:
            s1 = ''
        print "S0=%s"%s0
        print "S1=%s"%s1
        
        fv[s0] = s1
            
        if s0 == 'uid':
            uid = s1
        if s0 == 'vtag':
            vtag = s1
        if s0 == 'host':
            host = s1
        if s0 == 'vid':
            vid = s1
        if s0 == 'oid':
            oid = s1
        if s0 == 'hd':
            hd = s1
        if s0 == 'url240':
            url240 = s1
        if s0 == 'url360':
            url360 = s1
        if s0 == 'url480':
            url480 = s1
        if s0 == 'url720':
            url720 = s1

    url = url240
    qual = '240'
    if int(hd)==3:
        url = url720
        ual = '720'
    if int(hd)==2:
        url = url480
        ual = '480'
    if int(hd)==1:
        url = url360
        ual = '360'
    
    url = url.replace('\\', '')
    dbg_log('- nurl:'+  url + '\n')
#     surl = url.split('|')
#     print surl
    try:
        uri = 'http://vk.com/videostats.php?act=view&oid='+oid+'&vid='+vid+'&quality='+qual
        html = get_url(uri)
    except: pass

    if not url or not touch(url):
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

    dbg_log('- rurl:'+  url + '\n')
    return url


def get_YTD(url):
# import urlresolver
#     rurl = urlresolver.resolve(url)
#     return rurl

#     return 'https://cs9-1v4.vk.me/video/hls/p14/0c47dbcfedfd/index-f2-v1-a1.m3u8?extra=u_E-znf0xY2BHjn5njielmAohTD8JZ6l038lRNyfkTupdi83nejMhVfrv6xF0-pEYJ6duShxBfAzPXoaCJCKQJ-DlcnR07EC5yy8QwIUQRjOZTm_qmRQtalofgHHDGpq'

#     url= 'https://openload.co/embed/5VuUxHSVhug/'

#     import web_pdb; web_pdb.set_trace()
#     
#     url = 'https://vk.com/video-76470207_456252512'
#    import web_pdb; web_pdb.set_trace()
    vid = YDStreamExtractor.getVideoInfo(url,resolve_redirects=True)
    

    dbg_log('- YTD: \n')
    if vid:
        dbg_log('- YTD: Try\n')
        stream_url = vid.streamURL()
#         stream_url = vid.streamURL().split('|')[0]
        dbg_log('- surl:'+  stream_url + '\n')
        if stream_url.find('rutube') > -1:
            dbg_log('- rutube\n')
            streams = vid.streams()
#            dbg_log('- id1:'+str(streams)+'\n')
#            dbg_log('- id1:'+str(streams[0]['ytdl_format'])+'\n')
#            dbg_log('- id1:'+str(streams[0]['ytdl_format']['id'])+'\n')
            id = ''
            try: id = streams[0]['ytdl_format']['id']
            except: pass
            dbg_log('- id1:'+id+'\n')
            if id == '':
              try: id = streams[0]['ytdl_format']['webpage_url_basename'] 
              except: pass
            dbg_log('- id2:'+id+'\n')
            if id == '':
              try: id = streams[0]['ytdl_format']['display_id']
              except: pass
            dbg_log('- id3:'+id+'\n')
            if id != '': return get_rutube(url, id);
            else: return None
            
        return stream_url
    else: 
        dbg_log('- YTD: None\n')
        return None
    

def touch(url):
    req = urllib2.Request(url)
    try:
        res=urllib2.urlopen(req)
        res.close()
        return True
    except:
        return False            

def get_mailru(url):
#    try:
        url = url.replace('/my.mail.ru/video/', '/api.video.mail.ru/videos/embed/')
        url = url.replace('/my.mail.ru/mail/', '/api.video.mail.ru/videos/embed/mail/')
        url = url.replace('/videoapi.my.mail.ru/', '/api.video.mail.ru/')
        result = get_url(url)
#        print result
        url = re.compile('"metadataUrl" *: *"(.+?)"').findall(result)[0]
#        print url
        if not url.startswith('http'): url = 'http:' + url
        mycookie = get_url(url, save_cookie = True)
        cookie = re.search('<cookie>(.+?)</cookie>', mycookie).group(1)
        h = "|Cookie=%s" % urllib.quote(cookie)

        result = get_url(url)
#        print result
        result = json.loads(result)
        result = result['videos']
#        print result
        url = []
        url += [{'quality': '1080p', 'url': i['url'] + h} for i in result if i['key'] == '1080p']
        url += [{'quality': 'HD', 'url': i['url'] + h} for i in result if i['key'] == '720p']
        url += [{'quality': 'SD', 'url': i['url'] + h} for i in result if not (i['key'] == '1080p' or i ['key'] == '720p')]

        if url == []: return None
        return url
#    except:
        return None

def JVS_show(url, name):
    nurl = start_pg + url
    dbg_log('-JVS_show:' + '\n')
    dbg_log('- url:'+  nurl + '\n')
    
    http = get_url(nurl)

    entrys = re.compile('<iframe src="(.*?)"').findall(http)
    
    for href in entrys:
        img = jevs_icon
        dbg_log('-HREF %s'%href)
        
        if 'cityadspix' not in href:
            try:
                rsrc = re.compile('//(.*?)/').findall(href)
#                print rsrc
                lsrc = rsrc[0].split('.')
#                print lsrc
                lens = len(lsrc)
#                print lens
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
    dbg_log('- title:'+  title + '\n')
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
        uri = get_YTD(url)
        #uri = get_YTD(url)
    elif url.find('rutube') > -1:
        uri = get_rutube(url)
             
    if uri != None and uri != False:
        if not uri.startswith('http'): uri = 'http:' + uri
        uri = urllib.unquote_plus(uri)
        dbg_log('- uri: '+  uri + '\n')
        try: name = title[(title.find('~') + 1):]
        except: name = title
        item = xbmcgui.ListItem(path = uri)
        if 0:
            xbmcplugin.setResolvedUrl(pluginhandle, True, item)
        else:
            sPlayer = xbmc.Player()
            item.setInfo( type='Video', infoLabels={'title':name})
            item.setProperty('IsPlayable', 'true')
            sPlayer.play(uri, item)
        
def JVS_playpbtv(url, title):
    url = urllib.unquote_plus(url.replace('&amp;', '&'))
    if pbtv_start not in url:
        url = pbtv_start + url
    dbg_log('-JVS_playpbtv:'+ '\n')
    dbg_log('- url:'+  url + '\n')
    
    http = get_url(url)
    uri = pbtv_start + re.compile('file: "(.*?)"').findall(http)[0]
    
    dbg_log('- uri: '+  uri + '\n')
    name = title
    item = xbmcgui.ListItem(label=name, path = uri)
#    xbmcplugin.setResolvedUrl(pluginhandle, True, item)
    
    sPlayList   = xbmc.PlayList(xbmc.PLAYLIST_VIDEO) 
    sPlayer     = xbmc.Player()
    sPlayList.clear()
    item.setProperty('mimetype', 'video/x-msvideo')
    item.setProperty('IsPlayable', 'true')
    item.setInfo( type='video', infoLabels={'title': name})
    sPlayList.add(uri, item, 0)
    sPlayer.play(sPlayList)

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
oid = params['oid'] if 'oid' in params else ''
name = urllib.unquote_plus(params['name']) if 'name' in params else ''
url  = urllib.unquote_plus(params['url']) if 'url' in params else page_pg

if mode == '': JVS_top()
#if mode == '': JVS_list(url, page)
elif mode == 'list': JVS_list(url, page)
elif mode == 'vkalb': JVS_vkalb(url, oid)
elif mode == 'pbtvtop': JVS_pbtvtop()
elif mode == 'pbtv': JVS_pbtv(url, page)
elif mode == 'play': JVS_play(url, name)
elif mode == 'playpbtv': JVS_playpbtv(url, name)
elif mode == 'show': JVS_show(url, name)
elif mode == 'vkshow': JVS_vkshow(url, name, oid)
elif mode == 'mail': JVS_mail(url)
elif mode == 'vk': JVS_vk(url)

