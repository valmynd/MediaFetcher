# coding: utf-8


import os.path
import re

from .common import InfoExtractor
from ..compat import (
    compat_urllib_parse,
    compat_urllib_request,
)
from ..utils import ExtractorError


class MonikerIE(InfoExtractor):
    IE_DESC = 'allmyvideos.net and vidspot.net'
    _VALID_URL = r'https?://(?:www\.)?(?:allmyvideos|vidspot)\.net/(?P<id>[a-zA-Z0-9_-]+)'

    _TESTS = [{
        'url': 'http://allmyvideos.net/jih3nce3x6wn',
        'md5': '710883dee1bfc370ecf9fa6a89307c88',
        'info_dict': {
            'id': 'jih3nce3x6wn',
            'ext': 'mp4',
            'title': 'youtube-dl test video',
        },
    }, {
        'url': 'http://vidspot.net/l2ngsmhs8ci5',
        'md5': '710883dee1bfc370ecf9fa6a89307c88',
        'info_dict': {
            'id': 'l2ngsmhs8ci5',
            'ext': 'mp4',
            'title': 'youtube-dl test video',
        },
    }, {
        'url': 'https://www.vidspot.net/l2ngsmhs8ci5',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        orig_webpage = self._download_webpage(url, video_id)

        if '>File Not Found<' in orig_webpage:
            raise ExtractorError('Video %s does not exist' % video_id, expected=True)

        error = self._search_regex(
            r'class="err">([^<]+)<', orig_webpage, 'error', default=None)
        if error:
            raise ExtractorError(
                '%s returned error: %s' % (self.IE_NAME, error), expected=True)

        fields = re.findall(r'type="hidden" name="(.+?)"\s* value="?(.+?)">', orig_webpage)
        data = dict(fields)

        post = compat_urllib_parse.urlencode(data)
        headers = {
            b'Content-Type': b'application/x-www-form-urlencoded',
        }
        req = compat_urllib_request.Request(url, post, headers)
        webpage = self._download_webpage(
            req, video_id, note='Downloading video page ...')

        title = os.path.splitext(data['fname'])[0]

        # Could be several links with different quality
        links = re.findall(r'"file" : "?(.+?)",', webpage)
        # Assume the links are ordered in quality
        formats = [{
            'url': l,
            'quality': i,
        } for i, l in enumerate(links)]
        self._sort_formats(formats)

        return {
            'id': video_id,
            'title': title,
            'formats': formats,
        }
