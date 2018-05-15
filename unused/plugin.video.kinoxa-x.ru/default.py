#!/usr/bin/python
# -*- coding: utf-8 -*-
# Writer (c) 2013, Silhouette, E-mail: 
# Rev. 0.7.8


import urllib,urllib2, os, re,sys, json,cookielib, base64, socket
import xbmcplugin,xbmcgui,xbmcaddon
from BeautifulSoup import BeautifulSoup
import requests

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

socket.setdefaulttimeout(120)

QUALITY_TYPES = (360, 480, 720, 1080)

pluginhandle = int(sys.argv[1])

start_pg = "http://kinoxa-x.net"
#page_pg = start_pg + "/load/0-"
page_pg = start_pg + "/page/"
# fdpg_pg = ";t=0;md=;p="
# find_pg = start_pg + "/search/?q="
find_pg = start_pg + "/index.php?do=search"
# find_dt = "titleonly=3&do=search&subaction=search"
# find_ss = "&search_start="
# find_rs = "&full_search=0&result_from="
# find_str = "&story="


def gettranslit(msg):
    if use_translit == 'true': 
        try: return translit.rus(msg)
        except: return msg
    else: return msg
    

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

def KNX_list(url, page, type, fdata, cook):
    dbg_log('-KNX_list:' + '\n')
    dbg_log('- url:'+  url + '\n')
    dbg_log('- page:'+  page + '\n')
    dbg_log('- type:'+  type + '\n')
    dbg_log('- fdata:'+  fdata + '\n')
    
    
  
    if type == 'ctlg':
        n_url = url + 'page/' + page + '/'
        pdata = None
    elif fdata != '':
        
        dfind_ss = 'search_start'
        dfind_str = 'story'
        dfind_rs = 'result_from'
    
        dfind = {'titleonly' : '3',
                 'do' : 'search',
                 'subaction' : 'search',
                 'full_search' : '0'
                 }

        pdata = {}
        n_url = url
        pdata.update(dfind)
        pdata[dfind_ss] = page
        pdata[dfind_rs] = str(((int(page) - 1) * 12) + 1)
        pdata[dfind_str] = fdata

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
        entrys = BeautifulSoup(http).findAll('table',{"class":"eBlock"})
    else:        
        entrys = BeautifulSoup(http).findAll('section',{"class":"short_video_view"})

    for eid in entrys:

        if type == 'find' or type == 'unis' or type == 'unds':
#             xbmc.log(str(eid))
            hrtt = re.compile('<a href="(.*?)">(.*?)</a>').findall(str(eid))[0]
            href = hrtt[0]
            title = hrtt[1] 
            plot = ''
            try: img = start_pg + re.compile('<img src="(.*?)"').findall(re.sub('\thumbs', '',str(eid)))[0]
            except: img = ''
        else:
            href = re.compile('<a href="(.*?)"><h3').findall(str(eid))[0]
            plots = BeautifulSoup(str(eid)).findAll('td',{"class":"short_rewiev"})
#            print plots            
            try:
                plot = re.compile('<div>(.*?)</div>').findall(re.sub('[\n\r\t]', ' ',str(plots[0])))[0]
            except:
                plot = ''
            try:
                img = start_pg + re.compile('<img src="(.*?)"').findall(re.sub('\thumbs', '',str(eid)))[0]
            except:
                img = ''
            try:
                title = re.compile('<h3 class="title_film">(.*?)</h3>').findall(str(eid))[0]
            except:
                title = re.compile('title="(.*?)"').findall(str(eid))[0]
                


        dbg_log('-HREF %s'%href)
        dbg_log('-TITLE %s'%title)
        dbg_log('-IMG %s'%img)
        dbg_log('-PLOT %s'%plot)

        if type != 'unis':
            item = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
            item.setInfo( type='video', infoLabels={'title': title, 'plot': plot})
            uri = sys.argv[0] + '?mode=play' \
            + '&url=' + urllib.quote_plus(href)
            if type != 'unds': uri += '&cook=' + json.dumps(req.cookies.get_dict())
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, False)  
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


def KNX_show(url):
    dbg_log('-KNX_show:' + '\n')
    dbg_log('- url:'+  url + '\n')
    
    item = xbmcgui.ListItem('Play Video')
    uri = sys.argv[0] + '?mode=play&url=' + urllib.quote_plus(url)
    item.setProperty('IsPlayable', 'true')
    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, False)  
    dbg_log('- uri:'+  uri + '\n')
    xbmcplugin.endOfDirectory(pluginhandle)
    
     
def get_video_link_from_iframe(url, mainurl):
    
    from videohosts import moonwalk

    playlist_domain = 'streamblast.cc'
    playlist_domain2 = 's4.cdnapponline.com'

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
#            "Referer": mainurl
        "Referer": "http://www.random.org"
    }
    request = urllib2.Request(url, "", headers)
    request.get_method = lambda: 'GET'
    response = urllib2.urlopen(request).read()

    subtitles = None
    if 'subtitles: {"master_vtt":"' in response:
        subtitles = response.split('subtitles: {"master_vtt":"')[-1].split('"')[0]

    ###################################################
    values, attrs = moonwalk.get_access_attrs(response)
    ###################################################

    headers = {
        "Host": playlist_domain2,
        "Origin": "http://" + playlist_domain2,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
        "Referer": url,
        "X-Requested-With": "XMLHttpRequest"
    }
    headers.update(attrs)

    request = urllib2.Request('http://' + playlist_domain2 + attrs["purl"], urllib.urlencode(values), headers)
    response = urllib2.urlopen(request).read()
    data = json.loads(response.decode('unicode-escape'))
    playlisturl = data['mans']['manifest_m3u8']

    headers = {
        "Host": playlist_domain2,
        "Referer": url,
        "Origin": "http://" + playlist_domain2,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }

    request = urllib2.Request(playlisturl, "", headers)
    request.get_method = lambda: 'GET'
    response = urllib2.urlopen(request).read()

    urls = re.compile("http:\/\/.*?\n").findall(response)
    manifest_links = {}
    for i, url in enumerate(urls):
        manifest_links[QUALITY_TYPES[i]] = url.replace("\n", "")

    return manifest_links, subtitles
    
def get_moonwalk(url, ref, cook):
    links, subtitles = get_video_link_from_iframe(url, ref)
    xbmc.log(str(links))
    r0 = [str(x) for x in links.keys()]
    dbg_log('- r0:'+  str(r0) + '\n')
    i = xbmcgui.Dialog().select('Video Quality', r0)
    
    return links[int(r0[i])]

def get_moonwalk2(url, ref, cook):
    dbg_log('-get_moonwalk:' + '\n')
    dbg_log('- url:'+  url + '\n')
    dbg_log('- ref:'+  ref + '\n')
    dbg_log('- cook:'+  str(cook) + '\n')
    req = req_url(url, opts = {'Referer' : ref}, cookies=cook)
    page = req.content
    
#     xbmc.log(page)
    try: vtoken = re.findall("video_token: '(.*?)'", page)[0]
    except: return None
    nref = url
#    if 'serial' in url:
#      nref = url
#    else:
#      ulist = url.split('/')
#      ulist[len(ulist) - 2] = vtoken
#      nref = '/'.join(ulist)
    
#    req = req_url(nref, opts = {'Referer' : ref}, cookies=req.cookies)
#    page = req.content
    
#     xbmc.log(page)

#     csrf = re.findall('name="csrf-token" content="(.*?)"', page)[0]
#     xacc = re.findall("user_token: '(.*?)'", page)[0]
    #    bdata = base64.b64encode(re.findall('\|setRequestHeader\|(.*?)\|', page)[0])

    vtoken = re.findall("video_token: '(.*?)'", page)[0]
#     ctype = re.findall("content_type: '(.*?)'", page)[0]
#     mw_key = urllib.quote_plus(re.findall("var mw_key = '(.*?)'", page)[0])
#     ref = urllib.quote_plus(re.findall("ref: encodeURIComponent\('(.*?)'", page)[0])

    mw_pid = re.findall("partner_id: (.*?),", page)[0]
    p_domain_id = re.findall("domain_id: (.*?),", page)[0]
    
#    hzsh = re.findall("setTimeout\(function\(\) {\n    (.*?)\['(.*?)'\] = '(.*?)';", page, re.MULTILINE|re.DOTALL)[0]
#     setTimeout(function() {
#     e37834294bc3c6bda8e36eb04ac3adc5['4e0ee0a1036a72dacc804306eabaaba3'] = 'b4b34c43ff2dc523887b8814e5f96f2d';
#   }

    opts = {'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
#             'X-CSRF-Token': csrf,
#             'X-Access-Level': xacc,
            'X-Condition-Safe': 'Normal',
            'X-Format-Token': 'B300',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer' : nref
            }

    udata = {'video_token': vtoken,
#                 'content_type': ctype,
#                 'mw_key': mw_key,
                'mw_key': '1ffd4aa558cc51f5a9fc6888e7bc5cb4',
             'mw_pid': mw_pid,
             'p_domain_id': p_domain_id,
             'ad_attr': '0',
             'iframe_version': '2.1',
             'c0e005ee151ce1c4': 'cbafa6de912548080e8be488'
#              'c90b4ca500a12b91e2b54b2d4a1e4fb7': 'cc5610c93fa23befc2d244a76500ee6c'


             }
    
    req.cookies['quality'] = '720'
    
    murl = 'http://moonwalk.cc/manifests/video/%s/all'%vtoken
    
    req = req_url(murl, opts = opts, cookies = req.cookies, data = udata)
    html = req.content

#     cook = re.search('<cookie>(.+?)</cookie>', html).group(1)
#     xbmc.log('ncook= ' + cook + ';quality=720')    
#     re.sub('<cookie>(.+?)</cookie>', '', html)
    
    xbmc.log(html)
    page = json.loads(html)
    nurl = page["mans"]["manifest_m3u8"]

#     nurl = 'http://moonwalk.cc/video/html5?manifest_m3u8=%s&manifest_mp4=%s&token=%s&pid=%s&debug=0'% \
#     (page["mans"]["manifest_m3u8"], page["mans"]["manifest_mp4"], vtoken, mw_pid)
#     ndata = 'manifest_m3u8=%s&manifest_mp4=%s&token=%s&pid=%s&debug=0'% \
#     (page["mans"]["manifest_m3u8"], page["mans"]["manifest_mp4"], vtoken, mw_pid)
    
    params = {'manifest_m3u8': page["mans"]["manifest_m3u8"],
              'manifest_mp4': page["mans"]["manifest_mp4"],
              'token': vtoken,
              'pid': mw_pid,
              'debug': '0'
              }

    opts['Upgrade-Insecure-Requests'] = '1'
    req = req_url(nurl,
                  opts = {'Upgrade-Insecure-Requests': '1',
                          'Referer' : nref},
                  cookies = req.cookies,
                  params = params
                  )
        
    html = req.content
#    xbmc.log(html)
    
    r = [(i[0], i[1]) for i in re.findall('#EXT-X-STREAM-INF:.*?RESOLUTION=\d+x(\d+).*?(http.*?(?:\.abst|\.f4m|\.m3u8)).*?', html, re.DOTALL) if i]
    r0 = re.findall('RESOLUTION=(.*?),', html)
    dbg_log('- r:'+  str(r) + '\n')
    dbg_log('- r0:'+  str(r0) + '\n')
    i = xbmcgui.Dialog().select('Video Quality', r0)

    return r[i][1]
    

def get_kinoxa(url):
    dbg_log('-get_kinoxa:'+ '\n')
    dbg_log('- url:'+  url + '\n')    
    
    link = None
    req = req_url(url)
    http = req.content
    
    flvs = re.compile('src="http(.*?)"').findall(http)
    hrefs = re.compile('<a href="(.*?)">').findall(http)
    
    if len(flvs) > 1:
        link = "http" + flvs[1]
    elif len(flvs):
        link = "http" + flvs[0]
    elif len(hrefs):
        link = hrefs[0]
        
    return link
        
def KNX_play(url, cook):
    dbg_log('-NKN_play:'+ '\n')
    dbg_log('- url:'+  url + '\n')
    
    if cook: cookies=json.loads(cook)
    else: cookies=None
    
    req = req_url(url, cookies=cookies)
    http = req.content
    
    print http

    iframes = re.compile('<iframe class="prerolllvid"(.*?)src="(.*?)"').findall(http)
    
    if len(iframes[0][1]) == 0: return

    link = None
    
    if "kinoxa" in iframes[0][1]:
        link = get_kinoxa(iframes[0][1])
    elif "youtube" in iframes[0][1]:
        link = None
    else:
        link = get_moonwalk(iframes[0][1], url, req.cookies)

    if link != None:
        item = xbmcgui.ListItem(path = link)
        xbmcplugin.setResolvedUrl(pluginhandle, True, item)

def KNX_ctlg(url):
    dbg_log('-KNX_ctlg:' + '\n')
    dbg_log('- url:'+  url + '\n')
               
    catalog  = [
                ( "/novinki_kino/", 'Новинки кино'),
                ( "/filmy_2017_goda/", '2017 года'),
                ( "/filmy_2016_goda/", '2016 года'),
                ( "/filmy_2015_goda/", '2015 года'),
                ( "/filmy_2014_goda/", '2014 года'),
                ( "/filmy_2013_goda/", '2013 года'),
                ( "/filmy_2012_goda/", '2012 года'),
                ( "/filmy_2011_goda/", '2011 года'),
                ( "/filmy_2010_goda/", '2010 года'),
                ( "/filmy_2009_goda/", '2009 года'),
                ( "/filmy_v_vysokom_kachestve_hd/", 'В высоком качестве HD'),
                ( "/kachestvo_full_hd/", 'FULL HD'),
                ( "/komedii/", 'Комедии'),
                ( "/boeviki/", 'Боевики'),
                ( "/dramy/", 'Драмы'),
                ( "/uzhasy/", 'Ужасы'),
                ( "/fantastika/", 'Фантастика'),
                ( "/trillery/", 'Триллеры'),
                ( "/detektivy/", 'Детективы'),
                ( "/dokumentalnye/", 'Документальные'),
                ( "/multfilmy/", 'Мультфильмы'),
                ( "/mistika/", 'Мистика'),
                ( "/sovetskie_filmy/", 'Советские фильмы'),
                ( "/semejnye/", 'Семейные'),
                ( "/sportivnye/", 'Спортивные'),
                ( "/melodramy/", 'Мелодрамы'),
                ( "/russkie_melodramy/", 'Русские Мелодрамы'),
                ( "/russkie_filmy/", 'Русские фильмы'),
                ( "/russkie_serialy/", 'Русские сериалы'),
                ( "/zarubezhnye_serialy/", 'Зарубежные сериалы'),
                ( "/trejlery/", 'Трейлеры'),
                ( "/fehntezi/", 'Фэнтези'),
                ( "/prikljuchenija/", 'Приключения'),
                ( "/istoricheskie/", 'Исторические'),
                ( "/vestern/", 'Вестерн'),#         stxt = uni2enc(gettranslit(kbd.getText()))
                ( "/animeh/", 'Аниме'),
                ( "/kriminal/", 'Криминал'),
                ( "/voennye/", 'Военные'),
                ( "/goblinskij_perevod/", 'Гоблинский перевод'),
                ( "/poznaem_mir/", 'Познаем мир'),
                ( "/biografija/", 'Биография'),
                ( "/xxx/", 'XXX'),
                ( "/jumoristicheskie_peredachi/", 'Юмористические передачи'),
                ( "/teleshou/", 'Передачи')]
               
               
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
        
def KNX_find(cook):
    dbg_log('-KNX_find:'+ '\n')
    
    kbd = xbmc.Keyboard()
    kbd.setHeading('ПОИСК')
    kbd.doModal()
    if kbd.isConfirmed():
        stxt = uni2cp(gettranslit(kbd.getText()))
#         stxt = kbd.getText()
#         furl = find_pg + stxt + fdpg_pg
        furl = find_pg
        dbg_log('- furl:'+  furl + '\n')
        KNX_list(furl, '1', 'find', stxt, cook)

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
unified = params['unified'] if 'unified' in params else None
usearch = params['usearch'] if 'usearch' in params else None
if unified: type = 'unis'
if usearch: type = 'unds'

if url=='':
    url = page_pg

if mode == '': KNX_list(url, page, type, find, cook)
elif mode == 'ctlg': KNX_ctlg(url)
elif mode == 'play': KNX_play(url, cook)
elif mode == 'find': KNX_find(cook)
elif mode == 'show': KNX_show(url)
elif mode == 'search': 
    url = find_pg
    KNX_list(url, '1', type, uni2cp(gettranslit(urllib.unquote_plus(keyword))), cook)
    
#elif mode == 'list': KNX_list(url, page)


