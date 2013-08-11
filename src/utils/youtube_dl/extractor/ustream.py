import re

from .common import InfoExtractor


class UstreamIE(InfoExtractor):
    _VALID_URL = r'https?://www\.ustream\.tv/recorded/(?P<videoID>\d+)'
    IE_NAME = 'ustream'
    _TEST = {
        'url': 'http://www.ustream.tv/recorded/20274954',
        'file': '20274954.flv',
        'md5': '088f151799e8f572f84eb62f17d73e5c',
        'info_dict': {
            "uploader": "Young Americans for Liberty", 
            "title": "Young Americans for Liberty February 7, 2012 2:28 AM"
        }
    }

    def _real_extract(self, url):
        m = re.match(self._VALID_URL, url)
        video_id = m.group('videoID')

        video_url = 'http://tcdn.ustream.tv/video/%s' % video_id
        webpage = self._download_webpage(url, video_id)

        self.report_extraction(video_id)

        video_title = self._html_search_regex(r'data-title="(?P<title>.+)"',
            webpage, 'title')

        uploader = self._html_search_regex(r'data-content-type="channel".*?>(?P<uploader>.*?)</a>',
            webpage, 'uploader', fatal=False, flags=re.DOTALL)

        thumbnail = self._html_search_regex(r'<link rel="image_src" href="(?P<thumb>.*?)"',
            webpage, 'thumbnail', fatal=False)

        info = {
                'id': video_id,
                'url': video_url,
                'ext': 'flv',
                'title': video_title,
                'uploader': uploader,
                'thumbnail': thumbnail,
               }
        return info
