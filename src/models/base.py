from PySide.QtCore import *
from xml.etree import ElementTree as etree


class ElementTreeModel(QAbstractItemModel):
	"""
	Readonly ItemModel for ElementTree Data structures
	see https://pypi.python.org/pypi/EuroPython2006_PyQt4_Examples/
	also read http://qt-project.org/doc/qt-4.8/itemviews-simpletreemodel.html
	"""
	_columns = ["Tag", "Attributes"]

	def __init__(self, etree_root_element):
		QAbstractItemModel.__init__(self)
		self._n = {}  # node information used in parent(): (element, (parent_element, row_index)
		self._root = etree_root_element
		self.layoutChanged.connect(self._rebuild_index)
		self._rebuild_index()

	def _rebuild_index(self):
		""" this method is used to put the xml data into an internal dictionary """
		for parent in self._root.iter():
			for row_index, element in enumerate(parent):
				self._n[element] = (parent, row_index)

	def data(self, index, role):
		""" data is retrieved via data(), see setData() for data to be written """
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
		parent_item, row_index = self._n[index.internalPointer()]
		if id(parent_item) == id(self._root):
			return QModelIndex()
		return self.createIndex(self._n[parent_item][1], 0, parent_item)  # herefore we need row_index

	def rowCount(self, parent):
		item = parent.internalPointer() if parent.isValid() else self._root
		return len(item)

	def columnCount(self, parent):
		return len(self._columns)


class QueueModel(ElementTreeModel):
	def __init__(self, path_to_xml_file):
		"""other than ElementTreeModel(), QueueModel() does take a path to an XML file as a parameter"""
		root = etree.parse(path_to_xml_file).getroot()
		ElementTreeModel.__init__(self, root)

	def rowCount(self, parent):
		# Only "package" nodes should have children in the view!
		item = parent.internalPointer() if parent.isValid() else self._root
		if item.tag == "item":
			return 0
		return len(item)

	def _rebuild_index(self):
		# (don't know if this version does speedup lookups)
		self._n = dict((child, (parent, row_index))
							for parent in self._root.iter()
							for row_index, child in enumerate(parent)
							if parent.tag in ("clipboard", "package"))