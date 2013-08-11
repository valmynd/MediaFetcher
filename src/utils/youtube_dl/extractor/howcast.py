import re

from .common import InfoExtractor


class HowcastIE(InfoExtractor):
    _VALID_URL = r'(?:https?://)?(?:www\.)?howcast\.com/videos/(?P<id>\d+)'
    _TEST = {
        'url': 'http://www.howcast.com/videos/390161-How-to-Tie-a-Square-Knot-Properly',
        'file': '390161.mp4',
        'md5': '1d7ba54e2c9d7dc6935ef39e00529138',
        'info_dict': {
            "description": "The square knot, also known as the reef knot, is one of the oldest, most basic knots to tie, and can be used in many different ways. Here's the proper way to tie a square knot.", 
            "title": "How to Tie a Square Knot Properly"
        }
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)

        video_id = mobj.group('id')
        webpage_url = 'http://www.howcast.com/videos/' + video_id
        webpage = self._download_webpage(webpage_url, video_id)

        self.report_extraction(video_id)

        video_url = self._search_regex(r'\'?file\'?: "(http://mobile-media\.howcast\.com/[0-9]+\.mp4)',
            webpage, 'video URL')

        video_title = self._html_search_regex(r'<meta content=(?:"([^"]+)"|\'([^\']+)\') property=\'og:title\'',
            webpage, 'title')

        video_description = self._html_search_regex(r'<meta content=(?:"([^"]+)"|\'([^\']+)\') name=\'description\'',
            webpage, 'description', fatal=False)

        thumbnail = self._html_search_regex(r'<meta content=\'(.+?)\' property=\'og:image\'',
            webpage, 'thumbnail', fatal=False)

        return [{
            'id':       video_id,
            'url':      video_url,
            'ext':      'mp4',
            'title':    video_title,
            'description': video_description,
            'thumbnail': thumbnail,
        }]
