from models.base import *
from PySide.QtGui import QComboBox
import tempfile, re, urllib, os

thumbnail_path = os.path.join(tempfile.gettempdir(), "mediafetcher_thumbnails")
if not os.path.exists(thumbnail_path):
	os.mkdir(thumbnail_path)


class ClipBoardItemElement(QueueItemElement):
	def __init__(self, tag, attrib, **extra):
		QueueItemElement.__init__(self, tag, attrib, **extra)
		# the following attributes are meant to be accessed from anywhere:
		self.formats = {} # initialized via _init(): access a download option like this: element.format['flv']['720p']
		self.format_combobox = QComboBox() # initialized via ComboBoxDelegate.createEditor()
		self.quality_combobox = QComboBox() # initialized via ComboBoxDelegate.createEditor()
		# those attributes however should only be accessed via the respective methods:
		self._thumbnail_local = None

	def _init(self):
		# initialize format dict with information from child Elements
		for format in self.iterfind('format'):
			extension = format.attrib["extension"]
			self.formats[extension] = {}
			for option in format.iterfind('option'):
				quality = option.attrib["quality"]
				self.formats[extension][quality] = option
		# initialize combobox widgets
		selected_extension = self.getSelectedExtension()
		selected_quality = self.getSelectedQuality(selected_extension)
		self.format_combobox.addItems(self.getExtensions())
		self.format_combobox.setCurrentIndex(self.format_combobox.findText(selected_extension))
		self.quality_combobox.addItems(self.getQualityOptions(extension=selected_extension))
		self.quality_combobox.setCurrentIndex(self.quality_combobox.findText(selected_quality))

		#print(self.format_combobox.findText(selected_extension))
		self.format_combobox.setCurrentIndex(2)

	def getExtensions(self):
		return list(self.formats.keys())

	def getSelectedExtension(self):
		# fallback: take the first which got parsed from XML
		return self.get("selected", self.find("format").attrib["extension"])

	def getQualityOptions(self, extension):
		return list(self.formats[extension].keys())

	def getSelectedQuality(self, extension):
		# same as in getSelectedExtension; TODO: make default-fallback configurable
		for format in self.iterfind('format'):
			if format.attrib["extension"] == extension:
				return format.get("selected", format.find("option").attrib["quality"])

	def getThumbnail(self):
		if not isinstance(self.thumbnail, str) or '//' not in self.thumbnail: return
		if self._thumbnail_local is None:
			tmp_filename = re.sub('[^0-9a-zA-Z]+', '', self.thumbnail)
			self._thumbnail_local = os.path.join(thumbnail_path, tmp_filename)
			if not os.path.exists(self._thumbnail_local):
				tmp_file = open(self._thumbnail_local, 'wb')
				tmp_file.write(os.urlopen(self.thumbnail).read())
		return self._thumbnail_local

class ClipBoardModel(QueueModel):
	_columns = ['Title', 'Host', 'Status', 'Format', 'Quality']
	_element_cls = ClipBoardItemElement

	def flags(self, index):
		if index.column() == 0:
			return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
		return Qt.ItemIsEnabled | Qt.ItemIsSelectable

	def data(self, index, role):
		if not (index.isValid() and role == Qt.DisplayRole): return
		element = index.internalPointer()
		num_col = index.column()
		if element.tag == 'item':
			if num_col == 0:
				return element.attrib["title"]
			elif num_col == 1:
				return element.attrib.get("host")
			elif num_col == 2:
				return 'Available'
		elif element.tag == 'package':
			if num_col == 0:
				return element.attrib["name"]

	def setData(self, index, value, role):
		num_col = index.column()
		if num_col != 0 or role != Qt.EditRole or value == "":
			return QueueModel.setData(self, index, value, role)
		element = index.internalPointer()
		if element.tag == 'item':
			element.attrib["title"] = value
		elif element.tag == 'package':
			element.attrib["name"] = value
		self.dataChanged.emit(index, index)
		return True

	def merge(self, root):
		self._root.extend(list(root))
		self.layoutChanged.emit()


if __name__ == '__main__':
	#from xml.etree.ElementTree import parse, tostring
	model = ClipBoardModel("../models/clipboard_example.xml")
	print(thumbnail_path)
	for element in model._root:
		if element.tag == 'item':
			print(element.formats)
			#print(tostring(root, encoding="unicode"))