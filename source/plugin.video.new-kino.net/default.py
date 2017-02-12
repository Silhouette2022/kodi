#!/usr/bin/python
# -*- coding: utf-8 -*-
# Writer (c) 2012, Silhouette, E-mail: 
# Rev. 0.10.2


import urllib, urllib2, os, re, sys, json, cookielib, base64
import xbmcplugin,xbmcgui,xbmcaddon
from BeautifulSoup import BeautifulSoup
import urllib, urllib2, os, re, sys, json, cookielib
import YDStreamExtractor

try:
  # Import UnifiedSearch
  sys.path.append(os.path.dirname(__file__)+ '/../plugin.video.unified.search')
  from unified_search import UnifiedSearch
except: pass

__settings__ = xbmcaddon.Addon(id='plugin.video.new-kino.net')
use_translit = __settings__.getSetting('translit')

try:  
  import Translit as translit
  translit = translit.Translit()  
except: use_translit = 'false'

dbg = 0

supported = {'vk.com', 'vkontakte.ru', 'kinolot.com', 'mail.ru', 'moonwalk.cc', 'moonwalk.co'}

pluginhandle = int(sys.argv[1])

start_pg = "http://new-kino.net/"
page_pg = "page/"
find_pg = "http://new-kino.net/?do=search&subaction=search&story="
search_start = "&search_start="

def gettranslit(msg):
    if use_translit == 'true': 
        return translit.rus(msg)
    else: return msg

def dbg_log(line):
    if dbg: xbmc.log(line)

def get_url(url, data = None, cookie = None, save_cookie = False, referrer = None, opts=None):
    dbg_log("get_url=>%s"%url)
    if data: dbg_log("get_data=>%s"%data)
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:42.0) Gecko/20100101 Firefox/42.0')
#     req.add_header('Accept', 'text/html, application/xml, application/xhtml+xml, */*')
    req.add_header('Accept', '*/*')
    req.add_header('Accept-Language', 'ru,en;q=0.9')
    if cookie: req.add_header('Cookie', cookie)
    if referrer: req.add_header('Referer', referrer)
    if opts:
        for x1, x2 in opts:
            req.add_header(x1, x2)

    if data: 
        response = urllib2.urlopen(req, data)
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
    unis_res = []
    unis_en = False
    
    if cook == "unis":
        cook = ""
        unis_en = True
    else:
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')#movies episodes tvshows    
              
    if url.find(find_pg) != -1:
        n_url = url + search_start + page
    else:
        n_url = url + page_pg + page + '/'
        
    dbg_log('- n_url:'+  n_url + '\n')
    horg = get_url(n_url, cookie = cook, save_cookie = True)
    if cook=='':
        cook = re.search('<cookie>(.+?)</cookie>', horg).group(1)
    i = 0
    
    if unis_en == False:
      for ctTitle, ctMode  in ext_ls:
        item = xbmcgui.ListItem(ctTitle)
        uri = sys.argv[0] + ctMode + '&cook=' + urllib.quote_plus(cook)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
        dbg_log('- uri:'+  uri + '\n')    
    

    http = re.sub('<br />', '', horg)
    hrefs = re.compile('<a href="(.*?)(#|">|" >)(.*?)</a></h4>').findall(http)
#     print http
    extras = re.compile('<h2><a href="(.*?)">(.*?)</a></h2>').findall(http)
    print extras

    if len(hrefs):
        news_id = re.compile("news-id-[0-9]")
        news = BeautifulSoup(http).findAll('div',{"id":news_id})
        
        if (len(hrefs) == len(news)):
            for sa in news:
#                 print str(sa)
                href = hrefs[i][0]
                dbg_log('-HREF %s'%href)
#                infos = re.compile('<img src="/(.*?)" alt="(.*?)" title="(.*?)" />(</a><!--TEnd--></div>|<!--dle_image_end-->)(.*?)<').findall(str(sa))
                infos = re.compile('<img src="/(.*?)" alt="(.*?)" title="(.*?)" />').findall(str(sa))
                plots = re.compile('</div>(.*?)</div>').findall(str(sa))
#                print infos
#                 print str(sa)
#                 for logo, alt, title, plot in infos:
                for logo, alt, title in infos:
                  img = start_pg + logo
                  dbg_log('-TITLE %s'%title)
                  try:
                      if title == '': 
                          title = extras[i][1].decode('cp1251').encode('utf-8').strip()
                          dbg_log('-EXTRAS %s'%title)
                  except: pass
                  dbg_log('-IMG %s'%img)
                  try: dbg_log('-PLOT %s'%plots[0])
                  except: dbg_log('-PLOT ')
                  
                  if unis_en == False:
                    item = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
                    try: item.setInfo( type='video', infoLabels={'title': title, 'plot': plots[0]})
                    except: item.setInfo( type='video', infoLabels={'title': title})
                    item.setArt({'thumb': img, 'poster': img})
#                     item.setArt({'thumb': img, 'poster': img, 'fanart': img})
                    uri = sys.argv[0] + '?mode=view' \
                    + '&url=' + urllib.quote_plus(href) + '&img=' + urllib.quote_plus(img) \
                     + '&name=' + urllib.quote_plus(title)+ '&cook=' + urllib.quote_plus(cook)
                    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
                    dbg_log('- uri:'+  uri + '\n')
                  else:
                    try: unis_res.append({'title':  title, 'url': href, 'image': img, 'plugin': 'plugin.video.new-kino.net'})
                    except: pass
                    
                  i = i + 1
    
    if unis_en == True:
      try: UnifiedSearch().collect(unis_res)
      except:  pass
    else:
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

def NKN_view(url, img, name, cook):     
    dbg_log('-NKN_view:'+ '\n')
    dbg_log('- url:'+  url + '\n')
    dbg_log('- img:'+  img + '\n')
    dbg_log('- name:'+  name + '\n')
        
    http = get_url(url, cookie = cook)

    frames = re.compile('<iframe (.*?)</iframe>').findall(http)
    if len(frames) > 0:
        

        i = 1
       
        wdic = { '' : 0}
        for frame in frames:
            files = re.compile('src="(.*?)"').findall(frame)

            for file in files:
                if 'facebook' not in file:

                    try: 
                        web = getSite(file)
                    except: 
                        web = ''
                        
                    dbg_log('- web:'+  str(web) + '\n')

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
                    
                    if 'http' not in file:
                        file = 'http:' + file 
                        
                    dbg_log('- file:'+  file + '\n')
        
                    item = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
                    uri = sys.argv[0] + '?mode=play' \
                    + '&name=' + urllib.quote_plus(name) \
                    + '&web=' + urllib.quote_plus(web) \
                    + '&ref=' + urllib.quote_plus(url) \
                    + '&url=' + urllib.quote_plus(file) + '&cook=' + urllib.quote_plus(cook)
                    item.setProperty('IsPlayable', 'true')
                    xbmcplugin.addDirectoryItem(pluginhandle, uri, item)  
                    dbg_log('- uri:'+  uri + '\n')

        xbmcplugin.endOfDirectory(pluginhandle)


def Decode2(param):
        try:
            hk = ("0123456789WGXMHRUZID=NQVBLihbzaclmepsJxdftioYkngryTwuvihv7ec41D6GpBtXx3QJRiN5WwMf=ihngU08IuldVHosTmZz9kYL2bayE").split('ih')
            hash_key = hk[0]+'\n'+hk[1]

            #-- define variables
            loc_3 = [0,0,0,0]
            loc_4 = [0,0,0]
            loc_2 = ''

            #-- define hash parameters for decoding
            dec = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
            hash1 = hash_key.split('\n')[0]
            hash2 = hash_key.split('\n')[1]

            #-- decode
            for i in range(0, len(hash1)):
                re1 = hash1[i]
                re2 = hash2[i]

                param = param.replace(re1, '___')
                param = param.replace(re2, re1)
                param = param.replace('___', re2)

            i = 0
            while i < len(param):
                j = 0
                while j < 4 and i+j < len(param):
                    loc_3[j] = dec.find(param[i+j])
                    j = j + 1

                loc_4[0] = (loc_3[0] << 2) + ((loc_3[1] & 48) >> 4);
                loc_4[1] = ((loc_3[1] & 15) << 4) + ((loc_3[2] & 60) >> 2);
                loc_4[2] = ((loc_3[2] & 3) << 6) + loc_3[3];

                j = 0
                while j < 3:
                    if loc_3[j + 1] == 64 or loc_4[j] == 0:
                        break

                    loc_2 += unichr(loc_4[j])

                    j = j + 1
                i = i + 4;
        except:
            loc_2 = ''

        return loc_2

def DecodeUppodText2(sData):
  hash = "0123456789WGXMHRUZID=NQVBLihbzaclmepsJxdftioYkngryTwuvihv7ec41D6GpBtXx3QJRiN5WwMf=ihngU08IuldVHosTmZz9kYL2bayE"

#  Проверяем, может не нужно раскодировать (json или ссылка)
#  if ((Pos("{", sData)>0) || (LeftCopy(sData, 4)=="http")) return HmsUtf8Decode(sData);

  sData = DecodeUppod_tr(sData, "r", "A")
  
  hash = hash.replace('ih', '\n')
  if sData[-1] == '!' :
    sData = sData[:len(sData)-1]
    tab_a = hash.split('\n')[3]
    tab_b = hash.split('\n')[2]
  else:
    tab_a = hash.split('\n')[1]
    tab_b = hash.split('\n')[0]

  sData = sData.replace("\n", "")
  
  for i in range(1, len(tab_a)):
    char1 = tab_b[i]
    char2 = tab_a[i]
    sData = sData.replace(char1, "___")
    sData = sData.replace(char2, char1)
    sData = sData.replace("___", char2)

  sData = DecodeUppod_Base64(sData)
  sData = sData.replace("hthp:", "http:")
  return sData

def DecodeUppod_tr(sData, ch1, ch2):
  s = ""
  if (sData[len(sData)-1] == ch1) and (sData[3] == ch2):
    nLen = len(sData);
    for i in range(nLen, 1, -1): s += sData[i]
    loc3 = Int(Int(s[nLen-1:nLen])/2)
    s = s[3, nLen-2]
    i = loc3
    if loc3 < len(s):
      while (i < len(s)):
        s = s[:i] + s[i+2:]
        i+= loc3
    sData = s + "!"

  return sData
  
  
def DecodeUppod_Base64(param):
    #-- define variables
    loc_3 = [0,0,0,0]
    loc_4 = [0,0,0]
    loc_2 = ''
    #-- define hash parameters for decoding
    dec = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
    i = 0
    while i < len(param):
        j = 0
        while j < 4 and i+j < len(param):
            loc_3[j] = dec.find(param[i+j])
            j = j + 1

        loc_4[0] = (loc_3[0] << 2) + ((loc_3[1] & 48) >> 4);
        loc_4[1] = ((loc_3[1] & 15) << 4) + ((loc_3[2] & 60) >> 2);
        loc_4[2] = ((loc_3[2] & 3) << 6) + loc_3[3];

        j = 0
        while j < 3:
            if loc_3[j + 1] == 64: break
            loc_2 += unichr(loc_4[j])
            j = j + 1
        i = i + 4

    return loc_2        

def get_VK(url):
    dbg_log('-get_VK:' + '\n')
    html = get_url(url)
    dbg_log('- url:'+  url + '\n')
#    url = None
    rec = None
    try: rec = re.compile('var vars = {(.*?)};').findall(html)[0]
    except: pass
        
    if rec == None:
        try: rec = re.compile('var vars = {(.*?)};').findall(urllib.unquote_plus(html))[0]
        except: pass
        
    if rec == None: return
    
    fv={}
    
    for s in rec.split(','):
        
#         print "S=%s"%s

        s0 = s.split(':',1)[0].replace('\\"', '"').strip('"')
        try:
            s1 = s.split(':',1)[1].replace('\\"', '"').strip('"')
        except:
            s1 = ''
#         print "S0=%s"%s0
#         print "S1=%s"%s1
        
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

   
def get_VK1(url):
    html = get_url(url)
#    url = None
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
            if s.split('=',1)[0] == 'url240':
                url240 = s.split('=',1)[1]
            if s.split('=',1)[0] == 'url360':
                url360 = s.split('=',1)[1]
            if s.split('=',1)[0] == 'url480':
                url480 = s.split('=',1)[1]
            if s.split('=',1)[0] == 'url720':
                url720 = s.split('=',1)[1]

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

    return url

def touch(url):
    req = urllib2.Request(url)
    try:
        res=urllib2.urlopen(req)
        res.close()
        return True
    except:
        return False
    
def get_YTD(url):
    vid = YDStreamExtractor.getVideoInfo(url,resolve_redirects=True)
    dbg_log('- YTD: \n')
    if vid:
        dbg_log('- YTD: Try\n')
        stream_url = vid.streamURL()
#         stream_url = vid.streamURL().split('|')[0]
        dbg_log('- surl:'+  stream_url + '\n')

    else: 
        dbg_log('- YTD: None\n')
        return None
              
        
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


   
def get_moonwalk(url, ref, cook):
        
#    token=re.findall('http://moonwalk.cc/video/(.+?)/',url)[0]
    page = get_url(url, referrer=ref, cookie = cook)
#    xbmc.log(page)

#    video_token: 'f956e26b0ffe0ab9',
#                                                content_type: 'movie',
#                                                mw_key: '1152cb1dd4c4d544',
#                                                mw_pid: 537,
#                                                mw_domain_id: 13338,
#                                                ad_attr: condition_detected ? 1 : 0,
#                                                debug: false,
#                                                uuid: '9ee940f4080aa1c9d4815cab11bd7a42'
                                                
    
#    vtoken = re.findall("video_token: '(.*?)'", page)[0]
#    did = re.findall("d_id: (.*?),", page)[0]
#    ctype = re.findall("content_type: '(.*?)'", page)[0]
#    akey = re.findall("access_key: '(.*?)'", page)[0]
    csrf = re.findall('name="csrf-token" content="(.*?)"', page)[0]
#    bdata = base64.b64encode(re.findall('\|setRequestHeader\|(.*?)\|', page)[0])

    vtoken = re.findall("video_token: '(.*?)'", page)[0]
    ctype = re.findall("content_type: '(.*?)'", page)[0]
    mw_key = re.findall("mw_key: '(.*?)'", page)[0]
    mw_pid = re.findall("mw_pid: (.*?),", page)[0]
    p_domain_id = re.findall("p_domain_id: (.*?),", page)[0]
#    uuid = re.findall("uuid: '(.*?)'", page)[0]
    csafe = re.findall("condition_safe = '(.*?)'", page)[0]
#condition_safe = 'ed064acb78fd5dd9'
        
    
    opts = []
    opts.append(('Accept-Encoding', 'gzip, deflate'))
    opts.append(('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8'))
    opts.append(('X-CSRF-Token', csrf))
    opts.append(('X-Condition-Safe', 'Normal'))
#    opts.append(('X-Iframe-Option', 'Direct'))
    opts.append(('X-Requested-With', 'XMLHttpRequest'))
#    udata = 'partner=&d_id=%s&video_token=%s&content_type=%s&access_key=%s&cd=0'%(did, vtoken, ctype, akey)
    udata = 'video_token=%s&content_type=%s&mw_key=%s&mw_pid=%s&p_domain_id=%s&ad_atr=0&debug=false&condition_safe=%s'%(vtoken, ctype, mw_key, mw_pid, p_domain_id, csafe)


    html = get_url('http://moonwalk.cc/sessions/new_session', 
                   data=udata, 
                   referrer=url,
                   cookie=cook,
#                    cookie='_moon_session=NFdHdDBUWmQvUVpvdTk4N0xuVzlkTEdiekhva3NBRDJCQzVYN2JwVzJjenhtZG5jUW45ck9GRUpXMVdjMGhKSVBCdUhPN0NBVHZQSnkrVDFoSHRjME1pL1BKNS85RGpIN1lrbGFRbUFXYlNxcTFZNk8rNnlmcXpvTkl0blByTzREV0d4ZXVwOTMzZHd5emJMMUhTU2ZCVGVtNTV4bG1tTUljYUVGOFJVY2JtUEFLK2NucTQ1eWRwMlE4VFd4VGNrLS1EQjdFcDNxMGhNdlJPUUxuTzhaMzlnPT0%3D--0d2dafceaa11be80d5e17b5f9a657bbfcb0e1b29', 
                   opts=opts)
#    xbmc.log(html)    
    page=json.loads(html)
    xbmc.log(str(page))
    url = page["mans"]["manifest_m3u8"]
    return url   

def NKN_play(url, cook, name, web, ref):
    dbg_log('-NKN_play:'+ '\n')
    dbg_log('- url:'+  url.replace('&amp;', '&') + '\n')
    url = url.replace('&amp;', '&')
    furls = []

    if 'kinolot.com' in web:
        http = get_url(url, cookie = cook)
        files = re.compile('file=(.*?)&').findall(http)
        if len(files):
            furls.append(Decode2(Decode2(urllib.unquote_plus(files[0]))))
    elif 'vk.com' in web:
        furl = get_YTD(url)
        if furl != None: furls.append(furl)
        else:  dbg_log('VK : no url returned')
    elif 'vkontakte.ru' in web:
        furl = get_YTD(url)
        if furl != None: furls.append(furl)
        else:  dbg_log('VK : no url returned')
    elif 'mail.ru' in web:
        quals = get_mailru(url)
        try:        
          for d in quals: 
            if d['quality'] == 'HD' : 
                furls.append(d['url'])
                break
            if d['quality'] == '1080p' : 
                furls.append(d['url'])
                break
            if d['quality'] == 'SD' : 
                furls.append(d['url'])
                break
        except: pass
    elif 'moonwalk.c' in web or web[0].isdigit():
        furl = get_moonwalk(url.replace('.co','.cc'), ref, cook)
        if furl != None: furls.append(furl)
        else:  dbg_log('Moonwalk : no url returned')
    
    if len(furls) == 0:
        furl = get_YTD(url)
        if furl != None: furls.append(furl)
        else:  dbg_log('OTHER : no url returned')        
        
    if len(furls) == 1:
        dbg_log('- furl:'+  furls[0] + '\n')
        item = xbmcgui.ListItem(path = furls[0])
        xbmcplugin.setResolvedUrl(pluginhandle, True, item)
    elif len(furls):
        sPlayList   = xbmc.PlayList(xbmc.PLAYLIST_VIDEO) 
        sPlayer     = xbmc.Player()
        sPlayList.clear()
        runRes = False
        for furl in furls:
            item = xbmcgui.ListItem(name, path = furl)
            item.setProperty('mimetype', 'video/x-msvideo')
            item.setProperty('IsPlayable', 'true')
            sPlayList.add(furl, item) #, 0) 
            if not runRes: 
                xbmcplugin.setResolvedUrl(pluginhandle, True, item)
                runRes = True
        sPlayer.play(sPlayList)
         

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
web = ''
ref = ''

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
try: 
    web=urllib.unquote_plus(params['web'])
    dbg_log('-WEB:'+ web + '\n')
except: pass
try: 
    ref=urllib.unquote_plus(params['ref'])
    dbg_log('-REF:'+ ref + '\n')
except: pass

keyword = params['keyword'] if 'keyword' in params else None
unified = params['unified'] if 'unified' in params else None

if url=='':
    url = start_pg

if mode == '': NKN_start(url, page, cook)
elif mode == 'ctlg': NKN_ctlg(url, cook)
elif mode == 'view': NKN_view(url, imag, name, cook)
elif mode == 'play': NKN_play(url, cook, name, web, ref)
elif mode == 'find': NKN_find(cook)
elif mode == 'show': NKN_view(url, imag, "Play Video", cook)
elif mode == 'search': 
    url = find_pg + uni2cp(gettranslit(keyword))
    NKN_start(url, '1', 'unis')



