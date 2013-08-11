import re

from .common import InfoExtractor
from ..utils import (
    ExtractorError,
)


class TeamcocoIE(InfoExtractor):
    _VALID_URL = r'http://teamcoco\.com/video/(?P<url_title>.*)'
    _TEST = {
        'url': 'http://teamcoco.com/video/louis-ck-interview-george-w-bush',
        'file': '19705.mp4',
        'md5': '27b6f7527da5acf534b15f21b032656e',
        'info_dict': {
            "description": "Louis C.K. got starstruck by George W. Bush, so what? Part one.", 
            "title": "Louis C.K. Interview Pt. 1 11/3/11"
        }
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        if mobj is None:
            raise ExtractorError('Invalid URL: %s' % url)
        url_title = mobj.group('url_title')
        webpage = self._download_webpage(url, url_title)

        video_id = self._html_search_regex(r'<article class="video" data-id="(\d+?)"',
            webpage, 'video id')

        self.report_extraction(video_id)

        data_url = 'http://teamcoco.com/cvp/2.0/%s.xml' % video_id
        data = self._download_webpage(data_url, video_id, 'Downloading data webpage')

        video_url = self._html_search_regex(r'<file [^>]*type="high".*?>(.*?)</file>',
            data, 'video URL')

        return [{
            'id':          video_id,
            'url':         video_url,
            'ext':         'mp4',
            'title':       self._og_search_title(webpage),
            'thumbnail':   self._og_search_thumbnail(webpage),
            'description': self._og_search_description(webpage),
        }]
