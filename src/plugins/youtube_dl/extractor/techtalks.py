import re

from .common import InfoExtractor
from ..utils import (
    get_element_by_attribute,
    clean_html,
)


class TechTalksIE(InfoExtractor):
    _VALID_URL = r'https?://techtalks\.tv/talks/[^/]*/(?P<id>\d+)/'

    _TEST = {
        'url': 'http://techtalks.tv/talks/learning-topic-models-going-beyond-svd/57758/',
        'playlist': [
            {
                'file': '57758.flv',
                'info_dict': {
                    'title': 'Learning Topic Models --- Going beyond SVD',
                },
            },
            {
                'file': '57758-slides.flv',
                'info_dict': {
                    'title': 'Learning Topic Models --- Going beyond SVD',
                },
            },
        ],
        'params': {
            # rtmp download
            'skip_download': True,
        },
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        talk_id = mobj.group('id')
        webpage = self._download_webpage(url, talk_id)
        rtmp_url = self._search_regex(r'netConnectionUrl: \'(.*?)\'', webpage,
            'rtmp url')
        play_path = self._search_regex(r'href=\'(.*?)\' [^>]*id="flowplayer_presenter"',
            webpage, 'presenter play path')
        title = clean_html(get_element_by_attribute('class', 'title', webpage))
        video_info = {
                'id': talk_id,
                'title': title,
                'url': rtmp_url,
                'play_path': play_path,
                'ext': 'flv',
            }
        m_slides = re.search(r'<a class="slides" href=\'(.*?)\'', webpage)
        if m_slides is None:
            return video_info
        else:
            return [
                video_info,
                # The slides video
                {
                    'id': talk_id + '-slides',
                    'title': title,
                    'url': rtmp_url,
                    'play_path': m_slides.group(1),
                    'ext': 'flv',
                },
            ]
