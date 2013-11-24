import re

from ..utils import (
    unified_strdate,
)
from .subtitles import SubtitlesInfoExtractor


class VikiIE(SubtitlesInfoExtractor):
    IE_NAME = 'viki'

    _VALID_URL = r'^https?://(?:www\.)?viki\.com/videos/(?P<id>[0-9]+v)'
    _TEST = {
        'url': 'http://www.viki.com/videos/1023585v-heirs-episode-14',
        'file': '1023585v.mp4',
        'md5': 'a21454021c2646f5433514177e2caa5f',
        'info_dict': {
            'title': 'Heirs Episode 14',
            'uploader': 'SBS',
            'description': 'md5:c4b17b9626dd4b143dcc4d855ba3474e',
            'upload_date': '20131121',
            'age_limit': 13,
        }
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group(1)

        webpage = self._download_webpage(url, video_id)
        title = self._og_search_title(webpage)
        description = self._og_search_description(webpage)
        thumbnail = self._og_search_thumbnail(webpage)

        uploader = self._html_search_regex(
            r'<strong>Broadcast Network: </strong>\s*([^<]*)<', webpage,
            'uploader')
        if uploader is not None:
            uploader = uploader.strip()

        rating_str = self._html_search_regex(
            r'<strong>Rating: </strong>\s*([^<]*)<', webpage,
            'rating information', default='').strip()
        RATINGS = {
            'G': 0,
            'PG': 10,
            'PG-13': 13,
            'R': 16,
            'NC': 18,
        }
        age_limit = RATINGS.get(rating_str)

        info_url = 'http://www.viki.com/player5_fragment/%s?action=show&controller=videos' % video_id
        info_webpage = self._download_webpage(info_url, video_id)
        video_url = self._html_search_regex(
            r'<source[^>]+src="([^"]+)"', info_webpage, 'video URL')

        upload_date_str = self._html_search_regex(
            r'"created_at":"([^"]+)"', info_webpage, 'upload date')
        upload_date = (
            unified_strdate(upload_date_str)
            if upload_date_str is not None
            else None
        )

        # subtitles
        video_subtitles = self.extract_subtitles(video_id, info_webpage)
        if self._downloader.params.get('listsubtitles', False):
            self._list_available_subtitles(video_id, info_webpage)
            return

        return {
            'id': video_id,
            'title': title,
            'url': video_url,
            'description': description,
            'thumbnail': thumbnail,
            'age_limit': age_limit,
            'uploader': uploader,
            'subtitles': video_subtitles,
            'upload_date': upload_date,
        }

    def _get_available_subtitles(self, video_id, info_webpage):
        res = {}
        for sturl in re.findall(r'<track src="([^"]+)"/>'):
            m = re.search(r'/(?P<lang>[a-z]+)\.vtt', sturl)
            if not m:
                continue
            res[m.group('lang')] = sturl
        return res
