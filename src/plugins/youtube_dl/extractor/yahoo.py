import itertools
import json
import re

from .common import InfoExtractor, SearchInfoExtractor
from ..utils import (
    compat_urllib_parse,
    compat_urlparse,
    determine_ext,
    clean_html,
)


class YahooIE(InfoExtractor):
    IE_DESC = 'Yahoo screen'
    _VALID_URL = r'http://screen\.yahoo\.com/.*?-(?P<id>\d*?)\.html'
    _TESTS = [
        {
            'url': 'http://screen.yahoo.com/julian-smith-travis-legg-watch-214727115.html',
            'file': '214727115.mp4',
            'info_dict': {
                'title': 'Julian Smith & Travis Legg Watch Julian Smith',
                'description': 'Julian and Travis watch Julian Smith',
            },
        },
        {
            'url': 'http://screen.yahoo.com/wired/codefellas-s1-ep12-cougar-lies-103000935.html',
            'file': '103000935.flv',
            'info_dict': {
                'title': 'The Cougar Lies with Spanish Moss',
                'description': 'Agent Topple\'s mustache does its dirty work, and Nicole brokers a deal for peace. But why is the NSA collecting millions of Instagram brunch photos? And if your waffles have nothing to hide, what are they so worried about?',
            },
            'params': {
                # Requires rtmpdump
                'skip_download': True,
            },
        },
    ]

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')
        webpage = self._download_webpage(url, video_id)

        items_json = self._search_regex(r'YVIDEO_INIT_ITEMS = ({.*?});$',
            webpage, 'items', flags=re.MULTILINE)
        items = json.loads(items_json)
        info = items['mediaItems']['query']['results']['mediaObj'][0]
        meta = info['meta']

        formats = []
        for s in info['streams']:
            format_info = {
                'width': s.get('width'),
                'height': s.get('height'),
                'bitrate': s.get('bitrate'),
            }

            host = s['host']
            path = s['path']
            if host.startswith('rtmp'):
                format_info.update({
                    'url': host,
                    'play_path': path,
                    'ext': 'flv',
                })
            else:
                format_url = compat_urlparse.urljoin(host, path)
                format_info['url'] = format_url
                format_info['ext'] = determine_ext(format_url)
                
            formats.append(format_info)
        formats = sorted(formats, key=lambda f:(f['height'], f['width']))

        info = {
            'id': video_id,
            'title': meta['title'],
            'formats': formats,
            'description': clean_html(meta['description']),
            'thumbnail': meta['thumbnail'],
        }
        # TODO: Remove when #980 has been merged
        info.update(formats[-1])

        return info


class YahooSearchIE(SearchInfoExtractor):
    IE_DESC = 'Yahoo screen search'
    _MAX_RESULTS = 1000
    IE_NAME = 'screen.yahoo:search'
    _SEARCH_KEY = 'yvsearch'

    def _get_n_results(self, query, n):
        """Get a specified number of results for a query"""

        res = {
            '_type': 'playlist',
            'id': query,
            'entries': []
        }
        for pagenum in itertools.count(0): 
            result_url = 'http://video.search.yahoo.com/search/?p=%s&fr=screen&o=js&gs=0&b=%d' % (compat_urllib_parse.quote_plus(query), pagenum * 30)
            webpage = self._download_webpage(result_url, query,
                                             note='Downloading results page '+str(pagenum+1))
            info = json.loads(webpage)
            m = info['m']
            results = info['results']

            for (i, r) in enumerate(results):
                if (pagenum * 30) +i >= n:
                    break
                mobj = re.search(r'(?P<url>screen\.yahoo\.com/.*?-\d*?\.html)"', r)
                e = self.url_result('http://' + mobj.group('url'), 'Yahoo')
                res['entries'].append(e)
            if (pagenum * 30 +i >= n) or (m['last'] >= (m['total'] -1 )):
                break

        return res
