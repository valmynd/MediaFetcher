from models.modelbase import *
from PySide.QtGui import QComboBox
from multiprocessing import Pool, Queue
from extract import extract_url, pool_init
import tempfile
import os

thumbnail_path = os.path.join(tempfile.gettempdir(), "mediafetcher_thumbnails")
if not os.path.exists(thumbnail_path):
	os.mkdir(thumbnail_path)


class ClipBoardModel(QueueModel):
	def __init__(self, path_to_xml_file):
		QueueModel.__init__(self, path_to_xml_file)

		self.queue = Queue()
		self.pool = Pool(processes=2, initializer=pool_init, initargs=(self.queue,))

	def _init_internal_dict(self):
		# this variant of ElementTreeModel has additional dicts to manage:
		self.combo_boxes_format = {}   # format (=extension) combobox for each item
		self.combo_boxes_quality = {}  # quality combobox for each item
		QueueModel._init_internal_dict(self)

	def _add_to_internal_dict(self, element, parent, num_row):
		QueueModel._add_to_internal_dict(self, element, parent, num_row)
		# each row gets one combobox for the extension and one for the quality options
		if element.tag == "item":
			format_combobox = QComboBox()   # see ComboBoxDelegate.createEditor()
			quality_combobox = QComboBox()  # see ComboBoxDelegate.createEditor()
			# get selected extension -> fallback: take the first which got parsed from XML
			selected_extension = element.get("selected")
			if selected_extension is None:
				element.attrib["selected"] = element.find("format").attrib["extension"]
				selected_extension = element.attrib["selected"]
			# get selected quality; TODO: make default-fallback configurable
			selected_format = element.find("format[@extension='%s']" % selected_extension)
			selected_quality = selected_format.get("selected")
			if selected_quality is None:
				selected_format.attrib["selected"] = selected_format.find("option").attrib["quality"]
				selected_quality = selected_format.attrib["selected"]
			# initialize combobox widgets
			for format in element.findall("format"):
				format_combobox.addItem(format.get("extension"))
			format_combobox.setCurrentIndex(format_combobox.findText(selected_extension))
			for option in element.findall("format[@extension='%s']/option" % selected_extension):
				quality_combobox.addItem(option.get("quality"))
			quality_combobox.setCurrentIndex(quality_combobox.findText(selected_quality))
			self.combo_boxes_format[element] = format_combobox
			self.combo_boxes_quality[element] = quality_combobox

	def addURL(self, url):
		""" add URL to queue -> add temporary item that will be replaced when the information is fetched """
		self.addElement(etree.Element('task', url=url, status="Extracting"))
		self.pool.apply_async(func=extract_url, args=(url,))

	def updateProgress(self):
		if self.queue.empty():
			return
		url, result = self.queue.get()
		task = self._root.find("task[@url='%s']" % url)
		parent, num_row = self._n[task]
		if isinstance(result, Exception):
			index = self.createIndex(num_row, 2, task)
			self.setData(index, str(result), Qt.EditRole)
			return
		self.removeRow(num_row)
		element = etree.fromstring(result)
		self.addElement(element)
