from .poolbase import *

__author__ = "C. Wilhelm"
___license___ = "GPL v3"


class ClipBoardProcess(QueueProcess):
	def __init__(self, task_queue, result_queue):
		QueueProcess.__init__(self, task_queue, result_queue, function=self.extract)

	def extract(self, url):
		self.Plugins[0].extract(url)


class ClipBoardPool(QueuePool):
	Process = ClipBoardProcess
