from .poolbase import *
import re

__author__ = "C. Wilhelm"
___license___ = "GPL v3"


class ClipBoardProcess(QueueProcess):
	def __init__(self, task_queue, result_queue):
		QueueProcess.__init__(self, task_queue, result_queue)
		self.function = self.extract
		self.plugins = [Plugin(self) for Plugin in self.Plugins if Plugin.implements_extract]

	def extract(self, url):
		self.plugins[0].extract(url)


class ClipBoardPool(QueuePool):
	Process = ClipBoardProcess
