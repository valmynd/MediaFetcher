import pprint

pp = pprint.PrettyPrinter(depth=10)


class DownloadItem(object):
	def __init__(self, url, location, player_url, filename='undefined'):
		self.url = url
		self.location = location
		self.player_url = player_url
		self.filename = filename


class ClipBoardItem(object):
	def __init__(self, title, host, description, thumbnail, subtitles):
		self.host = host
		self.title = title
		self.thumbnail = thumbnail
		self.description = description
		self.subtitles = subtitles
		self.formats = {}

	def addDownloadOption(self, format, quality, url, location, player_url):
		if format == 'unknown':
			# ignore 'unknown', maybe have a setting for that somewhere?
			# don't confuse 'unknown' with 'undefined' -> the latter is to be used for sharehosters
			return
		if format not in self.formats:
			self.formats[format] = {}
		self.formats[format][quality] = DownloadItem(url=url, location=location, player_url=player_url)

	def getExtensions(self):
		return list(self.formats.keys())

	def getQualityOptions(self, format):
		return self.formats[format]

	def getDefaultQualityOptions(self):
		# TODO: handle defaults somewhere
		first_key = self.getExtensions()[0]
		return self.formats[first_key]

	def getDownloadItem(self, format, quality):
		return self.formats[format][quality]