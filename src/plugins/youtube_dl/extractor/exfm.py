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
            'url': 'http://ex.fm/song/1bgtzg',
            'file': '95223130.mp3',
            'md5': '8a7967a3fef10e59a1d6f86240fd41cf',
            'info_dict': {
                "title": "We Can't Stop - Miley Cyrus",
                "uploader": "Miley Cyrus",
                'upload_date': '20130603',
                'description': 'Download "We Can\'t Stop" \r\niTunes: http://smarturl.it/WeCantStop?IQid=SC\r\nAmazon: http://smarturl.it/WeCantStopAMZ?IQid=SC',
            },
            'note': 'Soundcloud song',
        },
        {
            'url': 'http://ex.fm/song/wddt8',
            'file': 'wddt8.mp3',
            'md5': '966bd70741ac5b8570d8e45bfaed3643',
            'info_dict': {
                'title': 'Safe and Sound',
                'uploader': 'Capital Cities',
            },
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
