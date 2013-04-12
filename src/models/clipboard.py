from models.base import *
import copy


class ClipBoardModel(ElementTreeModel):
	_columns = ['Title', 'Host', 'Status', 'Format', 'Quality']

	def __init__(self, root):
		# put children of "item" elements into a better suited data structure
		# note we must reverse this when storing the content back to an XML-File
		# TODO: store list of shown columns, etc
		self._data = copy.deepcopy(root)
		for element in root:
			if element.tag == "package":
				for item in element:
					item._children = ()
				continue
			element._children = ()
		ElementTreeModel.__init__(self, root)

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
