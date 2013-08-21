import json
import re
import time

from .common import InfoExtractor
from ..utils import (
    compat_str,
    compat_urllib_parse,
    compat_urllib_request,

    ExtractorError,
)


class HypemIE(InfoExtractor):
    """Information Extractor for hypem"""
    _VALID_URL = r'(?:http://)?(?:www\.)?hypem\.com/track/([^/]+)/([^/]+)'
    _TEST = {
        'url': 'http://hypem.com/track/1v6ga/BODYWORK+-+TAME',
        'file': '1v6ga.mp3',
        'md5': 'b9cc91b5af8995e9f0c1cee04c575828',
        'info_dict': {
            "title": "Tame"
        }
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        if mobj is None:
            raise ExtractorError('Invalid URL: %s' % url)
        track_id = mobj.group(1)

        data = { 'ax': 1, 'ts': time.time() }
        data_encoded = compat_urllib_parse.urlencode(data)
        complete_url = url + "?" + data_encoded
        request = compat_urllib_request.Request(complete_url)
        response, urlh = self._download_webpage_handle(request, track_id, 'Downloading webpage with the url')
        cookie = urlh.headers.get('Set-Cookie', '')

        self.report_extraction(track_id)

        html_tracks = self._html_search_regex(r'<script type="application/json" id="displayList-data">(.*?)</script>',
            response, 'tracks', flags=re.MULTILINE|re.DOTALL).strip()
        try:
            track_list = json.loads(html_tracks)
            track = track_list['tracks'][0]
        except ValueError:
            raise ExtractorError('Hypemachine contained invalid JSON.')

        key = track["key"]
        track_id = track["id"]
        artist = track["artist"]
        title = track["song"]

        serve_url = "http://hypem.com/serve/source/%s/%s" % (compat_str(track_id), compat_str(key))
        request = compat_urllib_request.Request(serve_url, "" , {'Content-Type': 'application/json'})
        request.add_header('cookie', cookie)
        song_data_json = self._download_webpage(request, track_id, 'Downloading metadata')
        try:
            song_data = json.loads(song_data_json)
        except ValueError:
            raise ExtractorError('Hypemachine contained invalid JSON.')
        final_url = song_data["url"]

        return [{
            'id':       track_id,
            'url':      final_url,
            'ext':      "mp3",
            'title':    title,
            'artist':   artist,
        }]