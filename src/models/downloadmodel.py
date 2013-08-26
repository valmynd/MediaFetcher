from models.modelbase import *
from PySide.QtGui import QProgressBar
from multiprocessing import Pool, Queue
from download import download, pool_init
from models.clipboardmodel import fill_filename_template


class DownloadModel(QueueModel):
	def __init__(self, main_window, qsettings_object):
		QueueModel.__init__(self, main_window, qsettings_object, "downloads.xml")

		self.commandqueue = Queue()  # contains commands such as "abort", "requeue"
		self.resultqueue = Queue()   # contains result tuples as such: (url, status, size_written, remote_size)
		self.pool = Pool(processes=4, initializer=pool_init, initargs=(self.commandqueue, self.resultqueue,))

	def _init_internal_dict(self):
		# this variant of ElementTreeModel has additional dicts to manage:
		self.progress_bars = {}   # progressbar for each item and package
		self.option_elements = {}  # selected option element for easy access
		QueueModel._init_internal_dict(self)

	def _add_to_internal_dict(self, element, parent, num_row):
		QueueModel._add_to_internal_dict(self, element, parent, num_row)
		if element.tag == "item":
			# TODO: check if file exists and if so, initialize percentage
			progressbar = QProgressBar()
			progressbar.setValue(0)
			self.progress_bars[element] = progressbar
			selected_extension = element.get("selected")
			if selected_extension is None:
				element.attrib["status"] = "Error: No Extension selected"
				return
			selected_format = element.find("format[@extension='%s']" % selected_extension)
			if selected_format is None:
				element.attrib["status"] = "Error: No Quality selected"
				return
			selected_quality = selected_format.get("selected")
			option = element.find("format[@extension='%s']/option[@quality='%s']" % (selected_extension, selected_quality))
			self.option_elements[element] = option
			# fill remaining filename template, extension and quality shall not change within DownloadModel
			mapping = dict(title=element.get("title"), url=element.get("url"), host=element.get("host"),
								extension=selected_extension, quality=selected_quality)
			element.attrib["filename"] = fill_filename_template(element.attrib["filename"], mapping)

	def data(self, index, role):
		if index.isValid() and role in (Qt.DisplayRole, Qt.EditRole):
			# handle extension, quality and progress differently here
			element = index.internalPointer()
			num_col = index.column()
			if element.tag == 'item':
				if num_col == 8:
					return element.attrib.get("selected")
				elif num_col == 9:
					# data() is called VERY often, even when the column ain't visible -> avoid xpath queries here
					option = self.option_elements[element]
					return option.attrib.get("quality")
			return QueueModel.data(self, index, role)

	def start(self):
		for item in self._root.findall("item[@status='Queued']"):
			item.attrib["status"] = "Progressing"  # TODO: self.dataChanged.emit(index, index)
			option = self.option_elements[item]
			self.pool.apply_async(func=download, args=(item.get("url"), item.get("path"), item.get("filename"),
																	 option.get("download_url"), option.get("download_url")))

	def pause(self):
		pass

	def updateProgress(self):
		while not self.resultqueue.empty():
			url, result_dict = self.resultqueue.get()
			item = self._root.find("item[@url='%s']" % url)
			if item is None:
				# TODO: item might have gotten deleted in the GUI, send abort signal!
				return
			progressbar = self.progress_bars[item]
			print(result_dict)
			if result_dict["status"] == "downloading":
				# TODO: Bandwidth
				percentage = result_dict.get("downloaded_bytes", 0) / result_dict.get("total_bytes", 1) * 100
				progressbar.setValue(percentage)
			elif result_dict["status"] == "finished":
				item.attrib["status"] = "Ready"  # TODO: datachanged()
				progressbar.setValue(100)