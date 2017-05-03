#!/usr/bin/python
# -*- coding: utf-8 -*-
# Writer (c) 2015, Silhouette, E-mail: 
# Rev. 0.8.2

# import pyopenssl
import xbmcplugin, xbmcgui, xbmcaddon
import urllib, urllib2, os, re, sys, json, cookielib
# import requests
from BeautifulSoup import BeautifulSoup
# import YDStreamExtractor
# from YDStreamExtractor.youtube_dl import utils
# from YDStreamExtractor.youtube_dl.extractor import common
# xbmc.log(str(dir(YDStreamExtractor)))


__addon__ = xbmcaddon.Addon(id='plugin.video.jevons.sx')
plugin_path = __addon__.getAddonInfo('path').decode('utf-8')
plugin_icon = __addon__.getAddonInfo('icon')
plugin_fanart = __addon__.getAddonInfo('fanart')

lite_icon = xbmc.translatePath(os.path.join(plugin_path, 'icon2.png'))
jevs_icon = xbmc.translatePath(os.path.join(plugin_path, 'jevs.png'))
pbtv_icon = xbmc.translatePath(os.path.join(plugin_path, 'pb.png'))
pbart_icon = xbmc.translatePath(os.path.join(plugin_path, 'pbart.png'))
art2_icon = xbmc.translatePath(os.path.join(plugin_path, 'fanart2.png'))
icon4_icon = xbmc.translatePath(os.path.join(plugin_path, 'icon4.png'))

dbg = 0

pluginhandle = int(sys.argv[1])

start_pg = "http://jevons.ru"
page_pg = start_pg + "/category/futbol-obzori/page/"
mail_pg = "http://my.mail.ru/mail/jevons/video/"
vk_start = "https://vk.com"
vk_videos = "/videos-"
# vk_oid = '76470207'
# vk_pg = vk_start + "/videos-"+ vk_oid + "?section=playlists"
tvg_oid = '22893032'
gt_oid = '76470207'
fnp_oid = '87879667'
ls_oid = '122493044'
vk_pg = vk_start + vk_videos  # + vk_oid
vk_alv = '/al_video.php'
rfpl_start = "http://rfpl.me"
rfpl_pg = rfpl_start + "/matche/page/"
pbtv_start = "http://www.pressball.by"
pbtv_pg = pbtv_start + "/tv/search/tag?ajax=yw0&q=222-pressbol-TV&TvVideo_page="
vk_vid = "/video-%s_%s"


def reportUsage(addonid, action):
    host = 'xbmc-doplnky.googlecode.com'
    tc = 'UA-3971432-4'
    try:
        utmain.main({'id': addonid, 'host': host, 'tc': tc, 'action': action})
    except:
        pass


def resolve(self, url):
    result = xbmcprovider.XBMCMultiResolverContentProvider.resolve(self, url)
    if result:
        # ping befun.cz GA account
        host = 'befun.cz'
        tc = 'UA-35173050-1'
        try:
            utmain.main({'id': __scriptid__, 'host': host, 'tc': tc, 'action': url})
        except:
            print 'Error sending ping to GA'
            traceback.print_exc()
    return result


def dbg_log(line):
    if dbg: xbmc.log(line)


def get_url(url, data=None, cookie=None, save_cookie=False, referrer=None):
    dbg_log('-get_url:' + '\n')
    dbg_log('- url:' + url + '\n')
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Opera/9.80 (X11; Linux i686; U; ru) Presto/2.7.62 Version/11.00')
    req.add_header('Accept', 'text/html, application/xml, application/xhtml+xml, */*')
    req.add_header('Accept-Language', 'ru,en;q=0.9')
    if cookie: req.add_header('Cookie', cookie)
    if referrer: req.add_header('Referer', referrer)
    if data:
        response = urllib2.urlopen(req, data, timeout=30)
    else:
        response = urllib2.urlopen(req, timeout=30)
    link = response.read()
    if save_cookie:
        setcookie = response.info().get('Set-Cookie', None)
        if setcookie:
            setcookie = re.search('([^=]+=[^=;]+)', setcookie).group(1)
            link = link + '<cookie>' + setcookie + '</cookie>'

    response.close()
    return link


try:
    compat_str = unicode  # Python 2
except NameError:
    compat_str = str
# This is not clearly defined otherwise
compiled_regex_type = type(re.compile(''))

def int_or_none(v, scale=1, default=None, get_attr=None, invscale=1):
    if get_attr:
        if v is not None:
            v = getattr(v, get_attr, None)
    if v == '':
        v = None
    if v is None:
        return default
    try:
        return int(v) * invscale // scale
    except ValueError:
        return default

class VKIE():
    _VALID_URL = r'''(?x)
                    https?://
                        (?:
                            (?:
                                (?:(?:m|new)\.)?vk\.com/video_|
                                (?:www\.)?daxab.com/
                            )
                            ext\.php\?(?P<embed_query>.*?\boid=(?P<oid>-?\d+).*?\bid=(?P<id>\d+).*)|
                            (?:
                                (?:(?:m|new)\.)?vk\.com/(?:.+?\?.*?z=)?video|
                                (?:www\.)?daxab.com/embed/
                            )
                            (?P<videoid>-?\d+_\d+)(?:.*\blist=(?P<list_id>[\da-f]+))?
                        )
                    '''


    def _search_regex(self, pattern, string, name, flags=0, group=None):
        """
        Perform a regex search on the given string, using a single or a list of
        patterns returning the first matching group.
        In case of failure return a default value or raise a WARNING or a
        RegexNotFoundError, depending on fatal, specifying the field name.
        """
        if isinstance(pattern, (str, compat_str, compiled_regex_type)):
            mobj = re.search(pattern, string, flags)
        else:
            for p in pattern:
                mobj = re.search(p, string, flags)
                if mobj:
                    break

        if mobj:
            if group is None:
                # return the first matching group
                return next(g for g in mobj.groups() if g is not None)
            else:
                return mobj.group(group)
        else:
            return None

    def _html_search_regex(self, pattern, string, name, flags=0, group=None):
        """
        Like _search_regex, but strips HTML tags and unescapes entities.
        """
        res = self._search_regex(pattern, string, name, flags, group)
        if res:
            return res.strip()
        else:
            return res

    def _real_extract(self, url):
        dbg_log('-_real_extract:\n')
        dbg_log('-url:' + url + '\n')
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('videoid')
        dbg_log('--video_id:' + video_id + '\n')
        if video_id:
            info_url = 'https://vk.com/al_video.php?act=show&al=1&module=video&video=%s' % video_id
            dbg_log('--info_url:' + info_url + '\n')
            # Some videos (removed?) can only be downloaded with list id specified
            list_id = mobj.group('list_id')
            if list_id:
                info_url += '&list=%s' % list_id
                dbg_log('--info_url:' + info_url + '\n')
        else:
            info_url = 'http://vk.com/video_ext.php?' + mobj.group('embed_query')
            dbg_log('--info_url:' + info_url + '\n')
            video_id = '%s_%s' % (mobj.group('oid'), mobj.group('id'))
            dbg_log('--video_id:' + video_id + '\n')

        info_page = get_url(info_url)

        # dbg_log(str(info_page))

        error_message = self._html_search_regex(
            [r'(?s)<!><div[^>]+class="video_layer_message"[^>]*>(.+?)</div>',
             r'(?s)<div[^>]+id="video_ext_msg"[^>]*>(.+?)</div>'],
            info_page, 'error message')

        if error_message:
            dbg_log('-error_message:\n')
            return None

        if re.search(r'<!>/login\.php\?.*\bact=security_check', info_page):
            dbg_log('-login:\n')
            return None

        m_rutube = re.search(
            r'\ssrc="((?:https?:)?//rutube\.ru\\?/(?:video|play)\\?/embed(?:.*?))\\?"', info_page)
        if m_rutube is not None:
            dbg_log('-rutube:\n')
            return m_rutube.group(1).replace('\\', '')

        m_opts = re.search(r'(?s)var\s+opts\s*=\s*({.+?});', info_page)
        dbg_log('-m_opts:' + str(m_opts) + '\n')
        if m_opts:
            m_opts_url = re.search(r"url\s*:\s*'((?!/\b)[^']+)", m_opts.group(1))
            dbg_log('--m_opts_url:' + m_opts_url + '\n')
            if m_opts_url:
                opts_url = m_opts_url.group(1)
                if opts_url.startswith('//'):
                    opts_url = 'http:' + opts_url
                dbg_log('--opts_url:' + opts_url + '\n')
                return self.url_result(opts_url)

        rdata = self._search_regex(
                r'<!json>\s*({.+?})\s*<!>', info_page, 'json')
        # dbg_log('-rdata:' + str(rdata) + '\n')
        jdata = json.loads(rdata.decode('cp1251').encode('utf-8'))
        data = jdata['player']['params'][0]
        dbg_log('-data:' + str(data) + '\n')
        formats = []
        for format_id, format_url in data.items():
            # dbg_log('-format_id:' + format_id + '\n')
            # dbg_log('-format_url:' + format_url.encode('utf-8') + '\n')
            if not isinstance(format_url, compat_str) or not format_url.startswith(('http', '//', 'rtmp')):
                continue
            if format_id.startswith(('url', 'cache')) or format_id in ('extra_data', 'live_mp4', 'postlive_mp4'):
                height = int_or_none(self._search_regex(
                    r'^(?:url|cache)(\d+)', format_id, 'height'))
                formats.append({
                    'format_id': format_id,
                    'url': format_url,
                    'height': height,
                })
            # elif format_id == 'hls':
            #     formats.extend(self._extract_m3u8_formats(
            #         format_url, video_id, 'mp4', m3u8_id=format_id,
            #         fatal=False, live=True))
            # elif format_id == 'rtmp':
            #     formats.append({
            #         'format_id': format_id,
            #         'url': format_url,
            #         'ext': 'flv',
            #     })
        return self._sort_fid(formats)
        #         self._sort_formats(formats)

    def _sort_fid(self, uslist):
        dbg_log('-_sort_fid:\n')
        dbg_log('-uslist:' + str(uslist)+ '\n')
        nurl = None
        fids = ['url720', 'cache720', 'url480', 'cache480', 'url360', 'cache360', 'url240', 'cache240', 'postlive_mp4']
        for fid in fids:
            for item in uslist:
                if item['format_id'] == fid:
                    dbg_log('- nurl:' + str(nurl) + '\n')
                    nurl = item['url']
                    break

            if nurl != None: break

        return nurl

def reportUsage(addonid, action):
    host = 'xbmc-doplnky.googlecode.com'
    tc = 'UA-3971432-4'
    try:
        utmain.main({'id': addonid, 'host': host, 'tc': tc, 'action': action})
    except:
        pass


def resolve(self, url):
    result = xbmcprovider.XBMCMultiResolverContentProvider.resolve(self, url)
    if result:
        # ping befun.cz GA account
        host = 'befun.cz'
        tc = 'UA-35173050-1'
        try:
            utmain.main({'id': __scriptid__, 'host': host, 'tc': tc, 'action': url})
        except:
            print 'Error sending ping to GA'
            traceback.print_exc()
    return result



def JVS_top():
    dbg_log('-JVS_top:' + '\n')

    #     xbmcplugin.addDirectoryItem(pluginhandle, sys.argv[0] + '?mode=list&url=' + urllib.quote_plus(page_pg), xbmcgui.ListItem('JEVONS.ru', thumbnailImage=jevs_icon), True)
    #    xbmcplugin.addDirectoryItem(pluginhandle, sys.argv[0] + '?mode=mail&url=' + urllib.quote_plus(mail_pg), xbmcgui.ListItem('< MAIL.RU >'), True)
    #    xbmcplugin.addDirectoryItem(pluginhandle, sys.argv[0] + '?mode=vk&url=' + urllib.quote_plus(vk_pg), xbmcgui.ListItem('< VK.COM >'), True)
    item = xbmcgui.ListItem('GOALTIME [vk.com/goaltime ]', iconImage=icon4_icon, thumbnailImage=icon4_icon)
    item.setProperty('fanart_image', art2_icon)
    xbmcplugin.addDirectoryItem(pluginhandle,
                                sys.argv[0] + '?mode=vkalb&oid=' + gt_oid + '&url=' +
                                urllib.quote_plus(vk_pg + gt_oid), item, True)
    item = xbmcgui.ListItem('ЖИВУ ФУТБОЛОМ [vk.com/football_news_pro ]', iconImage=icon4_icon, thumbnailImage=icon4_icon)
    item.setProperty('fanart_image', art2_icon)
    xbmcplugin.addDirectoryItem(pluginhandle,
                                sys.argv[0] + '?mode=vkalb&oid=' + fnp_oid + '&url=' +
                                urllib.quote_plus(vk_pg + fnp_oid), item, True)
    item = xbmcgui.ListItem('ФУТБОЛЬНЫЕ ОБЗОРЫ НА РУССКОМ [vk.com/lifesport ]', iconImage=icon4_icon, thumbnailImage=icon4_icon)
    item.setProperty('fanart_image', art2_icon)
    xbmcplugin.addDirectoryItem(pluginhandle,
                                sys.argv[0] + '?mode=vkalb&oid=' + ls_oid + '&url=' +
                                urllib.quote_plus(vk_pg + ls_oid), item, True)
    item = xbmcgui.ListItem('TVGOAL [vk.com/tvgoal ]', iconImage=icon4_icon, thumbnailImage=icon4_icon)
    item.setProperty('fanart_image', art2_icon)
    xbmcplugin.addDirectoryItem(pluginhandle,
                                sys.argv[0] + '?mode=vkalb&oid=' + tvg_oid + '&url=' +
                                urllib.quote_plus(vk_pg + tvg_oid), item, True)
    item = xbmcgui.ListItem('PRESSBALL.by', iconImage=pbtv_icon, thumbnailImage=pbtv_icon)
    item.setProperty('fanart_image', pbart_icon)
    xbmcplugin.addDirectoryItem(pluginhandle, sys.argv[0] + '?mode=pbtvtop', item, True)

    xbmcplugin.endOfDirectory(pluginhandle)


def JVS_vkalb(url, oid):
    dbg_log('-JVS_vkalb:' + '\n')
    dbg_log('- url:' + url + '\n')

    item = xbmcgui.ListItem('Добавленные', thumbnailImage=icon4_icon)
    item.setProperty('fanart_image', plugin_fanart)
    xbmcplugin.addDirectoryItem(pluginhandle,
                                sys.argv[0] + '?mode=vkshow&oid=' + oid + '&url=' + urllib.quote_plus(vk_videos + oid),
                                item, True)

    http = get_url(url)
    ap = re.compile('{"albumsPreload":{(.*?):\[\[(.*?)\]\]}').findall(http)[0]
    entries = re.compile('\[(.*?),(.*?),(.*?),(.*?),(.*?),(.*?),(.*?)\]').findall('[' + ap[1] + ']')
    for en in entries:
        title = en[0].strip('"').strip("'").replace('\/', '/').decode('cp1251').encode('utf-8')
        img = en[2].strip('"').strip("'").replace('\/', '/')
        href = en[3].strip('"').strip("'").replace('\/', '/')

        if href != "":
            item = xbmcgui.ListItem(title, thumbnailImage=img)
            item.setProperty('fanart_image', plugin_fanart)
            xbmcplugin.addDirectoryItem(pluginhandle,
                                        sys.argv[0] + '?mode=vkshow&oid=' + oid + '&url=' + urllib.quote_plus(href),
                                        item, True)

        dbg_log('- title:' + title + '\n')
        dbg_log('- img:' + img + '\n')
        dbg_log('- href:' + href + '\n')

    xbmcplugin.endOfDirectory(pluginhandle)


def JVS_vkshow(url, page, oid):
    dbg_log('-JVS_vkshow:' + '\n')
    dbg_log('- url:' + url + '\n')
    dbg_log('- page:' + page + '\n')

    http = get_url(vk_start + url)

    try:
        sect = url.split('=')[1]
        pdata = 'act=load_videos_silent&al=1&extended=0&offset=0&oid=-' + oid + '&section=' + sect
        hpost = get_url(vk_start + vk_alv, data=pdata, referrer=vk_start + url)
        slist = "list"
    except:
        hpost = http
        slist = "list"

    # print hpost.replace('],[', '],\n[').decode('cp1251').encode('utf-8')
    dbg_log('- slist:' + slist + '\n')
    if 1:
        pv = re.compile('"' + slist + '":\[\[(.*?)\]\]').findall(hpost)[0]
        #        print pv.replace('],[', '],\n[').decode('cp1251').encode('utf-8')
        entries = re.compile('\[(.*?),(.*?),(.*?),(.*?),(.*?),(.*?),(.*?),(.*?),(.*?),(.*?),(.*?)\]').findall(
            '[' + pv + ']')
        for entry in entries:
            #             print entry
            try:
                ht = "/video-%s_%s" % (oid, entry[1])
                href = vk_start + ht
                title = entry[3].decode('cp1251').encode('utf-8').replace('\/', '/').strip('"')
                img = entry[2].replace('\/', '/').strip('"')
            # if entry[19].find('rutube') != -1: href = ''
            except:
                href = ''
                title = ''
                img = lite_icon

            dbg_log('-HREF %s' % href)
            dbg_log('-TITLE %s' % title)
            dbg_log('-IMG %s' % img)

            if href != '':
                item = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
                item.setInfo(type='video', infoLabels={'title': title, 'plot': title})
                uri = sys.argv[0] + '?mode=play' + '&url=' + urllib.quote_plus(href) + '&name=' + urllib.quote_plus(
                    title)
                item.setProperty('IsPlayable', 'true')
                item.setProperty('fanart_image', plugin_fanart)
                xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
                dbg_log('- uri:' + uri + '\n')
    else:
        rinfos = BeautifulSoup(http).findAll('div', {"class": "video_row_info"})

        for rows in rinfos:
            row = BeautifulSoup(str(rows)).findAll('div', {"class": "video_row_info_name"})

            #         href = vk_start + re.compile('<a href="(.*?)"').findall(str(row))[0]
            #         title = re.compile('<a *?>(.*?)</a>').findall(str(row))[0].strip()
            try:
                ht = \
                re.compile('<a href="(.*?)"(.*?)">(.*?)</a>').findall(str(row).replace('\n', '').replace('\r', ''))[0]
                href = vk_start + ht[0]
                title = ht[2].strip()
            except:
                href = ''
                title = ''
            img = lite_icon

            dbg_log('-HREF %s' % href)
            dbg_log('-TITLE %s' % title)
            dbg_log('-IMG %s' % img)

            if href != '':
                item = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
                item.setInfo(type='video', infoLabels={'title': title, 'plot': title})
                uri = sys.argv[0] + '?mode=play' + '&url=' + urllib.quote_plus(href) + '&name=' + urllib.quote_plus(
                    title)
                item.setProperty('IsPlayable', 'true')
                item.setProperty('fanart_image', plugin_fanart)
                xbmcplugin.addDirectoryItem(pluginhandle, uri, item, False)
                dbg_log('- uri:' + uri + '\n')

    xbmcplugin.endOfDirectory(pluginhandle)


def JVS_list(url, page):
    dbg_log('-JVS_list:' + '\n')
    dbg_log('- url:' + url + '\n')
    dbg_log('- page:' + page + '\n')

    http = get_url(url + page + '/')

    i = 0

    entrys = re.compile(' <a title="(.*?)" href="(.*?)">').findall(http)

    for title, href in entrys:
        img = jevs_icon
        dbg_log('-HREF %s' % href)
        dbg_log('-TITLE %s' % title)
        dbg_log('-IMG %s' % img)

        item = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
        item.setInfo(type='video', infoLabels={'title': title, 'plot': title})
        item.setProperty('fanart_image', plugin_fanart)
        uri = sys.argv[0] + '?mode=show' + '&url=' + urllib.quote_plus(href) + '&name=' + urllib.quote_plus(title)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
        dbg_log('- uri:' + uri + '\n')
        i = i + 1

    if i:
        item = xbmcgui.ListItem('<NEXT PAGE>')
        uri = sys.argv[0] + '?mode=list&page=' + str(int(page) + 1)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
        dbg_log('- uri:' + uri + '\n')
        item = xbmcgui.ListItem('<NEXT PAGE +5>')
        item.setProperty('fanart_image', plugin_fanart)
        uri = sys.argv[0] + '?mode=list&page=' + str(int(page) + 5)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
        dbg_log('- uri:' + uri + '\n')

    xbmcplugin.endOfDirectory(pluginhandle)


def JVS_pbtvtop():
    dbg_log('-JVS_pbyvtop:' + '\n')

    pbtop = [("Прессбол-TV", "/tv/search/tag?q=222-pressbol-TV&TvVideo_page="),
             ("Футбол", "/tv/search/tag?q=41-futbol&TvVideo_page="),
             ("Чемпионат Беларуси", "/tv/search/tag?q=319-chempionat-belarusi&TvVideo_page="),
             ("Опять по пятницам", "/tv/search/tag?q=264-opyat'-po-pyatnicam&TvVideo_page="),
             ("На футболе", "/tv/streams/36?TvVideo_page="),
             ("Судите с нами", "/tv/search/tag?q=267-sudite-s-nami&TvVideo_page=")]

    for title, url in pbtop:
        item = xbmcgui.ListItem(title, iconImage=pbtv_icon, thumbnailImage=pbtv_icon)
        item.setProperty('fanart_image', pbart_icon)
        xbmcplugin.addDirectoryItem(pluginhandle, sys.argv[0] + '?mode=pbtv&url=' + urllib.quote_plus(pbtv_start + url),
                                    item , True)

    xbmcplugin.endOfDirectory(pluginhandle)


def JVS_pbtv(url, page):
    dbg_log('-JVS_pbtv:' + '\n')
    dbg_log('- url:' + url + '\n')
    dbg_log('- page:' + page + '\n')

    http = get_url(url + page)

    i = 0

    panels = BeautifulSoup(http).findAll('div', {"class": "item"})

    for panel in panels:
        #        print panel
        psoup = BeautifulSoup(str(panel))

        sref = str(panel).replace('\r', '').replace('\n', '')
        #        print sref
        try:
            href = re.compile("href='(.*?)'").findall(sref)[0].strip()
        except:
            href = re.compile('href="(.*?)"').findall(sref)[0].strip()
        # href = str(psoup.a['href'])
        salt = str(psoup.img).replace('\r', '').replace('\n', '')
        try:
            title = re.compile("alt='(.*?)'").findall(salt)[0].strip()
        except:
            title = re.compile('alt="(.*?)"').findall(salt)[0].strip()

        img = pbtv_start + str(psoup.img['src']).replace('\r', '').replace('\n', '').strip()

        if title != "":
            dbg_log('-HREF %s' % href)
            dbg_log('-IMG %s' % img)
            dbg_log('-TITLE %s' % title)

            item = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
            item.setInfo(type='video', infoLabels={'title': title, 'plot': title})
            item.setProperty('fanart_image', pbart_icon)
            uri = sys.argv[0] + '?mode=playpbtv' + '&url=' + urllib.quote_plus(href) + '&name=' + urllib.quote_plus(
                title)
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
            dbg_log('- uri:' + uri + '\n')
            i = i + 1

    next = BeautifulSoup(http).findAll('li', {"class": "next"})

    if next:
        item = xbmcgui.ListItem('<NEXT PAGE>')
        item.setProperty('fanart_image', pbart_icon)
        uri = sys.argv[0] + '?page=' + str(int(page) + 1) + '&mode=pbtv&url=' + urllib.quote_plus(url)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
        dbg_log('- uri:' + uri + '\n')

    xbmcplugin.endOfDirectory(pluginhandle)


def get_rutube(url, videoId=None):
    dbg_log('-get_rutube:' + '\n')
    dbg_log('- url-in:' + url + '\n')
    c = 0
    if not videoId:
        if 'rutube.ru' in url:
            try:
                videoId = re.findall('rutube.ru/play/embed/(.*?)"', url)[0]
            except:
                try:
                    videoId = re.findall('rutube.ru/video/(.*?)/', url)[0]
                except:
                    pass

    if videoId:
        url = 'http://rutube.ru/api/play/options/' + videoId + '?format=json'
        dbg_log('- url-req:' + url + '\n')
        request = urllib2.Request(url)
        request.add_header('User-agent',
                           'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36')
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
    dbg_log('- url-in:' + url + '\n')
    if not videoID:
        if 'rutube.ru/play/embed/' in url:
            try:
                videoId = re.findall('rutube.ru/play/embed/(.*?)"', url)[0]
            except:
                pass
    if videoID:
        url = 'http://rutube.ru/api/play/options/' + videoId + '?format=json'
        request = urllib2.Request(url)
        request.add_header('User-agent',
                           'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36')
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
    dbg_log('- url-in:' + url + '\n')
    result = get_url(url)
    jdata = urllib.unquote_plus(result).replace('&quot;', '"').replace('&amp;', '&')
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

        dbg_log('- url-out:' + url + '\n')
    except:
        url = None
    return url


def get_VK(url, n = 0):
    dbg_log('-get_VK:' + '\n')
    dbg_log('- url:' + url + '\n')

    newVK = VKIE()
    nurl = newVK._real_extract(url)

    if 'rutube' in nurl:
        nurl = get_rutube(nurl.replace('?','"'))

    return nurl


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
    vid = YDStreamExtractor.getVideoInfo(url, resolve_redirects=True)

    dbg_log('- YTD: \n')
    if vid:
        dbg_log('- YTD: Try\n')
        stream_url = vid.streamURL()
        #         stream_url = vid.streamURL().split('|')[0]
        dbg_log('- surl:' + stream_url + '\n')
        if stream_url.find('rutube') > -1:
            dbg_log('- rutube\n')
            streams = vid.streams()
            #            dbg_log('- id1:'+str(streams)+'\n')
            #            dbg_log('- id1:'+str(streams[0]['ytdl_format'])+'\n')
            #            dbg_log('- id1:'+str(streams[0]['ytdl_format']['id'])+'\n')
            id = ''
            try:
                id = streams[0]['ytdl_format']['id']
            except:
                pass
            dbg_log('- id1:' + id + '\n')
            if id == '':
                try:
                    id = streams[0]['ytdl_format']['webpage_url_basename']
                except:
                    pass
            dbg_log('- id2:' + id + '\n')
            if id == '':
                try:
                    id = streams[0]['ytdl_format']['display_id']
                except:
                    pass
            dbg_log('- id3:' + id + '\n')
            if id != '':
                return get_rutube(url, id);
            else:
                return None

        return stream_url
    else:
        dbg_log('- YTD: None\n')
        return None


def touch(url):
    req = urllib2.Request(url)
    try:
        res = urllib2.urlopen(req)
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
    mycookie = get_url(url, save_cookie=True)
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
    url += [{'quality': 'SD', 'url': i['url'] + h} for i in result if not (i['key'] == '1080p' or i['key'] == '720p')]

    if url == []: return None
    return url
    #    except:
    return None


def JVS_show(url, name):
    nurl = start_pg + url
    dbg_log('-JVS_show:' + '\n')
    dbg_log('- url:' + nurl + '\n')

    http = get_url(nurl)

    entrys = re.compile('<iframe src="(.*?)"').findall(http)

    for href in entrys:
        img = jevs_icon
        dbg_log('-HREF %s' % href)

        if 'cityadspix' not in href:
            try:
                rsrc = re.compile('//(.*?)/').findall(href)
                #                print rsrc
                lsrc = rsrc[0].split('.')
                #                print lsrc
                lens = len(lsrc)
                #                print lens
                if lens > 1:
                    title = '[%s.%s]~%s' % (lsrc[lens - 2], lsrc[lens - 1], name)
                else:
                    title = name
            except:
                title = name

            if 'http' not in href: href = 'http:' + href
            item = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
            item.setInfo(type='video', infoLabels={'title': title, 'plot': title})
            uri = sys.argv[0] + '?mode=play' + '&url=' + urllib.quote_plus(href) + '&name=' + urllib.quote_plus(title)
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, False)
            dbg_log('- uri:' + uri + '\n')

    xbmcplugin.endOfDirectory(pluginhandle)


def JVS_play(url, title):
    url = url.replace('&amp;', '&')

    dbg_log('-JVS_play:' + '\n')
    dbg_log('- url:' + url + '\n')
    dbg_log('- title:' + title + '\n')
    uri = None

    if url.find('videoapi.my.mail.ru') > -1:
        quals = get_mailru(url)
        for d in quals:
            try:
                if d['quality'] == 'HD':
                    uri = d['url']
                    break
                if d['quality'] == '1080p':
                    uri = d['url']
                    break
                if d['quality'] == 'SD':
                    uri = d['url']
                    break
            except:
                pass

    elif url.find('vkontakte.ru') > -1:
        uri = get_VK(url)
    elif url.find('vk.com') > -1:
        #         uri = get_YTD(url)
        uri = get_VK(url)
    elif url.find('rutube') > -1:
        uri = get_rutube(url)

    if uri != None and uri != False:
        if not uri.startswith('http'): uri = 'http:' + uri
        uri = urllib.unquote_plus(uri)
        dbg_log('- uri: ' + uri + '\n')
        try:
            name = title[(title.find('~') + 1):]
        except:
            name = title
        item = xbmcgui.ListItem(path=uri)
        if 0:
            xbmcplugin.setResolvedUrl(pluginhandle, True, item)
        else:
            sPlayer = xbmc.Player()
            item.setInfo(type='Video', infoLabels={'title': name})
            item.setProperty('IsPlayable', 'true')
            sPlayer.play(uri, item)


def JVS_playpbtv(url, title):
    url = urllib.unquote_plus(url.replace('&amp;', '&'))
    if pbtv_start not in url:
        url = pbtv_start + url
    dbg_log('-JVS_playpbtv:' + '\n')
    dbg_log('- url:' + url + '\n')

    http = get_url(url)
    uri = pbtv_start + re.compile('file: "(.*?)"').findall(http)[0]

    dbg_log('- uri: ' + uri + '\n')
    name = title
    item = xbmcgui.ListItem(label=name, path=uri)
    #    xbmcplugin.setResolvedUrl(pluginhandle, True, item)

    sPlayList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    sPlayer = xbmc.Player()
    sPlayList.clear()
    item.setProperty('mimetype', 'video/x-msvideo')
    item.setProperty('IsPlayable', 'true')
    item.setInfo(type='video', infoLabels={'title': name})
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
    param = []
    # print sys.argv[2]
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    return param


params = get_params()
mode = params['mode'] if 'mode' in params else ''
page = params['page'] if 'page' in params else '1'
oid = params['oid'] if 'oid' in params else ''
name = urllib.unquote_plus(params['name']) if 'name' in params else ''
url = urllib.unquote_plus(params['url']) if 'url' in params else page_pg

if mode == '':
    JVS_top()
# if mode == '': JVS_list(url, page)
elif mode == 'list':
    JVS_list(url, page)
elif mode == 'vkalb':
    JVS_vkalb(url, oid)
elif mode == 'pbtvtop':
    JVS_pbtvtop()
elif mode == 'pbtv':
    JVS_pbtv(url, page)
elif mode == 'play':
    JVS_play(url, name)
elif mode == 'playpbtv':
    JVS_playpbtv(url, name)
elif mode == 'show':
    JVS_show(url, name)
elif mode == 'vkshow':
    JVS_vkshow(url, name, oid)
elif mode == 'mail':
    JVS_mail(url)
elif mode == 'vk':
    JVS_vk(url)

