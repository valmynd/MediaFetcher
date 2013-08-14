from models.modelbase import *
from PySide.QtGui import QComboBox
from multiprocessing import Pool, Queue
from extract import extract_url
import tempfile
import os

thumbnail_path = os.path.join(tempfile.gettempdir(), "mediafetcher_thumbnails")
if not os.path.exists(thumbnail_path):
	os.mkdir(thumbnail_path)


class ClipBoardModel(QueueModel):
	_columns = ['Title', 'Host', 'Status', 'Format', 'Quality', 'Description']

	def __init__(self, path_to_xml_file):
		self.combo_boxes_format = {}   # format (=extension) combobox for each item
		self.combo_boxes_quality = {}  # quality combobox for each item
		QueueModel.__init__(self, path_to_xml_file)

		self.queue = Queue()
		self.pool = Pool(processes=2, initializer=self._pool_init, initargs=(self.queue,))

	def _pool_init(self, queue):
		# Assign a Queue to a Function that will run in background here
		# see http://stackoverflow.com/a/3843313/852994
		extract_url._queue = queue

	def _rebuild_index(self):
		# this variant of ElementTreeModel is mutable!
		# -> the following attributes shall be flushed every time
		self.combo_boxes_format = {}
		self.combo_boxes_quality = {}
		self._n = {}
		for parent in self._root.iter():
			if parent.tag in ("clipboard", "package"):
				for row_index, element in enumerate(parent):
					self._n[element] = (parent, row_index)
					# each row gets one combobox for the extension and one for the quality options
					if element.tag == "item":
						format_combobox = QComboBox()   # see ComboBoxDelegate.createEditor()
						quality_combobox = QComboBox()  # see ComboBoxDelegate.createEditor()
						# get selected extension -> fallback: take the first which got parsed from XML
						selected_extension = element.get("selected", element.find("format").attrib["extension"])
						# get selected quality; TODO: make default-fallback configurable
						selected_format = element.find("format[@extension='%s']" % selected_extension)
						selected_quality = selected_format.get("selected", selected_format.find("option").attrib["quality"])
						# initialize combobox widgets
						for format in element.findall("format"):
							format_combobox.addItem(format.get("extension"))
						format_combobox.setCurrentIndex(format_combobox.findText(selected_extension))
						for option in element.findall("format[@extension='%s']/option" % selected_extension):
							quality_combobox.addItem(option.get("quality"))
						quality_combobox.setCurrentIndex(quality_combobox.findText(selected_quality))
						self.combo_boxes_format[element] = format_combobox
						self.combo_boxes_quality[element] = quality_combobox

	def flags(self, index):
		if index.column() == 0:
			return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
		return Qt.ItemIsEnabled | Qt.ItemIsSelectable

	def data(self, index, role):
		if not (index.isValid() and role in (Qt.DisplayRole, Qt.EditRole)):
			# if Qt.EditRole ain't accepted, QDataWidgetMapper wouldn't work properly
			return None
		# columns 3, 4 are handled via ComboBoxDelegate
		element = index.internalPointer()
		num_col = index.column()
		if element.tag == 'item':
			if num_col == 0:
				return element.attrib["title"]
			elif num_col == 1:
				return element.attrib.get("host")
			elif num_col == 2:
				return 'Available'
			elif num_col == 5:
				return element.attrib.get("description")
		elif element.tag == 'package':
			if num_col == 0:
				return element.attrib["name"]
			elif num_col == 2:
				return 'Available'
		elif element.tag == 'task':
			if num_col == 0:
				return element.attrib["url"]
			elif num_col == 2:
				return element.attrib.get("status", "Extracting")

	def setData(self, index, value, role):
		if role != Qt.EditRole or value == "":
			return QueueModel.setData(self, index, value, role)
		element = index.internalPointer()
		num_col = index.column()
		if element.tag == 'item':
			if num_col == 0:
				element.attrib["title"] = value
			elif num_col == 5:
				element.attrib["description"] = value
		elif element.tag == 'package':
			if num_col == 0:
				element.attrib["name"] = value
		elif element.tag == 'task':
			pass
		self.dataChanged.emit(index, index)
		return True

	def addURL(self, url):
		""" add URL to queue -> add temporary item that will be replaced when the information is fetched """
		self._root.append(etree.Element('task', url=url))
		self.layoutChanged.emit()
		self.pool.apply_async(func=extract_url, args=(url,))

	def updateProgress(self):
		if self.queue.empty():
			return
		url, result = self.queue.get()
		task = self._root.find("task[@url='%s']" % url)
		if isinstance(result, Exception):
			task.attrib["status"] = str(result)
		else:
			element = etree.fromstring(result)
			self._root.append(element)
			self._root.remove(task)
		self.layoutChanged.emit()
