from plugins.youtube_dl.YoutubeDL import *
from extract import pool_init_for_youtubedl


def download_using_youtubedl(url, path, filename, download_url, player_url):
	ydl = download_using_youtubedl.ydl  # see pool_init_for_youtubedl()
	print(url, path, filename, download_url, player_url)


def pool_init(commandqueue, resultqueue):
	# Assign a Queue to the Function that will run in background here
	# see http://stackoverflow.com/a/3843313/852994
	download._commandqueue = commandqueue
	download._resultqueue = resultqueue
	pool_init_for_youtubedl(download_using_youtubedl)


def download(url, path, filename, download_url, player_url):
	try:
		# in view: switch status to Progressing
		# when updateProgress() handles the response, the next item is started
		download_using_youtubedl(url, path, filename, download_url, player_url)
		# handle pause: whenever a process notifies about progress, there must be messurement to abort
		#download._queue.put((url, xml))
		pass
	except Exception as e:
		#download._queue.put((url, e))
		print(e)