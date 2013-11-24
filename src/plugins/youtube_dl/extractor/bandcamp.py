import json
import re

from .common import InfoExtractor
from ..utils import (
    compat_str,
    compat_urlparse,
    ExtractorError,
)


class BandcampIE(InfoExtractor):
    IE_NAME = 'Bandcamp'
    _VALID_URL = r'http://.*?\.bandcamp\.com/track/(?P<title>.*)'
    _TESTS = [{
        'url': 'http://youtube-dl.bandcamp.com/track/youtube-dl-test-song',
        'file': '1812978515.mp3',
        'md5': 'cdeb30cdae1921719a3cbcab696ef53c',
        'info_dict': {
            "title": "youtube-dl test song \"'/\\\u00e4\u21ad"
        },
        'skip': 'There is a limit of 200 free downloads / month for the test song'
    }]

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        title = mobj.group('title')
        webpage = self._download_webpage(url, title)
        # We get the link to the free download page
        m_download = re.search(r'freeDownloadPage: "(.*?)"', webpage)
        if m_download is None:
            m_trackinfo = re.search(r'trackinfo: (.+),\s*?\n', webpage)
        if m_trackinfo:
            json_code = m_trackinfo.group(1)
            data = json.loads(json_code)

            for d in data:
                formats = [{
                    'format_id': 'format_id',
                    'url': format_url,
                    'ext': format_id.partition('-')[0]
                } for format_id, format_url in sorted(d['file'].items())]
                return {
                    'id': compat_str(d['id']),
                    'title': d['title'],
                    'formats': formats,
                }
        else:
            raise ExtractorError('No free songs found')

        download_link = m_download.group(1)
        id = re.search(r'var TralbumData = {(.*?)id: (?P<id>\d*?)$', 
                       webpage, re.MULTILINE|re.DOTALL).group('id')

        download_webpage = self._download_webpage(download_link, id,
                                                  'Downloading free downloads page')
        # We get the dictionary of the track from some javascrip code
        info = re.search(r'items: (.*?),$',
                         download_webpage, re.MULTILINE).group(1)
        info = json.loads(info)[0]
        # We pick mp3-320 for now, until format selection can be easily implemented.
        mp3_info = info['downloads']['mp3-320']
        # If we try to use this url it says the link has expired
        initial_url = mp3_info['url']
        re_url = r'(?P<server>http://(.*?)\.bandcamp\.com)/download/track\?enc=mp3-320&fsig=(?P<fsig>.*?)&id=(?P<id>.*?)&ts=(?P<ts>.*)$'
        m_url = re.match(re_url, initial_url)
        #We build the url we will use to get the final track url
        # This url is build in Bandcamp in the script download_bunde_*.js
        request_url = '%s/statdownload/track?enc=mp3-320&fsig=%s&id=%s&ts=%s&.rand=665028774616&.vrs=1' % (m_url.group('server'), m_url.group('fsig'), id, m_url.group('ts'))
        final_url_webpage = self._download_webpage(request_url, id, 'Requesting download url')
        # If we could correctly generate the .rand field the url would be
        #in the "download_url" key
        final_url = re.search(r'"retry_url":"(.*?)"', final_url_webpage).group(1)

        track_info = {'id':id,
                      'title' : info['title'],
                      'ext' :   'mp3',
                      'url' :   final_url,
                      'thumbnail' : info['thumb_url'],
                      'uploader' :  info['artist']
                      }

        return [track_info]


class BandcampAlbumIE(InfoExtractor):
    IE_NAME = 'Bandcamp:album'
    _VALID_URL = r'http://.*?\.bandcamp\.com/album/(?P<title>.*)'

    _TEST = {
        'url': 'http://blazo.bandcamp.com/album/jazz-format-mixtape-vol-1',
        'playlist': [
            {
                'file': '1353101989.mp3',
                'md5': '39bc1eded3476e927c724321ddf116cf',
                'info_dict': {
                    'title': 'Intro',
                }
            },
            {
                'file': '38097443.mp3',
                'md5': '1a2c32e2691474643e912cc6cd4bffaa',
                'info_dict': {
                    'title': 'Kero One - Keep It Alive (Blazo remix)',
                }
            },
        ],
        'params': {
            'playlistend': 2
        },
        'skip': 'Bancamp imposes download limits. See test_playlists:test_bandcamp_album for the playlist test'
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        title = mobj.group('title')
        webpage = self._download_webpage(url, title)
        tracks_paths = re.findall(r'<a href="(.*?)" itemprop="url">', webpage)
        if not tracks_paths:
            raise ExtractorError('The page doesn\'t contain any track')
        entries = [
            self.url_result(compat_urlparse.urljoin(url, t_path), ie=BandcampIE.ie_key())
            for t_path in tracks_paths]
        title = self._search_regex(r'album_title : "(.*?)"', webpage, 'title')
        return {
            '_type': 'playlist',
            'title': title,
            'entries': entries,
        }
