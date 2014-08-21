#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.2.9
# -*- coding: utf-8 -*-

import urllib, re, sys
import xbmc, xbmcplugin,xbmcgui,xbmcaddon
import HTMLParser
import XbmcHelpers
import simplejson as json

from urllib2 import Request, urlopen, URLError
common = XbmcHelpers

BASE_URL = 'http://www.filin.tv'
pluginhandle = int(sys.argv[1])

Addon = xbmcaddon.Addon(id='plugin.video.filin.tv')
language      = Addon.getLocalizedString
addon_icon    = Addon.getAddonInfo('icon')
addon_path    = Addon.getAddonInfo('path')

import Translit as translit
translit = translit.Translit(encoding='cp1251')

VIEW_MODES = {
    "List" : '50',
    "Big List" : '51',
    "Media Info" : '52',
    "Media Info 2" : '54',
    "Fanart" : '57',
    "Fanart 2" : '59'
}

# *** Python helpers ***
def strip_html(text):
  def fixup(m):
    text = m.group(0)
    if text[:1] == "<":
      if text[1:3] == 'br':
        return '\n'
      else:
        return ""
    if text[:2] == "&#":
      try:
        if text[:3] == "&#x":
          return chr(int(text[3:-1], 16))
        else:
          return chr(int(text[2:-1]))
      except ValueError:
        pass
    elif text[:1] == "&":
      import htmlentitydefs
      if text[1:-1] == "mdash":
        entity = " - "
      elif text[1:-1] == "ndash":
        entity = "-"
      elif text[1:-1] == "hellip":
        entity = "-"
      else:
        entity = htmlentitydefs.entitydefs.get(text[1:-1])
      if entity:
        if entity[:2] == "&#":
          try:
            return chr(int(entity[2:-1]))
          except ValueError:
            pass
        else:
          return entity
    return text
  ret =  re.sub("(?s)<[^>]*>|&#?\w+;", fixup, text)
  return re.sub("\n+", '\n' , ret)

def remove_extra_spaces(data):  # Remove more than one consecutive white space
    p = re.compile(r'\s+')
    return p.sub(' ', data)

def unescape(entity, encoding):
  if encoding == 'utf-8':
    return HTMLParser.HTMLParser().unescape(entity).encode(encoding)
  elif encoding == 'cp1251':
    return entity.decode(encoding).encode('utf-8')

def localize(string):
    return unescape(string, 'utf-8')

def colorize(string, color):
    text = "[COLOR " + color + "]" + string + "[/COLOR]"
    return text

def get_url(string):
  return re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+.xml', string)[0]


# *** XBMC helpers ***
def xbmcItem(url, title, mode, *args):
    item = xbmcgui.ListItem(title)
    uri = sys.argv[0] + '?mode='+ mode + '&url=' + url
    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)


def get_params():
    param=[]
    paramstring = sys.argv[2]

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


# *** Addon helpers ***
def beatify_title(title):
  title = unescape(title, 'cp1251').replace(language(5000).encode('utf-8'),"")
  return title.replace(language(5001).encode('utf-8'),"")


def getDescription(block):
    html = block[block.find('</h2>'):len(block)]
    return unescape(strip_html(remove_extra_spaces(html)), 'cp1251')

    #return unescape(remove_extra_spaces(remove_html_tags(html)), 'cp1251')


def getThumbnail(block):
    thumbnail = common.parseDOM(block, "img", ret = "src")[0]
    if thumbnail[0] == '/': thumbnail = BASE_URL+thumbnail
    return thumbnail


def getTitle(block):
    title = common.parseDOM(block, "a")
    return title[len(title)-1]


def calculateRating(x):
    rating = (int(x)*100)/100
    xbmc_rating = (rating*10)/100
    return xbmc_rating

# *** UI functions ***
def search():
    kbd = xbmc.Keyboard()
    kbd.setDefault('')
    kbd.setHeading(language(2002))
    kbd.doModal()
    keyword=''

    if kbd.isConfirmed():
      keyword = kbd.getText()

    if Addon.getSetting('translit') == 'true':
      keyword = translit.rus(kbd.getText())

    path = "/do=search"

    # Advanced search: titles only
    values = {
      'beforeafter' : 'after',
      'catlist[]' : '0',
      'do' : 'search',
      'full_search' : '1',
      'replyless' : '0',
      'replylimit' : '0',
      'resorder' : 'desc',
      'result_from' : '1',
      'result_num' : '30',
      'search_start' : '1',
      'searchdate' : '0',
      'searchuser' : '',
      'showposts' : '0',
      'sortby' : 'date',
      'subaction' : 'search',
      'titleonly' : '3'
    }
    try:
        # Apple TV
        values['story'] = keyword

        data = urllib.urlencode(values)
        req = Request(BASE_URL+path, data)
    except UnicodeEncodeError:
        # Desktop
        values['story'] = keyword.encode('cp1251')

        data = urllib.urlencode(values)
        req = Request(BASE_URL+path, data)

    try:
        response = urlopen(req)
    except URLError, e:
        if hasattr(e, 'reason'):
            print 'We failed to reach a server.'
            print 'Reason: ', e.reason
        elif hasattr(e, 'code'):
            print 'The server couldn\'t fulfill the request.'
            print 'Error code: ', e.code
    else:
        response = response.read()
        content = common.parseDOM(response, "div", attrs = { "id":"dle-content" })
        blocks = common.parseDOM(content, "div", attrs = { "class":"block" })

        if len(blocks) > 1:
            result = common.parseDOM(content, "span", attrs = { "class":"sresult" })[0]
            item = xbmcgui.ListItem(colorize(unescape(result, 'cp1251'), 'FF00FFF0'))
            item.setProperty('IsPlayable', 'false')
            xbmcplugin.addDirectoryItem(pluginhandle, '', item, False)

            mainf = common.parseDOM(content, "div", attrs = { "class":"mainf" })
            titles = common.parseDOM(mainf, "a")
            links = common.parseDOM(mainf, "a", ret = "href")

            for i in range(0, len(links)):
                title = beatify_title(titles[i])
                uri = sys.argv[0] + '?mode=SHOW&url=' + links[i] + "&thumbnail="

                item = xbmcgui.ListItem(title)

                # TODO: move to "addFavorite" function
                script = "special://home/addons/plugin.video.filin.tv/contextmenuactions.py"
                params = "add|%s"%links[i] + "|%s"%title
                runner = "XBMC.RunScript(" + str(script)+ ", " + params + ")"
                item.addContextMenuItems([(localize(language(3001)), runner)])
                xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
        else:
            item = xbmcgui.ListItem(colorize(language(2004), 'FFFF4000'))
            item.setProperty('IsPlayable', 'false')
            xbmcplugin.addDirectoryItem(pluginhandle, '', item, False)


    xbmcplugin.endOfDirectory(pluginhandle, True)


def getCategories(url):
    result = common.fetchPage({"link": url})

    if result["status"] == 200:
        content = common.parseDOM(result["content"], "div", attrs = { "class":"mcont" })
        categories = common.parseDOM(content, "option", ret="value")
        descriptions = common.parseDOM(content, "option")

        for i in range(0, len(categories)):
            uri = sys.argv[0] + '?mode=CATEGORIE&url=' + BASE_URL + '/x.php&categorie=' + categories[i]
            title = unescape(descriptions[i], 'cp1251')

            item = xbmcgui.ListItem(title)
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

    xbmcplugin.endOfDirectory(pluginhandle, True)


def getCategoryItems(url, categorie, page):
    print "*** getCategoryItems"
    path = url + "?onlyjanr=" + categorie
    page = int(page)

    response = common.fetchPage({"link": path})
    content = response['content']

    if response["status"] == 200:
        links = common.parseDOM(content, "a", ret="href")
        titles = common.parseDOM(content, "a")

        if page == 1:
            min=0
            max = {True: page*20, False: len(links)}[len(links) > (page*20)]
        else:
            min=(page-1)*20
            max= {True: page*20, False: len(links)}[len(links) > (page*20)]

        for i in range(min, max):
          uri = sys.argv[0] + '?mode=SHOW&url=' + links[i] + "&thumbnail="

          if titles[i] == '': titles[i] = "[Unknown]" #TODO: investigate title issue
          item = xbmcgui.ListItem(titles[i])

          # TODO: move to "addFavorite" function
          script = "special://home/addons/plugin.video.filin.tv/contextmenuactions.py"
          params = "add|%s"%links[i] + "|%s"%titles[i]
          runner = "XBMC.RunScript(" + str(script)+ ", " + params + ")"


          item.addContextMenuItems([(localize(language(3001)), runner)])
          xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

        if max >= 20 and max < len(links):
            uri = sys.argv[0] + '?mode=CNEXT&url=' + url + '&page=' + str(page+1) + '&categorie=' + categorie
            item = xbmcgui.ListItem(localize(language(3000)))
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

        xbmcplugin.endOfDirectory(pluginhandle, True)


def listGenres():
    genres = [
                 'http://www.filin.tv/otechestvennue/',
                 'http://www.filin.tv/detectiv/',
                 'http://www.filin.tv/romance/',
                 'http://www.filin.tv/action/',
                 'http://www.filin.tv/fantastika/',
                 'http://www.filin.tv/kriminal/',
                 'http://www.filin.tv/comedi/',
                 'http://www.filin.tv/teleshou/',
                 'http://www.filin.tv/multfilms/',
                 'http://www.filin.tv/adventure/',
                 'http://www.filin.tv/fantasy/',
                 'http://www.filin.tv/horror/',
                 'http://www.filin.tv/drama/',
                 'http://www.filin.tv/history/',
                 'http://www.filin.tv/triller/',
                 'http://www.filin.tv/mystery/',
                 'http://www.filin.tv/sport/',
                 'http://www.filin.tv/musical/',
                 'http://www.filin.tv/dokumentalnii/',
                 'http://www.filin.tv/war/'
    ]


    for i in range(0, len(genres)):
        uri = sys.argv[0] + '?&url=' + genres[i] + '/'
        item = xbmcgui.ListItem(localize(language(1000+i)))
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

    xbmcplugin.endOfDirectory(pluginhandle, True)


def listFavorites():
    string = Addon.getSetting('favorites')

    if len(string) == 0:
        item = xbmcgui.ListItem(language(3002))
        xbmcplugin.addDirectoryItem(pluginhandle, '', item, False)
    else:
        favorites = json.loads(string.replace('\x00', ''))
        for key in favorites:
            item = xbmcgui.ListItem(favorites[key])

            # TODO: show thumbnail (item = xbmcgui.ListItem(key, thumbnailImage=thumbnail))
            uri = sys.argv[0] + '?mode=SHOW&url=' + key + '&thumbnail='
            item.setInfo( type='Video', infoLabels={'title': favorites[key]})

            # TODO: move to "addFavorite" function
            script = "special://home/addons/plugin.video.filin.tv/contextmenuactions.py"
            params = "remove|%s" % key + "|%s" % favorites[key]
            runner = "XBMC.RunScript(" + str(script)+ ", " + params + ")"
            item.addContextMenuItems([(localize(language(3004)), runner)])
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

        item = xbmcgui.ListItem("[COLOR=FFFF4000]%s[/COLOR]" % language(3006))
        uri = sys.argv[0] + '?mode=RESET'
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

    xbmcplugin.endOfDirectory(pluginhandle, True)

def resetFavorites():
    dialog = xbmcgui.Dialog()
    answer = dialog.yesno(language(3006), language(3007))
    if answer == 1:
      Addon.setSetting('favorites', '')

# Get latest income from index page
def getRecentItems(url):

    if url==BASE_URL:
        xbmcItem('', colorize(localize('['+language(2002)+']'), "FF00FF00"), 'SEARCH')
        xbmcItem('', colorize(localize(language(2003)), "FF00FFF0"), 'FAVORITES')
        xbmcItem('', colorize(localize(language(2000)), "FF00FFF0"), 'CATEGORIES')
        xbmcItem('', colorize(localize(language(2001)), "FF00FFF0"), 'GENRES')

    getItems(url)


def getItems(url):
    print "*** getItems"

    response = common.fetchPage({"link": url})

    if response["status"] == 200:
        content = common.parseDOM(response["content"], "div", attrs = { "id":"dle-content" })
        blocknews = common.parseDOM(content, "div", attrs = { "class":"blocknews" })

        mainf = common.parseDOM(blocknews, "div", attrs = { "class":"mainf" })

        titles = common.parseDOM(mainf, "a")
        links = common.parseDOM(mainf, "a", ret="href")

        blocktext = common.parseDOM(content, "div", attrs = { "class":"block_text" })

        images = common.parseDOM(blocktext, "img", ret = "src")
        descriptions = common.parseDOM(blocktext, "td", attrs = { "style":"padding-left:10px;" })
        ratings = common.parseDOM(blocktext, "li", attrs={"class": "current-rating"})

        genres = []
        for i, g in enumerate(common.parseDOM(blocknews, "div", attrs = { "class":"categ" })):
            genres.append(" ".join(str(g) for g in common.parseDOM(g, "a")))

        for i, title in enumerate(titles):
            if images[i][0] == '/': images[i] = BASE_URL+images[i]
            title = beatify_title(title)
            genre = unescape(str(genres[i]), 'cp1251')

            description = unescape(descriptions[i].split('<br/>')[-1], 'cp1251')
            description = common.stripTags(description.split('</strong>')[-1])

            uri = sys.argv[0] + '?mode=SHOW&url=' + links[i] + '&thumbnail=' + images[i]
            item = xbmcgui.ListItem(title, iconImage = addon_icon, thumbnailImage=images[i])
            infoLabels={'title': title, 'genre' : genre, 'plot': description}

            if calculateRating(ratings[i]) > 0:
                infoLabels['rating'] = calculateRating(ratings[i])

            # print "Rating: %s - %d" % (ratings[i], calculateRating(ratings[i]))

            item.setInfo( type='Video', infoLabels=infoLabels)
            item.setProperty( "isFolder", 'True')

            # TODO: move to "addFavorite" function
            script = "special://home/addons/plugin.video.filin.tv/contextmenuactions.py"
            params = "add|%s"%links[i] + "|%s"%title
            runner = "XBMC.RunScript(" + str(script)+ ", " + params + ")"

            item.addContextMenuItems([(localize(language(3001)), runner)])
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

    next = url + '/page/2' if url.find("page") == -1 else url[:-1] + str(int(url[-1])+1)

    xbmcItem(next, localize(language(3000)), 'RNEXT')

    try:
        mode = VIEW_MODES[Addon.getSetting('seasonsViewMode')]
        xbmc.executebuiltin("Container.SetViewMode(" + mode + ")")
    except Exception, e:
        print "*** Exception"
        print e
        xbmc.executebuiltin('Container.SetViewMode(50)')

    xbmcplugin.endOfDirectory(pluginhandle, True)


def showItem(url, thumbnail):
    content = common.fetchPage({"link": url})["content"]
    mainf = common.parseDOM(content, "div", attrs = { "class":"categ" })
    block = common.parseDOM(content, "div", attrs = { "class":"ssc" })[0]

    image_container = common.parseDOM(block, "td", attrs = { 'valign':'top' })
    image = common.parseDOM(image_container, "img", ret="src")[0]
    image = image if image.startswith( 'http' ) else BASE_URL + image

    genre = unescape(" ".join(str(g) for g in common.parseDOM(mainf, "a")), 'cp1251')

    title = beatify_title(getTitle(block))
    desc = common.stripTags(getDescription(block))

    # TODO: find an alternativ way to get flashvars from javascript
    scripts = filter(None, common.parseDOM(content, 'script', attrs={'language': "javascript"})) # fastest
    matching = [s for s in scripts if "flashvar" in s]
    playlist = (matching[0].split('pl: ')[-1].split('.json')[0] + '.json').replace(' ', '').replace('"', '')

    if playlist:
        source_url = "http://kino-dom.tv/"

        if '/play/' in playlist:
          url2json = source_url+playlist
        else:
          url2json = source_url+playlist.replace('play/', '/play/')

        # multiple
        # url2json = "http://kino-dom.tv/01f551e61970b9645b5465460daccdfe/play/devushkiibombi.xml.json"

        # single
        # url2json = "http://kino-dom.tv/01f551e61970b9645b5465460daccdfe/play/sashatanja_mp4.xml.json"

        # wrong json format
        # url2json = "http://kino-dom.tv/01f551e61970b9645b5465460daccdfe/play/institutblagorodnihdevic2_mp4.xml.json"

        response = common.fetchPage({"link":url2json})["content"]

        try:
          playlist = json.loads(response)['playlist']
        except ValueError:
          print "WARNING: wrong JSON format"

          response = response.replace('\r', '').replace('\t', '').replace('\r\n', '')
          playlist = json.loads(response)['playlist']

        if 'playlist' in playlist[0]:
            print "*** This is a playlist with several seasons"

            for season in playlist:
                title = season['comment']
                episods = season['playlist']

                for episode in episods:
                    title = ('%s (%s)') % (episode['comment'], season['comment'])
                    uri = sys.argv[0] + '?mode=play&url=%s' % episode['file']

                    item = xbmcgui.ListItem(title, thumbnailImage=image)

                    overlay = xbmcgui.ICON_OVERLAY_WATCHED
                    info = {"Title": title, 'genre' : genre, "Plot": desc, "overlay": overlay, "playCount": 0}

                    item.setInfo( type='Video', infoLabels=info)
                    item.setProperty('IsPlayable', 'true')
                    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, False)
        else:
            print "*** This is a playlist with one season"

            for episode in playlist:
                title = episode['comment']
                uri = sys.argv[0] + '?mode=play&url=%s' % episode['file']

                item = xbmcgui.ListItem(title, thumbnailImage=image)

                overlay = xbmcgui.ICON_OVERLAY_WATCHED
                info = {"Title": title, 'genre' : genre, "Plot": desc, "overlay": overlay, "playCount": 0}

                item.setInfo( type='Video', infoLabels=info)
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(pluginhandle, uri, item, False)

        # for season in json:
        #     seasonName = season['comment']
        #     for obj in season['playlist']:
        #         locations.append(obj['file'])
        #         titles.append(seasonName+" - "+obj['comment'])

        # for i in range(0, len(locations)):
        #     uri = sys.argv[0] + '?mode=PLAY&url=%s'%locations[i]
        #     item = xbmcgui.ListItem(unescape(titles[i], 'utf-8'), iconImage=addon_icon, thumbnailImage=image)

        #     print locations[i]

        #     overlay = xbmcgui.ICON_OVERLAY_WATCHED
        #     info = {"Title": title, 'genre' : genre, "Plot": desc, "overlay": overlay, "playCount": 0}
        #     item.setInfo( type='Video', infoLabels=info)
        #     item.setProperty('IsPlayable', 'true')
        #     xbmcplugin.addDirectoryItem(pluginhandle, uri, item, False)

    # set view mode to List2 (quarz3 skin)
    try:
        mode = VIEW_MODES[Addon.getSetting('episodsViewMode')]
        xbmc.executebuiltin("Container.SetViewMode(" + mode +")")
    except Exception, e:
        print "*** Exception"
        print e
        xbmc.executebuiltin('Container.SetViewMode(50)')

    xbmcplugin.endOfDirectory(pluginhandle, True)



def playItem(url):
    item = xbmcgui.ListItem(path = url)
    item.setProperty('mimetype', 'video/x-flv')
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)





# MAIN()
params = get_params()

# TODO: code refactoring
url=None
mode=None
categorie=None
thumbnail=None
page=None

try:
    mode=params['mode'].upper()
except: pass
try:
    url=urllib.unquote_plus(params['url'])
except: pass
try:
    categorie=params['categorie']
except: pass
try:
    thumbnail=urllib.unquote_plus(params['thumbnail'])
except: pass
try:
    page=params['page']
except: pass


if mode == 'RNEXT':
    getRecentItems(url)
elif mode == 'CATEGORIES':
    getCategories(BASE_URL)
elif mode == 'CATEGORIE':
    getCategoryItems(url, categorie, '1')
elif mode == 'CNEXT':
    getCategoryItems(url, categorie, page)
elif mode == 'SHOW':
    showItem(url,thumbnail)
elif mode == 'PLAY':
    playItem(url)
elif mode == 'GENRES':
    listGenres();
elif mode == 'SEARCH':
    search();
elif mode == 'FAVORITES':
    listFavorites();
elif mode == 'RESET':
    resetFavorites();
elif mode == None:
    url = BASE_URL if url == None else url
    getRecentItems(url)

# View modes
# <include>CommonRootView</include> <!-- view id = 50 -->
# <include>FullWidthList</include> <!-- view id = 51 -->
# <include>ThumbnailView</include> <!-- view id = 500 -->
# <include>PosterWrapView</include> <!-- view id = 501 -->
# <include>PosterWrapView2_Fanart</include> <!-- view id = 508 -->
# <include>MediaListView3</include> <!-- view id = 503 -->
# <include>MediaListView2</include> <!-- view id = 504 -->
# <include>WideIconView</include> <!-- view id = 505 -->
# <include>MusicVideoInfoListView</include> <!-- view id = 511 -->
# <include>AddonInfoListView1</include> <!-- view id = 550 -->
# <include>AddonInfoThumbView1</include> <!-- view id = 551 -->
# <include>LiveTVView1</include> <!-- view id = 560 -->
