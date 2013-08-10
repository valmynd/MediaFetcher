from models.base import *
from PySide.QtGui import QComboBox
import tempfile, re, urllib, os

thumbnail_path = os.path.join(tempfile.gettempdir(), "mediafetcher_thumbnails")
if not os.path.exists(thumbnail_path):
	os.mkdir(thumbnail_path)


class ClipBoardModel(QueueModel):
	_columns = ['Title', 'Host', 'Status', 'Format', 'Quality']

	def __init__(self, path_to_xml_file):
		self.combo_boxes_format = {}   # format (=extension) combobox for each item
		self.combo_boxes_quality = {}  # quality combobox for each item
		QueueModel.__init__(self, path_to_xml_file)

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
						selected_format = element.find("format[@extension='" + selected_extension + "']")
						selected_quality = selected_format.get("selected", selected_format.find("option").attrib["quality"])
						# initialize combobox widgets
						for format in element.findall("format"):
							format_combobox.addItem(format.get("extension"))
						format_combobox.setCurrentIndex(format_combobox.findText(selected_extension))
						for option in element.findall("format[@extension='" + selected_extension + "']/option"):
							quality_combobox.addItem(option.get("quality"))
						quality_combobox.setCurrentIndex(quality_combobox.findText(selected_quality))
						self.combo_boxes_format[element] = format_combobox
						self.combo_boxes_quality[element] = quality_combobox

	def flags(self, index):
		if index.column() == 0:
			return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
		return Qt.ItemIsEnabled | Qt.ItemIsSelectable

	def data(self, index, role):
		if not (index.isValid() and role == Qt.DisplayRole): return
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