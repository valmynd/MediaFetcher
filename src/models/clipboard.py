from models.base import *


class ClipBoardItemElement(QueueItemElement):
	def __init__(self, tag, attrib, **extra):
		QueueItemElement.__init__(self, tag, attrib, **extra)
		# the following attributes are meant to be accessed from the outside:
		self.formats = {} # for example, one could access a download option like this: element.format['flv']['720p']
		self.format_combobox = None
		self.quality_combobox = None

	def _init(self):
		for format in self.iterfind('format'):
			extension = format.attrib["extension"]
			self.formats[extension] = {}
			for option in format.iterfind('option'):
				quality = option.attrib["quality"]
				self.formats[extension][quality] = option

	def getThumbnail(self):
		#if not isinstance(self.thumbnail, str) or '//' not in self.thumbnail:
		#	return ''
		#if self._thumbnail_local is None:
		#	tmp_filename = re.sub('[^0-9a-zA-Z]+', '', self.thumbnail)
		#	tmp_file_path = path.join(thumbnail_path, tmp_filename)
		#	tmp_file = open(tmp_file_path, 'wb')
		#	tmp_file.write(urlopen(self.thumbnail).read())
		#	self._thumbnail_local = tmp_file_path
		#return self._thumbnail_local
		pass

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
	for element in model._root:
		if element.tag == 'item':
			print(element.formats)
			#print(tostring(root, encoding="unicode"))