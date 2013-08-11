import json
import re

from .common import InfoExtractor
from ..utils import (
    compat_str,
    compat_urllib_parse,

    ExtractorError,
)


class EscapistIE(InfoExtractor):
    _VALID_URL = r'^(https?://)?(www\.)?escapistmagazine\.com/videos/view/(?P<showname>[^/]+)/(?P<episode>[^/?]+)[/?]?.*$'
    _TEST = {
        'url': 'http://www.escapistmagazine.com/videos/view/the-escapist-presents/6618-Breaking-Down-Baldurs-Gate',
        'file': '6618-Breaking-Down-Baldurs-Gate.mp4',
        'md5': 'c6793dbda81388f4264c1ba18684a74d',
        'info_dict': {
            "description": "Baldur's Gate: Original, Modded or Enhanced Edition? I'll break down what you can expect from the new Baldur's Gate: Enhanced Edition.", 
            "uploader": "the-escapist-presents", 
            "title": "Breaking Down Baldur's Gate"
        }
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        if mobj is None:
            raise ExtractorError('Invalid URL: %s' % url)
        showName = mobj.group('showname')
        videoId = mobj.group('episode')

        self.report_extraction(videoId)
        webpage = self._download_webpage(url, videoId)

        videoDesc = self._html_search_regex('<meta name="description" content="([^"]*)"',
            webpage, 'description', fatal=False)

        playerUrl = self._og_search_video_url(webpage, name='player url')

        title = self._html_search_regex('<meta name="title" content="([^"]*)"',
            webpage, 'player url').split(' : ')[-1]

        configUrl = self._search_regex('config=(.*)$', playerUrl, 'config url')
        configUrl = compat_urllib_parse.unquote(configUrl)

        configJSON = self._download_webpage(configUrl, videoId,
                                            'Downloading configuration',
                                            'unable to download configuration')

        # Technically, it's JavaScript, not JSON
        configJSON = configJSON.replace("'", '"')

        try:
            config = json.loads(configJSON)
        except (ValueError,) as err:
            raise ExtractorError('Invalid JSON in configuration file: ' + compat_str(err))

        playlist = config['playlist']
        videoUrl = playlist[1]['url']

        info = {
            'id': videoId,
            'url': videoUrl,
            'uploader': showName,
            'upload_date': None,
            'title': title,
            'ext': 'mp4',
            'thumbnail': self._og_search_thumbnail(webpage),
            'description': videoDesc,
            'player_url': playerUrl,
        }

        return [info]
