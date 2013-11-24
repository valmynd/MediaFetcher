import re

from .common import InfoExtractor


class GamekingsIE(InfoExtractor):
    _VALID_URL = r'http?://www\.gamekings\.tv/videos/(?P<name>[0-9a-z\-]+)'
    _TEST = {
        "url": "http://www.gamekings.tv/videos/phoenix-wright-ace-attorney-dual-destinies-review/",
        'file': '20130811.mp4',
        # MD5 is flaky, seems to change regularly
        #u'md5': u'2f32b1f7b80fdc5cb616efb4f387f8a3',
        'info_dict': {
            "title": "Phoenix Wright: Ace Attorney \u2013 Dual Destinies Review",
            "description": "Melle en Steven hebben voor de review een week in de rechtbank doorbracht met Phoenix Wright: Ace Attorney - Dual Destinies.",
        }
    }

    def _real_extract(self, url):

        mobj = re.match(self._VALID_URL, url)
        name = mobj.group('name')
        webpage = self._download_webpage(url, name)
        video_url = self._og_search_video_url(webpage)

        video = re.search(r'[0-9]+', video_url)
        video_id = video.group(0)

        # Todo: add medium format
        video_url = video_url.replace(video_id, 'large/' + video_id)

        return {
            'id': video_id,
            'ext': 'mp4',
            'url': video_url,
            'title': self._og_search_title(webpage),
            'description': self._og_search_description(webpage),
        }
