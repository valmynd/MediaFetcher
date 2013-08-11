import re
import json

from .common import InfoExtractor
from ..utils import (
    determine_ext,
)


class IGNIE(InfoExtractor):
    """
    Extractor for some of the IGN sites, like www.ign.com, es.ign.com de.ign.com.
    Some videos of it.ign.com are also supported
    """

    _VALID_URL = r'https?://.+?\.ign\.com/(?:videos|show_videos)(/.+)?/(?P<name_or_id>.+)'
    IE_NAME = 'ign.com'

    _CONFIG_URL_TEMPLATE = 'http://www.ign.com/videos/configs/id/%s.config'
    _DESCRIPTION_RE = [r'<span class="page-object-description">(.+?)</span>',
                       r'id="my_show_video">.*?<p>(.*?)</p>',
                       ]

    _TEST = {
        'url': 'http://www.ign.com/videos/2013/06/05/the-last-of-us-review',
        'file': '8f862beef863986b2785559b9e1aa599.mp4',
        'md5': 'eac8bdc1890980122c3b66f14bdd02e9',
        'info_dict': {
            'title': 'The Last of Us Review',
            'description': 'md5:c8946d4260a4d43a00d5ae8ed998870c',
        }
    }

    def _find_video_id(self, webpage):
        res_id = [r'data-video-id="(.+?)"',
                  r'<object id="vid_(.+?)"',
                  r'<meta name="og:image" content=".*/(.+?)-(.+?)/.+.jpg"',
                  ]
        return self._search_regex(res_id, webpage, 'video id')

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        name_or_id = mobj.group('name_or_id')
        webpage = self._download_webpage(url, name_or_id)
        video_id = self._find_video_id(webpage)
        result = self._get_video_info(video_id)
        description = self._html_search_regex(self._DESCRIPTION_RE,
                                              webpage, 'video description',
                                              flags=re.DOTALL)
        result['description'] = description
        return result

    def _get_video_info(self, video_id):
        config_url = self._CONFIG_URL_TEMPLATE % video_id
        config = json.loads(self._download_webpage(config_url, video_id,
                            'Downloading video info'))
        media = config['playlist']['media']
        video_url = media['url']

        return {'id': media['metadata']['videoId'],
                'url': video_url,
                'ext': determine_ext(video_url),
                'title': media['metadata']['title'],
                'thumbnail': media['poster'][0]['url'].replace('{size}', 'grande'),
                }


class OneUPIE(IGNIE):
    """Extractor for 1up.com, it uses the ign videos system."""

    _VALID_URL = r'https?://gamevideos.1up.com/video/id/(?P<name_or_id>.+)'
    IE_NAME = '1up.com'

    _DESCRIPTION_RE = r'<div id="vid_summary">(.+?)</div>'

    _TEST = {
        'url': 'http://gamevideos.1up.com/video/id/34976',
        'file': '34976.mp4',
        'md5': '68a54ce4ebc772e4b71e3123d413163d',
        'info_dict': {
            'title': 'Sniper Elite V2 - Trailer',
            'description': 'md5:5d289b722f5a6d940ca3136e9dae89cf',
        }
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        id = mobj.group('name_or_id')
        result = super(OneUPIE, self)._real_extract(url)
        result['id'] = id
        return result
