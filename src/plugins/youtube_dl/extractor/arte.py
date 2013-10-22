# encoding: utf-8
import re
import json
import xml.etree.ElementTree

from .common import InfoExtractor
from ..utils import (
    ExtractorError,
    find_xpath_attr,
    unified_strdate,
    determine_ext,
    get_element_by_id,
)

# There are different sources of video in arte.tv, the extraction process 
# is different for each one. The videos usually expire in 7 days, so we can't
# add tests.

class ArteTvIE(InfoExtractor):
    _VIDEOS_URL = r'(?:http://)?videos.arte.tv/(?P<lang>fr|de)/.*-(?P<id>.*?).html'
    _LIVEWEB_URL = r'(?:http://)?liveweb.arte.tv/(?P<lang>fr|de)/(?P<subpage>.+?)/(?P<name>.+)'
    _LIVE_URL = r'index-[0-9]+\.html$'

    IE_NAME = 'arte.tv'

    @classmethod
    def suitable(cls, url):
        return any(re.match(regex, url) for regex in (cls._VIDEOS_URL, cls._LIVEWEB_URL))

    # TODO implement Live Stream
    # from ..utils import compat_urllib_parse
    # def extractLiveStream(self, url):
    #     video_lang = url.split('/')[-4]
    #     info = self.grep_webpage(
    #         url,
    #         r'src="(.*?/videothek_js.*?\.js)',
    #         0,
    #         [
    #             (1, 'url', u'Invalid URL: %s' % url)
    #         ]
    #     )
    #     http_host = url.split('/')[2]
    #     next_url = 'http://%s%s' % (http_host, compat_urllib_parse.unquote(info.get('url')))
    #     info = self.grep_webpage(
    #         next_url,
    #         r'(s_artestras_scst_geoFRDE_' + video_lang + '.*?)\'.*?' +
    #             '(http://.*?\.swf).*?' +
    #             '(rtmp://.*?)\'',
    #         re.DOTALL,
    #         [
    #             (1, 'path',   u'could not extract video path: %s' % url),
    #             (2, 'player', u'could not extract video player: %s' % url),
    #             (3, 'url',    u'could not extract video url: %s' % url)
    #         ]
    #     )
    #     video_url = u'%s/%s' % (info.get('url'), info.get('path'))

    def _real_extract(self, url):
        mobj = re.match(self._VIDEOS_URL, url)
        if mobj is not None:
            id = mobj.group('id')
            lang = mobj.group('lang')
            return self._extract_video(url, id, lang)

        mobj = re.match(self._LIVEWEB_URL, url)
        if mobj is not None:
            name = mobj.group('name')
            lang = mobj.group('lang')
            return self._extract_liveweb(url, name, lang)

        if re.search(self._LIVE_URL, video_id) is not None:
            raise ExtractorError('Arte live streams are not yet supported, sorry')
            # self.extractLiveStream(url)
            # return

    def _extract_video(self, url, video_id, lang):
        """Extract from videos.arte.tv"""
        ref_xml_url = url.replace('/videos/', '/do_delegate/videos/')
        ref_xml_url = ref_xml_url.replace('.html', ',view,asPlayerXml.xml')
        ref_xml = self._download_webpage(ref_xml_url, video_id, note='Downloading metadata')
        ref_xml_doc = xml.etree.ElementTree.fromstring(ref_xml)
        config_node = find_xpath_attr(ref_xml_doc, './/video', 'lang', lang)
        config_xml_url = config_node.attrib['ref']
        config_xml = self._download_webpage(config_xml_url, video_id, note='Downloading configuration')

        video_urls = list(re.finditer(r'<url quality="(?P<quality>.*?)">(?P<url>.*?)</url>', config_xml))
        def _key(m):
            quality = m.group('quality')
            if quality == 'hd':
                return 2
            else:
                return 1
        # We pick the best quality
        video_urls = sorted(video_urls, key=_key)
        video_url = list(video_urls)[-1].group('url')
        
        title = self._html_search_regex(r'<name>(.*?)</name>', config_xml, 'title')
        thumbnail = self._html_search_regex(r'<firstThumbnailUrl>(.*?)</firstThumbnailUrl>',
                                            config_xml, 'thumbnail')
        return {'id': video_id,
                'title': title,
                'thumbnail': thumbnail,
                'url': video_url,
                'ext': 'flv',
                }

    def _extract_liveweb(self, url, name, lang):
        """Extract form http://liveweb.arte.tv/"""
        webpage = self._download_webpage(url, name)
        video_id = self._search_regex(r'eventId=(\d+?)("|&)', webpage, 'event id')
        config_xml = self._download_webpage('http://download.liveweb.arte.tv/o21/liveweb/events/event-%s.xml' % video_id,
                                            video_id, 'Downloading information')
        config_doc = xml.etree.ElementTree.fromstring(config_xml.encode('utf-8'))
        event_doc = config_doc.find('event')
        url_node = event_doc.find('video').find('urlHd')
        if url_node is None:
            url_node = video_doc.find('urlSd')

        return {'id': video_id,
                'title': event_doc.find('name%s' % lang.capitalize()).text,
                'url': url_node.text.replace('MP4', 'mp4'),
                'ext': 'flv',
                'thumbnail': self._og_search_thumbnail(webpage),
                }


class ArteTVPlus7IE(InfoExtractor):
    IE_NAME = 'arte.tv:+7'
    _VALID_URL = r'https?://www\.arte.tv/guide/(?P<lang>fr|de)/(?:(?:sendungen|emissions)/)?(?P<id>.*?)/(?P<name>.*?)(\?.*)?'

    @classmethod
    def _extract_url_info(cls, url):
        mobj = re.match(cls._VALID_URL, url)
        lang = mobj.group('lang')
        # This is not a real id, it can be for example AJT for the news
        # http://www.arte.tv/guide/fr/emissions/AJT/arte-journal
        video_id = mobj.group('id')
        return video_id, lang

    def _real_extract(self, url):
        video_id, lang = self._extract_url_info(url)
        webpage = self._download_webpage(url, video_id)
        return self._extract_from_webpage(webpage, video_id, lang)

    def _extract_from_webpage(self, webpage, video_id, lang):
        json_url = self._html_search_regex(r'arte_vp_url="(.*?)"', webpage, 'json url')

        json_info = self._download_webpage(json_url, video_id, 'Downloading info json')
        self.report_extraction(video_id)
        info = json.loads(json_info)
        player_info = info['videoJsonPlayer']

        info_dict = {
            'id': player_info['VID'],
            'title': player_info['VTI'],
            'description': player_info.get('VDE'),
            'upload_date': unified_strdate(player_info.get('VDA', '').split(' ')[0]),
            'thumbnail': player_info.get('programImage') or player_info.get('VTU', {}).get('IUR'),
        }

        formats = list(player_info['VSR'].values())
        def _match_lang(f):
            if f.get('versionCode') is None:
                return True
            # Return true if that format is in the language of the url
            if lang == 'fr':
                l = 'F'
            elif lang == 'de':
                l = 'A'
            regexes = [r'VO?%s' % l, r'VO?.-ST%s' % l]
            return any(re.match(r, f['versionCode']) for r in regexes)
        # Some formats may not be in the same language as the url
        formats = list(filter(_match_lang, formats))
        # Some formats use the m3u8 protocol
        formats = [f for f in formats if f.get('videoFormat') != 'M3U8']
        # We order the formats by quality
        formats = list(formats) # in python3 filter returns an iterator
        if re.match(r'[A-Z]Q', formats[0]['quality']) is not None:
            sort_key = lambda f: ['HQ', 'MQ', 'EQ', 'SQ'].index(f['quality'])
        else:
            sort_key = lambda f: int(f.get('height',-1))
        formats = sorted(formats, key=sort_key)
        # Prefer videos without subtitles in the same language
        formats = sorted(formats, key=lambda f: re.match(r'VO(F|A)-STM\1', f.get('versionCode', '')) is None)
        # Pick the best quality
        def _format(format_info):
            quality = format_info['quality']
            m_quality = re.match(r'\w*? - (\d*)p', quality)
            if m_quality is not None:
                quality = m_quality.group(1)
            if format_info.get('versionCode') is not None:
                format_id = '%s-%s' % (quality, format_info['versionCode'])
            else:
                format_id = quality
            info = {
                'format_id': format_id,
                'format_note': format_info.get('versionLibelle'),
                'width': format_info.get('width'),
                'height': format_info.get('height'),
            }
            if format_info['mediaType'] == 'rtmp':
                info['url'] = format_info['streamer']
                info['play_path'] = 'mp4:' + format_info['url']
                info['ext'] = 'flv'
            else:
                info['url'] = format_info['url']
                info['ext'] = determine_ext(info['url'])
            return info
        info_dict['formats'] = [_format(f) for f in formats]

        return info_dict


# It also uses the arte_vp_url url from the webpage to extract the information
class ArteTVCreativeIE(ArteTVPlus7IE):
    IE_NAME = 'arte.tv:creative'
    _VALID_URL = r'https?://creative\.arte\.tv/(?P<lang>fr|de)/magazine?/(?P<id>.+)'

    _TEST = {
        'url': 'http://creative.arte.tv/de/magazin/agentur-amateur-corporate-design',
        'file': '050489-002.mp4',
        'info_dict': {
            'title': 'Agentur Amateur #2 - Corporate Design',
        },
    }


class ArteTVFutureIE(ArteTVPlus7IE):
    IE_NAME = 'arte.tv:future'
    _VALID_URL = r'https?://future\.arte\.tv/(?P<lang>fr|de)/(thema|sujet)/.*?#article-anchor-(?P<id>\d+)'

    _TEST = {
        'url': 'http://future.arte.tv/fr/sujet/info-sciences#article-anchor-7081',
        'file': '050940-003.mp4',
        'info_dict': {
            'title': 'Les champignons au secours de la planète',
        },
    }

    def _real_extract(self, url):
        anchor_id, lang = self._extract_url_info(url)
        webpage = self._download_webpage(url, anchor_id)
        row = get_element_by_id(anchor_id, webpage)
        return self._extract_from_webpage(row, anchor_id, lang)
