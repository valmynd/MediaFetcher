from PySide.QtCore import *
from PySide.QtGui import *
from pprint import pprint


class ElementTreeModel(QAbstractItemModel):
	"""
	Readonly ItemModel for ElementTree Data structures
	see https://pypi.python.org/pypi/EuroPython2006_PyQt4_Examples/
	also read http://qt-project.org/doc/qt-4.8/itemviews-simpletreemodel.html
	"""
	_columns = ["Tag", "Attributes"]

	def __init__(self, etree_root_element):
		QAbstractItemModel.__init__(self)
		self._root = etree_root_element
		self.layoutChanged.connect(self._rebuild_index)
		self._rebuild_index()

	def _rebuild_index(self):
		self._np = dict((child, (parent, row_index)) for parent in self._root.iter()
						for row_index, child in enumerate(parent))

	def data(self, index, role):
		if not (index.isValid() and role == Qt.DisplayRole): return
		element = index.internalPointer()
		if index.column() == 0:
			return element.tag
		return ";".join("%s=\"%s\"" % (k, v) for k, v in element.items())

	def headerData(self, section, orientation, role):
		if orientation == Qt.Horizontal and role == Qt.DisplayRole:
			return self._columns[section]

	def index(self, row, column, parent=QModelIndex()):
		parent_item = parent.internalPointer() if parent.isValid() else self._root
		return self.createIndex(row, column, parent_item[row])

	def parent(self, index):
		if not index.isValid():
			return QModelIndex()
		parent_item, row_index = self._np[index.internalPointer()]
		if id(parent_item) == id(self._root):
			return QModelIndex()
		return self.createIndex(self._np[parent_item][1], 0, parent_item)

	def rowCount(self, parent):
		item = parent.internalPointer() if parent.isValid() else self._root
		return len(item)

	def columnCount(self, parent):
		return len(self._columns)


class QueueModel(ElementTreeModel):
	def rowCount(self, parent):
		# Only "package" nodes should have children in the view!
		item = parent.internalPointer() if parent.isValid() else self._root
		if item.tag == "item":
			return 0
		return len(item)