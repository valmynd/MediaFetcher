from plugins.youtube_dl.YoutubeDL import *
from extract import pool_init_for_youtubedl


def download_using_youtubedl(option):
	ydl = download_using_youtubedl.ydl  # see pool_init_for_youtubedl()


def pool_init(queue_object):
	# Assign a Queue to the Function that will run in background here
	# see http://stackoverflow.com/a/3843313/852994
	download._queue = queue_object
	pool_init_for_youtubedl(download_using_youtubedl)


def download(option):
	try:
		#download._queue.put((url, xml))
		pass
	except Exception as e:
		#download._queue.put((url, e))
		print(e)