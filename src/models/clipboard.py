from models.base import *
# TODO: store list of shown columns, etc

class ClipBoardModel(QueueModel):
	_columns = ['Title', 'Host', 'Status', 'Format', 'Quality']

	def _rebuild_index(self):
		# overridden so every 'item' becomes a dict assigned to it like this: {extension: {quality: 'option'-Element}}
		# for example, one could access a download option like this: element.format['flv']['720p']
		QueueModel._rebuild_index(self)
		# the following can be replaced with the in python3.3: element.findall(".//item")
		# ... but it is not too common yet and I don't want hard dependency on lxml (although lxml is great)
		all_items = list(self._root.iterfind('item'))
		for package in self._root.iterfind('package'):
			all_items += list(package.iterfind('item'))
		for item in all_items:
			item.formats = {}
			for format in item.iterfind('format'):
				extension = format.attrib["extension"]
				item.formats[extension] = {}
				for option in format.iterfind('option'):
					quality = option.attrib["quality"]
					item.formats[extension][quality] = option

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