from plugins.youtube_dl.YoutubeDL import *
from extract import pool_init_for_youtubedl
import os


def download_using_youtubedl(url, path, filename, download_url, player_url, queue):
	ydl = download_using_youtubedl.ydl  # see pool_init_for_youtubedl()
	fdl = FileDownloader(ydl, ydl.params)
	info_dict = {
		'url': download_url,
		'player_url': player_url,
		'page_url': url,
		#'play_path': None,
		#'tc_url': None,
		#'urlhandle': None,
		#'user_agent': None,
	}
	fdl.add_progress_hook(lambda d: queue.put((url, d)) and print(d))
	filepath = os.path.join(path, filename)
	fdl._do_download(filepath, info_dict)


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
		download_using_youtubedl(url, path, filename, download_url, player_url, download._resultqueue)
		# handle pause: whenever a process notifies about progress, there must be messurement to abort
		#download._queue.put((url, xml))
		pass
	except Exception as e:
		#download._queue.put((url, e))
		print(e)