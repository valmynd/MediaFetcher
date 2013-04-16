from utils.youtube_dl.FileDownloader import *
from utils.youtube_dl.InfoExtractors import gen_extractors
#from lib.items import ClipBoardItem, ExtractedItems
#from datetime import date
#from xml.etree.ElementTree import Element, tostring
from lxml.etree import Element, ElementBase, tostring

class ItemElement(ElementBase):
	def honking(self):
		print("")


class MediaExtractor(FileDownloader):
	def __init__(self, url):
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

		# Try Retrieving Information for the URL
		#raise Exception("Random Error")
		self._download(url)
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
		items = {} # xml.etree.Element 'item' objects by title
		for instance in self.videos:
			formats = {} # xml.etree.Element 'format' objects by (title, extension)
			title = instance['title']
			if title not in items:
				items[title] = Element('item', title=title, host=self.ie.IE_NAME,
									   description=str(instance.get('description')),
									   thumbnail=str(instance.get('thumbnail')))
				# subtitles=instance.get('subtitles')
			item = items[title]
			# Extract relevant Download Options
			extension, quality = self._extract_format(format_str=instance.get('format'))
			if extension not in formats:
				formats[extension] = Element('format', extension=extension)
				item.append(formats[extension])
			format = formats[extension]
			format.append(Element('option', quality=quality, url=str(instance.get('url')), location=str(instance.get('location')), player_url=str(instance.get('player_url'))))
		self.clipboard = Element('clipboard')
		if len(items) == 1:
			self.clipboard.extend(items.values())
			return
		package = Element('package', name="Youtube Playlist") # give more meaningful name!
		package.extend(items.values())
		self.clipboard.append(package)

	def _extract_format(self, format_str):
		# currently, format_str is typically something like '45 - 720x1280' for youtube-dl
		if isinstance(format_str, str) and ' ' in format_str:
			fid = format_str[:format_str.find(' ')]
			format = self.ie._video_extensions.get(fid, 'unknown')
			quality = self.ie._video_dimensions.get(fid, 'unknown')
			return format, quality
		# note that 'format' field is optional, see InfoExtractor documentation
		return 'undefined', 'undefined'

	def getXML(self):
		return tostring(self.clipboard, encoding="unicode")

def extract_url(url):
	try:
		extractor = MediaExtractor(url)
		extract_url._queue.put((url, extractor.getXML()))
	except Exception as e:
		extract_url._queue.put((url, e))


if __name__ == '__main__':
	fetcher = MediaExtractor('https://www.youtube.com/watch?v=vwjNfc6ORTg')
	print(fetcher.getXML())