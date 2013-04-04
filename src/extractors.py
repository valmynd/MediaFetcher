from utils.youtube_dl.FileDownloader import *
from utils.youtube_dl.InfoExtractors import gen_extractors


class DownloaderYDL(FileDownloader):
	def __init__(self, url_or_search_string=''):
		FileDownloader.__init__(self,
								dict(consoletitle=False, continuedl=True, forcedescription=False, forcefilename=False,
									 forceformat=False, forcethumbnail=False, forcetitle=False, forceurl=False,
									 format=None, format_limit=None, ignoreerrors=False, listformats=True,
									 logtostderr=False, matchtitle=None, max_downloads=None, nooverwrites=False,
									 nopart=False, noprogress=False, outtmpl="%(id)s.%(ext)s", password=None,
									 playlistend=-1, playliststart=1, prefer_free_formats=False, quiet=False,
									 ratelimit=None, rejecttitle=None, retries=10, simulate=False, skip_download=False,
									 subtitleslang=None, subtitlesformat="srt", test=True, updatetime=True,
									 usenetrc=False, username=None, verbose=True, writedescription=False,
									 writeinfojson=True, writesubtitles=False, onlysubtitles=False, allsubtitles=False,
									 listssubtitles=False))
		url = url_or_search_string # FIXME: check if it is an URL or just a search string
		# Initialize List of Extractors
		for extractor in gen_extractors():
			self.add_info_extractor(extractor)
		# Try to Extract Information on URL
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

		#import pprint
		#pp = pprint.PrettyPrinter(indent=4)
		#pp.pprint(self.videos)
		#for item in self.videos:
		#	print(item['format'])


if __name__ == '__main__':
	fetcher = DownloaderYDL('http://www.youtube.com/watch?v=iycDDKZySbI')