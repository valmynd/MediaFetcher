import json
import re

from .common import InfoExtractor
from ..utils import (
    compat_str,
    compat_urllib_parse,

    ExtractorError,
)


class EscapistIE(InfoExtractor):
    _VALID_URL = r'^https?://?(www\.)?escapistmagazine\.com/videos/view/(?P<showname>[^/]+)/(?P<episode>[^/?]+)[/?]?.*$'
    _TEST = {
        'url': 'http://www.escapistmagazine.com/videos/view/the-escapist-presents/6618-Breaking-Down-Baldurs-Gate',
        'file': '6618-Breaking-Down-Baldurs-Gate.mp4',
        'md5': 'ab3a706c681efca53f0a35f1415cf0d1',
        'info_dict': {
            "description": "Baldur's Gate: Original, Modded or Enhanced Edition? I'll break down what you can expect from the new Baldur's Gate: Enhanced Edition.", 
            "uploader": "the-escapist-presents", 
            "title": "Breaking Down Baldur's Gate"
        }
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        showName = mobj.group('showname')
        videoId = mobj.group('episode')

        self.report_extraction(videoId)
        webpage = self._download_webpage(url, videoId)

        videoDesc = self._html_search_regex(
            r'<meta name="description" content="([^"]*)"',
            webpage, 'description', fatal=False)

        playerUrl = self._og_search_video_url(webpage, name='player URL')

        title = self._html_search_regex(
            r'<meta name="title" content="([^"]*)"',
            webpage, 'title').split(' : ')[-1]

        configUrl = self._search_regex('config=(.*)$', playerUrl, 'config URL')
        configUrl = compat_urllib_parse.unquote(configUrl)

        formats = []

        def _add_format(name, cfgurl):
            configJSON = self._download_webpage(
                cfgurl, videoId,
                'Downloading ' + name + ' configuration',
                'Unable to download ' + name + ' configuration')

            # Technically, it's JavaScript, not JSON
            configJSON = configJSON.replace("'", '"')

            try:
                config = json.loads(configJSON)
            except (ValueError,) as err:
                raise ExtractorError('Invalid JSON in configuration file: ' + compat_str(err))
            playlist = config['playlist']
            formats.append({
                'url': playlist[1]['url'],
                'format_id': name,
            })

        _add_format('normal', configUrl)
        hq_url = (configUrl +
                  ('&hq=1' if '?' in configUrl else configUrl + '?hq=1'))
        try:
            _add_format('hq', hq_url)
        except ExtractorError:
            pass  # That's fine, we'll just use normal quality

        return {
            'id': videoId,
            'formats': formats,
            'uploader': showName,
            'title': title,
            'thumbnail': self._og_search_thumbnail(webpage),
            'description': videoDesc,
            'player_url': playerUrl,
        }
