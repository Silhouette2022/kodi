'''
    Our Match Add-on
    Copyright (C) 2016 123456

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import xbmcplugin, xbmcgui, urllib, re, os, sys, time
import dom_parser2
import client
import kodi
art       = xbmc.translatePath(os.path.join('special://home/addons/plugin.video.ourmatch/resources/art', ''))

def main(name=None, iconimage=None):

    c = client.request('http://ourmatch.net')
    if not iconimage: iconimage = kodi.addonicon
    if name:
        r = dom_parser2.parse_dom(c, 'li', {'class': 'header'})
        r = [i for i in r if 'title="%s"' % name in i.content]
        r = dom_parser2.parse_dom(r, 'li', {'class': 'hover-tg'})
        r = dom_parser2.parse_dom(r, 'a')
        for i in r:
            addDir(i.content,i.attrs['href'],3,iconimage)
    else:
        r = dom_parser2.parse_dom(c, 'a', {'class': 'sub'})
        addDir(kodi.giveColor(kodi.countGitHubIssues('https://github.com/Colossal1/plugin.video.ourmatch/issues'),'blue',True) + kodi.giveColor(' | Click To View Issues','white',True),'null',5,kodi.addonicon,isFolder=False,isPlayable=False)
        addDir('Search...','search',3,art+'search.png')
        addDir('Most Recent','http://ourmatch.net/',3,art+'new.png')
        for i in r:
            addDir(i.attrs['title'],'none',2,art+i.attrs['title'].lower()+'.png')

def getMatches(url):

    if url == 'search':
        term = kodi.get_keyboard(heading='Search Our Match')
        if term: c  = client.request('http://ourmatch.net/?s=%s' % term.lower().replace(' ','+'))
        else: quit()
    else:
        c  = client.request(url)
    r = dom_parser2.parse_dom(c, 'div', {'class': 'vidthumb'})
    r = [(dom_parser2.parse_dom(i, 'span', {'class': 'time'}), \
          dom_parser2.parse_dom(i, 'a', req=['href','title']), \
          dom_parser2.parse_dom(i, 'img', req='src')) for i in r if i]
    r = [(re.sub('<.+?>', '', i[0][0].content), i[1][0].attrs['title'], i[1][0].attrs['href'], i[2][0].attrs['src']) for i in r]
    for i in r:
        addDir('%s - %s' % (i[0], i[1]), i[2], 4, i[3])   
    try:
        np = re.findall('''<link\s*rel=['"]next['"]\s*href=['"]([^'"]+)''', c)[0]
        addDir('Next Page -->', np, 3, art+'nextpage.png')
    except: pass

def getStreams(name,url,iconimage):
    c  = client.request(url)
    r = re.findall("\d+':\s*{embed:'([^}]+)", c)
    for i in r:
        try:
            src = re.findall('''src=['"]([^'"]+)''',i)[0]
            if not src.startswith('http'): src = 'https:' + src
            try: lang = re.findall('''lang:['"]([^'"]+)''',i)[0]
            except: lang = 'Unknown'
            try: name = re.findall('''['"]type['"]:['"]([^'"]+)''',i)[0]
            except: name = 'Unknown'
            try: quality = re.findall('''quality:['"]([^'"]+)''',i)[0]
            except: quality = 'Unknown'
            try: source = re.findall('''source:['"]([^'"]+)''',i)[0]
            except: source = 'Unknown'
            addDir('%s - %s - %s - %s' % (name, quality, lang, source),src,1,iconimage,isFolder=False)
        except: pass

def githubIssues():

    choice = xbmcgui.Dialog().yesno("[COLOR red]Please select an option[/COLOR]", "Would you like to view open issues or closed issues?",yeslabel='Closed',nolabel='Open')

    import githubissues
    if choice == 0: name = 'open'
    elif choice == 1: name = 'closed'
    else: quit()
    githubissues.run('Colossal1/plugin.video.ourmatch', '%s' % name)
    file = xbmc.translatePath(os.path.join(kodi.datafolder, '%s-issues-%s.csv' % (kodi.get_id(),name)))
    
    with open(file,mode='r')as f: txt = f.read()
    items = re.findall('<item>(.+?)</item>', txt, re.DOTALL)
    if (not items) or (len(items) < 1):
        msg_text = kodi.giveColor('No %s issues with Our Match at this time.' % name.title(),'blue',True)
    else:
        msg_text = kodi.giveColor('%s Issues with Our Match\n' % name.title(),'blue',True) + kodi.giveColor('Report Issues @ https://github.com/Colossal1/plugin.video.ourmatch/issues','white',True) + '\n---------------------------------\n\n'
        for item in items:
            try: id = re.findall('<id>([^<]+)', item)[0]
            except: id = 'Unknown'
            try: user = re.findall('<username>([^<]+)', item)[0]
            except: user = 'Unknown'
            try: label = re.findall('<label>([^<]+)', item)[0]
            except: label = 'Unknown'
            try: title = re.findall('<title>([^<]+)', item)[0]
            except: title = 'Unknown'
            try: body = re.findall('<body>([^<]+)', item)[0]
            except: body = 'Unknown'
            try: 
                created = re.findall('<created>([^<]+)', item)[0]
                date,time = created.split('T')
            except:
                date = 'Unknown'
                time = 'Unknwon'
            msg_text += '[B]ID: %s | Label: %s \nBy: %s on %s at %s[/B] \n\nTitle: %s \nMessage %s \n\n---------------------------------\n\n' \
                         % (id, \
                            kodi.githubLabel(label), \
                            user, \
                            date, \
                            time.replace('Z',''), \
                            title, \
                            body)
    textboxGit('OurMatch Issues', msg_text)

def textboxGit(header=None,announce=None):
    class TextBox():
        WINDOW=10147
        CONTROL_LABEL=1
        CONTROL_TEXTBOX=5
        def __init__(self,*args,**kwargs):
            xbmc.executebuiltin("ActivateWindow(%d)" % (self.WINDOW, )) # activate the text viewer window
            self.win=xbmcgui.Window(self.WINDOW) # get window
            xbmc.sleep(500) # give window time to initialize
            self.setControls()
        def setControls(self):
            if header == None: self.win.getControl(self.CONTROL_LABEL).setLabel(sys.args(0)) # set heading
            else: self.win.getControl(self.CONTROL_LABEL).setLabel(header) # set heading
            self.win.getControl(self.CONTROL_TEXTBOX).setText(str(announce))
            return
    announce = announce.encode('utf-8')
    TextBox()
    while xbmc.getCondVisibility('Window.IsVisible(10147)'):
        time.sleep(.5)

def vidupstream(url):
      url = url[:url.find("?")]
      url = url.replace("player/PopUpIframe", "embed00")
      link = client.request(url)
      hls = re.compile('hls:"(.+?)"').findall(link)
      xbmc.log(str(hls))
      xbmc.log(str(len(hls)))
      if len(hls):
        if len(hls) == 1: i = 0
        else:
          r0 = ["Source " + str(key + 1) for key in range(len(hls))]
          xbmc.log('- r0:'+  str(r0) + '\n')
          i = xbmcgui.Dialog().select('', r0)
          
        return 'http:' + hls[i]
      else: return None
      
def okru(url):
      link = client.request(url)
      html = urllib.unquote_plus(link).replace("\&quot;", '"').replace("\\\\u0026","&")
      #xbmc.log(html)
      names = re.compile('"name":"(.+?)","url":"https(.+?)"').findall(html)
      xbmc.log(str(names))
      xbmc.log(str(len(names)))
      
      lnames = len(names)
      if lnames:
        if lnames == 1: i = 0
        else:
          r0 = [names[key][0] for key in range(1,lnames)]
          r0.reverse()
          xbmc.log('- r0:'+  str(r0) + '\n')
          
          i = lnames - 1 - xbmcgui.Dialog().select('', r0)
          
        return 'https' + names[i][1]
      else: return None


def play(name,url):
    import urlresolver
    if urlresolver.HostedMediaFile(url).valid_url(): 
        url = urlresolver.HostedMediaFile(url).resolve()
    else:
        link  = client.request(url)
        link  = link
        match = re.compile('<source src="(.+?)" type="video/mp4" class="mp4-source"/>').findall(link)
        for url in match:
            name = name
            url  = 'https:'+url
    stream_url = url
    xbmc.log(" $$$$$$$ ") 
    xbmc.log(stream_url)
    if "vidupstream" or "streamatus" in url: stream_url = vidupstream(url)
    elif "ok.ru" in url: stream_url = okru(url)
    else: stream_url = url
    xbmc.log(str(stream_url))

    if stream_url != None:
        liz = xbmcgui.ListItem(name, path=stream_url)
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)        
        
def addDir(name,url,mode,iconimage,isFolder=True,isPlayable=True):
    try: client.replaceHTMLCodes(name)
    except: pass
    name = name.replace('&#038;','&')
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name} )
    liz.setProperty('fanart_image', kodi.addonfanart)
    if isPlayable: liz.setProperty("IsPlayable","true")
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=isFolder)
    return ok

def get_params():
    param=[]
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
url=None
name=None
mode=None
iconimage=None
try: url=urllib.unquote_plus(params["url"])
except: pass
try: name=urllib.unquote_plus(params["name"])
except: pass
try: mode=int(params["mode"])
except: pass
try: iconimage=urllib.unquote_plus(params["iconimage"])
except: pass

if mode==None or url==None or len(url)<1: main()
elif mode==1: play(name,url)
elif mode==2: main(name, iconimage)
elif mode==3: getMatches(url)
elif mode==4: getStreams(name,url,iconimage)
elif mode==5: githubIssues()

xbmcplugin.endOfDirectory(int(sys.argv[1]))