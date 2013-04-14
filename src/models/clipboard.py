from models.base import *
import copy
# TODO: store list of shown columns, etc

class ClipBoardModel(QueueModel):
	_columns = ['Title', 'Host', 'Status', 'Format', 'Quality']

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
		if role != Qt.EditRole: return False
		element = index.internalPointer()
		num_col = index.column()
		if element.tag == 'item':
			if num_col == 0:
				element.attrib["title"] = value
		elif element.tag == 'package':
			if num_col == 0:
				if value == "": return False
				element.attrib["name"] = value
		self.dataChanged.emit(index, index)
		return True

	def _get_format_options(self, element):
		return [format.attrib["name"] for format in element.iterfind('format')]

	def _get_quality_options(self, element):
		# same as _get_format_options(), except here we must know which format is selected
		selected = element.get("selected", element.find("format").attrib["name"])
		print(selected)
		# the following will work with python3.3: element.findall(".//*[@name='webm']")
		for format in element.iterfind('format'):
			if format.attrib.get("name") == selected:
				return [option.attrib["quality"] for option in format.iterfind('option')]
		return []

	def _get_combobox(self, parent, option, index, delegate):
		num_col = index.column()
		element = index.internalPointer()
		combo = QComboBox(parent)
		combo.element = element # needed in _format_changed(), TODO: find better solution
		if num_col == 3:
			combo.addItems(self._get_format_options(element))
			combo.currentIndexChanged.connect(self._format_changed)
			element.format_combobox = combo # dirty trick, TODO: find better solution
		elif num_col == 4:
			combo.addItems(self._get_quality_options(element))
			element.quality_combobox = combo # dirty trick, TODO: find better solution
		combo.setMaximumHeight(delegate.sizeHint(option, index).height())
		return combo

	def _format_changed(self, index):
		print("_format_changed %s" % self.sender())
		format_combobox = self.sender()
		element = format_combobox.element
		quality_combobox = element.quality_combobox
		element.set("selected", format_combobox.currentText())
		quality_combobox.clear()
		quality_combobox.addItems(self._get_quality_options(element))

	def merge(self, root):
		self._root.extend(list(root))
		self.layoutChanged.emit()