# -*- coding: utf-8 -*-
#!/usr/bin/python
# Writer (c) 2012, Silhouette, E-mail: 
# Rev. 0.5.3


import urllib,urllib2,re,sys,os,time,random
import xbmcplugin,xbmcgui,xbmcaddon
import json

dbg = 0
dbg_gd = 0

pluginhandle = int(sys.argv[1])

start_pg = "http://www.imb-plus.tv/"
login_pg = "user/login.php"
index_pg = "index.php"
cntry_pg = "tv_channels.php/country/"
cntry_pl = "index.php/id/"
guige_pg = "guide.php?src="
vlc_pg = "vlc.php?"
key_pg = "lib/ajax/ajax_channelChanged.php?"
time_pg = "http://www.timeanddate.com/worldclock/city.html?n="

__settings__ = xbmcaddon.Addon(id='plugin.video.imbplus.tv')
usr_log = __settings__.getSetting('usr_log')
usr_pwd = __settings__.getSetting('usr_pwd')
usr_ctry = __settings__.getSetting('usr_ctry')
usr_guide = __settings__.getSetting('usr_guide')

if usr_guide == "true":
  usr_tst = __settings__.getSetting('usr_tst')

usr_allch = "false"

def dbg_log(line):
    if dbg: print line
    
def get_events(url, events, chGr):    

    months = {'Января':'01',
            'Февраля':'02',
            'Марта':'03',
            'Апреля':'04',
            'Мая':'05',
            'Июня':'06',
            'Июля':'07',
            'Августа':'08',
            'Сентября':'09',
            'Октября':'10',
            'Ноября':'11',
            'Декабря':'12',
            'Січня': '01',
            'Лютого': '02',
            'Березня': '03',
            'Квітня': '04',
            'Травня': '05',
            'Червня': '06',
            'Липня': '07',
            'Серпня': '08',
            'Вересня': '09',
            'Жовтня': '10',
            'Листопада': '11',
            'Грудня': '12',
            'Styczeń': '01',
            'Luty': '02',
            'Marzec': '03',
            'Kwiecień': '04',
            'Maj': '05',
            'Czerwiec': '06',
            'Lipiec': '07',
            'Sierpień': '08',
            'Wrzesień': '09',
            'Październik': '10',
            'Listopad': '11',
            'Grudzień': '12 '}
    

    htpg = get_url(url + guige_pg + chGr)
    print htpg
    oneline = re.sub('\n', '', htpg)
    htpg = re.sub('<tr class="day">', '<class/><tr class="day">', oneline)
    oneline = re.sub('</table>', '<class/></table>', htpg)

    pg_ls = re.compile('<tr class="day"><td colspan="3">(.*?), (.*?)</td></tr>(.*?)<class/>').findall(oneline)
    if len(pg_ls) == 0:
        return events

    i = 0
    for dw, ed, ddescr in pg_ls:
        ed_ls = re.split(' ',ed)
        
        ev_ls = re.compile('<td class="et">(.*?)</td><td class="event">(.*?)</td>').findall(ddescr)
        if len(ev_ls) == 0:
            return events
        for evt, evm in ev_ls:
            evtn = time.mktime(time.strptime(ed_ls[2] + '-' + months[ed_ls[1]]+ '-' + ed_ls[0] + ' '+ evt, "%Y-%m-%d %H:%M"))
            if i: 
                if dbg_gd: 
                    dbg_log(evtn)
                    dbg_log(time.localtime(evtn))

            if i and events[-1][0][0] > evtn:
                oldyd = time.localtime(events[-1][0][0]).tm_yday
                newyd = time.localtime(evtn).tm_yday
                if oldyd != newyd or corr == 0:
                    evtn += 24 * 3600
                    corr = 1
                    if dbg_gd: dbg_log(time.localtime(evtn))
                else: corr = 0
            else: corr = 0

            events.append([(evtn, evm)])
            if dbg_gd: dbg_log('%d %s'%(evtn,ed_ls[2] + '-' + months[ed_ls[1]]+ '-' + ed_ls[0] + ' '+ evt + ' '+ evm))
            i = 1
             
    return events

def get_evline(events, tm):
    prtm = events[0][0][0]
    if dbg_gd: dbg_log('tm-%s'%tm)
    for i in range(1,len(events)):
        if tm >= prtm and tm < events[i][0][0]:
            line = '%s-%s %s'%(time.strftime("%H:%M", time.localtime(prtm)),\
            time.strftime("%H:%M", time.localtime(events[i][0][0])),events[i-1][0][1])
            return line
        else:
            prtm = events[i][0][0]
            
    return ''
  

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

def IMB_ctls(url):
    dbg_log('-IMB_ctls:' + '\n')

    http = get_url(url + login_pg, save_cookie = True, referrer = url + index_pg)
    mycookie = re.search('<cookie>(.+?)</cookie>', http).group(1)
    http = get_url(url + login_pg, 
                  data = "login=" + usr_log + "&pass=" + usr_pwd + "&sign=Login",
                  cookie = mycookie, referrer = url + login_pg)
                  
    if usr_ctry != 'all':
        IMB_chls(url, mycookie)
        return
        
    ct_ls = [('ru', 'Russian TV', 'images/programs-russian.jpg'),\
             ('ua', 'Ukranian TV', 'images/programs-ukrainian.jpg'),\
             ('pl', 'Polish TV', 'images/programs-polish.jpg')]
    
    for ctry, ctTitle, ctLogo  in ct_ls:
        item = xbmcgui.ListItem(ctTitle, iconImage=url + ctLogo, thumbnailImage=url + ctLogo)
        uri = sys.argv[0] + '?mode=chls' \
        + '&ctry=' + ctry + '&cook=' + urllib.quote_plus(mycookie)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
        dbg_log('- uri:'+  uri + '\n')
    
    xbmcplugin.endOfDirectory(pluginhandle) 
           
def IMB_chls(url, mycookie):
    dbg_log('-IMB_chls:' + '\n')

    if mycookie == '':
        http = get_url(url + login_pg, save_cookie = True, referrer = url + index_pg)
        mycookie = re.search('<cookie>(.+?)</cookie>', http).group(1)
        http = get_url(url + login_pg, 
                  data = "login=" + usr_log + "&pass=" + usr_pwd + "&sign=Login",
                  cookie = mycookie, referrer = url + login_pg)
    else:
        http = get_url(url, cookie = mycookie, referrer = url + login_pg)

    if usr_ctry != 'pl':
        cntry_ls = re.compile('<a href="'+ url + cntry_pg + usr_ctry + '(.+?)"').findall(http)
    else:
        cntry_ls = re.compile('<a href="'+ url + index_pg + '(.+?)"').findall(http)
        
    if len(cntry_ls):
        channel_pg = cntry_pg + usr_ctry + cntry_ls[0]
        dbg_log('- channel_pg:'+  channel_pg + '\n')
    
        http = get_url(url + channel_pg, cookie = mycookie, referrer = url + index_pg)
        rnew_ls = re.compile('window.location\s=\s"http://www.imb-plus.tv/user/renew.php"').findall(http)

        if len(rnew_ls) and usr_tst != "true":
            item = xbmcgui.ListItem("Renew Membership")
            xbmcplugin.addDirectoryItem(pluginhandle, "", item, False)  
            dbg_log('- renew\n')
        else:
            chan_ls = re.compile('<tr><td align="center"><div class="channel_bg"><img class="channel_logo" onclick="javascript:RunChannel((.+?));" src="(.+?)" title="(.+?)"/></div></td><td align="center" colspan="1"><img src="(.+?)" onclick="javascript:GetChannelGrid((.+?));" border="0" title="(.+?)" /></td></tr>').findall(http)

            for chRun, runch2, chLogo, chTitle, prGuide, chGrid, gdGrid2, gdTitle  in chan_ls:
                #print chRun+" "+chLogo+" "+chTitle+" "+chGrid
                item = xbmcgui.ListItem(chTitle, iconImage=chLogo, thumbnailImage=chLogo)
                uri = sys.argv[0] + '?mode=chtz' + '&ctry=' + usr_ctry \
                + '&chrn=' + chRun + '&chgr=' + chGrid \
                + '&rfr=' + url + index_pg + '&chpg=' + channel_pg +  '&chlg=' + chLogo + '&cook=' + urllib.quote_plus(mycookie)
                
                if usr_allch == "false":
                    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
                    dbg_log('- uri:'+  uri + '\n')
                else:
                    IMB_chtz(start_pg, chRun, chLogo, chGrid, mycookie, url + index_pg, channel_pg)
                
    xbmcplugin.endOfDirectory(pluginhandle) 
    
def IMB_chtz(url, chrn, chlg, chgr, cook, rfr, chpg):
    dbg_log('-IMB_chtz:'+ '\n')

    http = get_url(url + chpg, cookie = cook, referrer = rfr)

    uid_ls = re.compile('<body onload="onLoad\((.+?), (.+?), (.+?), (.+?)\)">').findall(http)
    uid = re.sub("\'", "", uid_ls[0][3])
    dbg_log('- uid:'+  uid + '\n')
    
    chrn2 = re.sub("\(", "", chrn)
    chrn = re.sub("\)", "", chrn2)

    events = []  
    tml = 0
    
    if usr_guide == "true":
      tm_ref = {'ru': '166', 
                'ua': '367', 
                'pl': '262'}    

      events = get_events(url, events, chgr)
      if len(events):
          httm = get_url(time_pg + tm_ref[usr_ctry])
          tml_ls = re.compile('<th class=w5>Current Time</th><td><strong id=ct  class=big>(.*?)</strong>').findall(httm)
          if len(tml_ls):
              if dbg_gd: dbg_log(tml_ls[0]) #Monday, March 12, 2012 at 7:20:27 AM
              tml = time.mktime(time.strptime(tml_ls[0],"%A, %B %d, %Y at %I:%M:%S %p"))
            
    tz_ls = re.compile("<option name='time_zone' class='box' id=\"(.+?)\" value=\"(.+?)\" (.+?)>(.+?)</option>").findall(http)
    i = 0
    for tz_nm, tz_val, tz_sel, tz_dcr  in tz_ls:
        tzvl = int(tz_val)
        if tzvl:
            if usr_ctry == "ru": tzgd = tzvl + 4
            elif usr_ctry == "ua": tzgd = tzvl + 2
            elif usr_ctry == "pl": tzgd = tzvl + 1
            
            tzvl = i + 4
        else:
            tzgd = 0

        tz_val = str(tzvl)

        if tml:
            evline = get_evline(events, tml - (tzgd) * 3600 )
        else:
            evline = None 
        
        if evline:  description = evline
        else: description = tz_dcr
        
        dbg_log('- description:'+  description)
                
        item = xbmcgui.ListItem(description, iconImage=chlg)
        uri = sys.argv[0] + '?mode=chpl' + '&tzvl=' + tz_val \
        + '&uid=' + uid + '&chrn=' + chrn \
        + '&rfr=' + url + chpg + '&chlg=' + chlg + '&cook=' + urllib.quote_plus(cook)
    
        title = description
        thumbnail = chlg
    
        item.setInfo( type='video', infoLabels={'title': title, 'plot': description})
        item.setProperty('IsPlayable', 'true')
        #item.setProperty('fanart_image',thumbnail)
        xbmcplugin.addDirectoryItem(pluginhandle,uri,item)
        dbg_log('- uri:'+  uri + '\n')
        i += 1

    if mode == 'chtz':
        xbmcplugin.endOfDirectory(pluginhandle)


def IMB_chpl(url, chrn, chlg, cook, rfr, tzvl, uid):     
    dbg_log('-IMB_chpl:'+ '\n')
    vlc_url = url + 'lib/ajax/aux_act_json.php?' + 'order=' + uid + '&ch=' + chrn + '&tz=' + tzvl + '&ts=0' + '&t=' + str(random.random())
    vlc = get_url(vlc_url, cookie = cook, referrer = rfr)
    dbg_log(vlc)
    lnk_ls = re.compile('"url":"(.+?)"').findall(vlc)
    if len(lnk_ls) :
        #vlink = re.sub('\\/','/',lnk_ls[0])
        vlink_ls = lnk_ls[0].split('\/')
        #print vlink_ls
        vlink = vlink_ls[0]+'//'+vlink_ls[2]+'/'+vlink_ls[3]
        dbg_log(vlink)
        item = xbmcgui.ListItem(path =  vlink)
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

tzvl = ''
cook = ''
rfr = ''
chpg = ''
chrn = ''
chlg = ''
chgr = ''
ctry = ''
uid = ''
mode=''


try:
    mode=params['mode']
    dbg_log('-MODE:'+ mode + '\n')
except: pass
try: 
    tzvl=urllib.unquote_plus(params['tzvl'])
    dbg_log('-TZVL:'+ tzvl + '\n')
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
    chpg=urllib.unquote_plus(params['chpg'])
    dbg_log('-CHPG:'+ chpg + '\n')
except: pass
try: 
    chrn=urllib.unquote_plus(params['chrn'])
    dbg_log('-CHRN:'+ chrn + '\n')
except: pass
try: 
    chlg=urllib.unquote_plus(params['chlg'])
    dbg_log('-CHLG:'+ chlg + '\n')
except: pass
try: 
    chgr=urllib.unquote_plus(params['chgr'])
    dbg_log('-CHGR:'+ chgr + '\n')
except: pass
try: 
    uid=urllib.unquote_plus(params['uid'])
    dbg_log('-UID:'+ uid + '\n')
except: pass
try: 
    ctry=urllib.unquote_plus(params['ctry'])
    dbg_log('-CTRY:'+ ctry + '\n')
except: pass

if usr_ctry == 'all':
    if ctry != '':
        usr_ctry = ctry
else:
    if mode == None:
        mode = 'ctls'
     

if mode == 'chpl': IMB_chpl(start_pg, chrn, chlg, cook, rfr, tzvl, uid)
elif mode == 'chtz': IMB_chtz(start_pg, chrn, chlg, chgr, cook, rfr, chpg)
elif mode == 'chls': IMB_chls(start_pg, cook)
elif mode == '': IMB_ctls(start_pg)

