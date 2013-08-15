from PySide.QtCore import *
from xml.etree import ElementTree as etree


class ElementTreeModel(QAbstractItemModel):
	"""
	Model for ElementTree Data Structures

	inspired by: https://pypi.python.org/pypi/EuroPython2006_PyQt4_Examples/
	also read: http://qt-project.org/doc/qt-4.8/itemviews-simpletreemodel.html
	"""
	_columns = ["Tag", "Attributes"]

	def __init__(self, etree_root_element):
		QAbstractItemModel.__init__(self)
		self._root = etree_root_element
		self._init_internal_dict()

	def _init_internal_dict(self):
		""" this method is used to put the xml data into an internal dictionary """
		self._n = {}  # node information used in parent(): (element, (parent_element, row_index)
		for num_row, element in enumerate(self._root):
			self._add_to_internal_dict(element, self._root, num_row)

	def _add_to_internal_dict(self, element, parent, num_row):
		""" override this if something shall happen with newly added elements """
		self._n[element] = (parent, num_row)
		for num_row, child in enumerate(element):
			self._add_to_internal_dict(child, element, num_row)

	def _remove_from_internal_dict(self, element):
		for child in list(element):
			self._remove_from_internal_dict(child)
		self._n.pop(element)

	def data(self, index, role):
		""" data is retrieved via data(), implement setData() for data to be written! """
		# index.internalPointer() -> internal data for requested row
		# index.column() -> number of requested column
		if not (index.isValid() and role == Qt.DisplayRole):
			return
		element = index.internalPointer()
		if index.column() == 0:
			return element.tag
		return ";".join("%s=\"%s\"" % (k, v) for k, v in element.items())

	def headerData(self, section, orientation, role):
		""" return header by column number (here called section) """
		if orientation == Qt.Horizontal and role == Qt.DisplayRole:
			return self._columns[section]

	def index(self, row, column, parent=QModelIndex()):
		""" this method must be implemented, returns some Index object, is used by qt internally """
		parent_item = parent.internalPointer() if parent.isValid() else self._root
		return self.createIndex(row, column, parent_item[row])

	def parent(self, index):
		""" this method must be implemented, returns some Index object, is used by qt internally """
		if not index.isValid():
			return QModelIndex()
		parent_item, num_row = self._n[index.internalPointer()]
		if id(parent_item) == id(self._root):
			return QModelIndex()
		return self.createIndex(self._n[parent_item][1], 0, parent_item)  # this is why we need num_row

	def rowCount(self, parent):
		item = parent.internalPointer() if parent.isValid() else self._root
		return len(item)

	def columnCount(self, parent):
		return len(self._columns)

	def indexForElement(self, element, num_col=0):
		parent, num_row = self._n[element]
		return self.createIndex(num_row, num_col, element)

	def removeElementAtIndex(self, index, element=None):
		parent_index = self.parent(index)
		parent_element = parent_index.internalPointer() if parent_index.isValid() else self._root
		# from qt documentation: is important to notify any connected views about changes to the model's dimensions both
		# before and after they occur (otherwise it the view will constantly ask for the parent of the removed element)
		self.beginRemoveRows(parent_index, index.row(), index.row())
		element = index.internalPointer() if element is None else element
		#self._remove_from_internal_dict(element)
		parent_element.remove(element)
		# index must be rebuilt, as row-numbers have changed!
		self._init_internal_dict()
		self.endRemoveRows()

	def removeAll(self):
		self.beginResetModel()
		self._root.clear()
		self._init_internal_dict()
		self.endResetModel()

	def addElement(self, element):
		# parameters first and last of beginInsertRows() are the row numbers that the new rows will have
		row_number = len(self._root) + 1
		self.beginInsertRows(QModelIndex(), row_number, row_number)
		self._root.append(element)
		self._init_internal_dict()
		#self._n[element] = (self._root, row_number)
		#self._init_element(element)
		self.endInsertRows()


class QueueModel(ElementTreeModel):
	def __init__(self, path_to_xml_file):
		"""other than ElementTreeModel(), QueueModel() does take a path to an XML file as a parameter"""
		root_element = etree.parse(path_to_xml_file).getroot()
		ElementTreeModel.__init__(self, root_element)

	def rowCount(self, parent):
		# Only "package" nodes should have children in the view!
		item = parent.internalPointer() if parent.isValid() else self._root
		if item.tag == "item":
			return 0
		return len(item)