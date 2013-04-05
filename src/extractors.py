from utils.youtube_dl.FileDownloader import *
from utils.youtube_dl.InfoExtractors import gen_extractors
from lib.items import ClipBoardItem


class MediaExtractor(FileDownloader):
	def __init__(self, url_or_search_string=''):
		FileDownloader.__init__(self,
								dict(format='all', format_limit=None, ignoreerrors=False, listformats=False,
									 consoletitle=False, continuedl=True, forcedescription=False, forcefilename=False,
									 forceformat=False, forcethumbnail=False, forcetitle=False, forceurl=False,
									 logtostderr=False, matchtitle=None, max_downloads=None, nooverwrites=False,
									 nopart=False, noprogress=False, password=None, username=None,
									 playlistend=-1, playliststart=1, prefer_free_formats=False, quiet=False,
									 ratelimit=None, rejecttitle=None, retries=10, simulate=False, skip_download=False,
									 subtitleslang=None, subtitlesformat="srt", test=True, updatetime=True,
									 usenetrc=False, verbose=True, writedescription=False,
									 writeinfojson=True, writesubtitles=False, onlysubtitles=False, allsubtitles=False,
									 listssubtitles=False, outtmpl="%(id)s.%(ext)s"))
		# Initialize List of Extractors
		for extractor in gen_extractors():
			self.add_info_extractor(extractor)
		self._download(url_or_search_string)
		self._extract()

	def _download(self, url):
		"""Modified FileDownloader.download() to extract Information from a single URL only;
		Information is written into self.videos, used InfoExtractor is written into self.ie"""
		suitable_found = False
		for ie in self._ies:
			# Go to next InfoExtractor if not suitable
			if not ie.suitable(url):
				continue
			# Warn if the _WORKING attribute is False
			if not ie.working():
				self.report_warning('the program functionality for this site has been marked as broken')
			# Suitable InfoExtractor found
			suitable_found = True
			self.ie = ie
			# Extract information from URL and process it
			try:
				self.videos = ie.extract(url)
			except ExtractorError as de: # An error we somewhat expected
				self.trouble('ERROR: ' + compat_str(de), de.format_traceback())
				break
			except MaxDownloadsReached:
				self.to_screen('[info] Maximum number of downloaded files reached.')
				raise
			except Exception as e:
				if self.params.get('ignoreerrors', False):
					self.report_error('' + compat_str(e), tb=compat_str(traceback.format_exc()))
					break
				else:
					raise
			# Suitable InfoExtractor had been found; end Loop
			break
		if not suitable_found:
			self.report_error('no suitable InfoExtractor: %s' % url)

	def _extract(self):
		"""
		The following are common fields for a title:
		title:          Video title, unescaped.
		host:           IE_NAME (needs to be added to the dictionary here!)
		thumbnail:      Full URL to a video thumbnail image.
		description:    One-line video description.
		subtitles:      The subtitle file contents.

		The following fields are specific to a certain Format- and Quality Variant
		url:            Final video URL.
		location:       Physical location of the video. (???)
		player_url:     SWF Player URL (used for rtmpdump).

		The following format-specific fields are transformed in this method
		ext:            Video filename extension. -> becomes 'format'
		format:         The video format -> optional, becomes 'quality'

		The following fields are currently ignored:
		id:             Video identifier.
		uploader:       Full name of the video uploader.
		upload_date:    Video upload date (YYYYMMDD).
		uploader_id:    Nickname or id of the video uploader.
		urlhandle:      [internal] (???)
		"""
		media = {}
		for item in self.videos:
			title = item['title']
			if title not in media:
				media[title] = ClipBoardItem(title=title, host=self.ie.IE_NAME, description=item.get('description'),
											 thumbnail=item.get('thumbnail'), subtitles=item.get('subtitles'))
			# Extract relevant Download Options
			if ' ' in item.get('format'): # e.g. '45 - 720x1280'
				fid = item.get('format')[:item.get('format').find(' ')]
				format = self.ie._video_extensions.get(fid, 'unknown')
				quality = self.ie._video_dimensions.get(fid, 'unknown')
			else: # note that 'format' field is optional, see InfoExtractor documentation
				format = quality = 'undefined'
			# Add Download option to Title
			media[title].addDownloadOption(format=format, quality=quality, url=item.get('url'),
										   location=item.get('location'), player_url=item.get('player_url'))
		self.media = media
		for v in media.values():
			print(v)

	def getTitles(self):
		return self.media.keys()

	def getClipBoardItem(self, title):
		return self.media[title]


if __name__ == '__main__':
	fetcher = MediaExtractor('https://www.youtube.com/watch?v=2ssflEr3s44')