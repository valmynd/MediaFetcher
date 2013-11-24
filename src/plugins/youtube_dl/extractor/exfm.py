import re
import json

from .common import InfoExtractor


class ExfmIE(InfoExtractor):
    IE_NAME = 'exfm'
    IE_DESC = 'ex.fm'
    _VALID_URL = r'(?:http://)?(?:www\.)?ex\.fm/song/([^/]+)'
    _SOUNDCLOUD_URL = r'(?:http://)?(?:www\.)?api\.soundcloud.com/tracks/([^/]+)/stream'
    _TESTS = [
        {
            'url': 'http://ex.fm/song/eh359',
            'file': '44216187.mp3',
            'md5': 'e45513df5631e6d760970b14cc0c11e7',
            'info_dict': {
                "title": "Test House \"Love Is Not Enough\" (Extended Mix) DeadJournalist Exclusive",
                "uploader": "deadjournalist",
                'upload_date': '20120424',
                'description': 'Test House \"Love Is Not Enough\" (Extended Mix) DeadJournalist Exclusive',
            },
            'note': 'Soundcloud song',
            'skip': 'The site is down too often',
        },
        {
            'url': 'http://ex.fm/song/wddt8',
            'file': 'wddt8.mp3',
            'md5': '966bd70741ac5b8570d8e45bfaed3643',
            'info_dict': {
                'title': 'Safe and Sound',
                'uploader': 'Capital Cities',
            },
            'skip': 'The site is down too often',
        },
    ]

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        song_id = mobj.group(1)
        info_url = "http://ex.fm/api/v3/song/%s" %(song_id)
        webpage = self._download_webpage(info_url, song_id)
        info = json.loads(webpage)
        song_url = info['song']['url']
        if re.match(self._SOUNDCLOUD_URL, song_url) is not None:
            self.to_screen('Soundcloud song detected')
            return self.url_result(song_url.replace('/stream',''), 'Soundcloud')
        return [{
            'id':          song_id,
            'url':         song_url,
            'ext':         'mp3',
            'title':       info['song']['title'],
            'thumbnail':   info['song']['image']['large'],
            'uploader':    info['song']['artist'],
            'view_count':  info['song']['loved_count'],
        }]
