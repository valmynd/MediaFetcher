# -*- coding: utf-8 -*-

import re

from .common import InfoExtractor
from ..utils import determine_ext


class SztvHuIE(InfoExtractor):
    _VALID_URL = r'(?:http://)?(?:(?:www\.)?sztv\.hu|www\.tvszombathely\.hu)/(?:[^/]+)/.+-(?P<id>[0-9]+)'
    _TEST = {
        'url': 'http://sztv.hu/hirek/cserkeszek-nepszerusitettek-a-kornyezettudatos-eletmodot-a-savaria-teren-20130909',
        'file': '20130909.mp4',
        'md5': 'a6df607b11fb07d0e9f2ad94613375cb',
        'info_dict': {
            "title": "Cserkészek népszerűsítették a környezettudatos életmódot a Savaria téren",
            "description": 'A zöld nap játékos ismeretterjesztő programjait a Magyar Cserkész Szövetség szervezte, akik az ország nyolc városában adják át tudásukat az érdeklődőknek. A PET...',
        },
        'skip': 'Service temporarily disabled as of 2013-11-20'
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')
        webpage = self._download_webpage(url, video_id)
        video_file = self._search_regex(
            r'file: "...:(.*?)",', webpage, 'video file')
        title = self._html_search_regex(
            r'<meta name="title" content="([^"]*?) - [^-]*? - [^-]*?"',
            webpage, 'video title')
        description = self._html_search_regex(
            r'<meta name="description" content="([^"]*)"/>',
            webpage, 'video description', fatal=False)
        thumbnail = self._og_search_thumbnail(webpage)

        video_url = 'http://media.sztv.hu/vod/' + video_file

        return {
            'id': video_id,
            'url': video_url,
            'title': title,
            'ext': determine_ext(video_url),
            'description': description,
            'thumbnail': thumbnail,
        }
