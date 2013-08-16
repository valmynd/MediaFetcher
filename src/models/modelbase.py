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
		# initially i implemented a _remove_from_internal_dict() counterpart, but that doesn't make sense since
		# usually dozens of row-numbers must change if an element is removed -> index shall be rebuilt, then!
		self._n[element] = (parent, num_row)
		for num_row, child in enumerate(element):
			self._add_to_internal_dict(child, element, num_row)

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
		""" returns QModelIndex object at row, column under parent, is used by qt internally """
		parent_element = parent.internalPointer() if parent.isValid() else self._root
		try:
			return self.createIndex(row, column, parent_element[row])
		except IndexError:
			if hasattr(self, "_remove_rows_active") and self._remove_rows_active:
				# beginRemoveRows() will ask for the row next row, even if it is the last!
				if row == len(parent_element):
					return QModelIndex()
			print("tried Row: %s" % row)
			raise

	def parent(self, index):
		""" returns QModelIndex object for the parent element, is used by qt internally """
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

	def removeRows(self, row, count, parent=QModelIndex()):
		parent_element = parent.internalPointer() if parent.isValid() else self._root
		# from qt documentation: is important to notify any connected views about changes to the model's dimensions both
		# before and after they occur (otherwise the view will relentlessly ask for the parent of the removed element!)
		self._remove_rows_active = True  # flag for exception in index()
		self.beginRemoveRows(parent, row, row + count - 1)
		self._remove_rows_active = False
		indexes = [self.index(row + i, 0, parent) for i in range(count)]
		elements = [index.internalPointer() for index in indexes]
		for element in elements:
			parent_element.remove(element)
		# the internal dict must be rebuilt, as row-numbers have changed!
		self._init_internal_dict()
		self.endRemoveRows()
		return True

	def removeListOfRows(self, rows=[], parent=QModelIndex()):
		# the rows will be removed in groups where one row follows another
		rows.sort(reverse=True)
		count = 1
		last = -1
		for row in list(rows):
			if last - row == 1:
				if last != -1:
					count += 1
			elif last != -1:
				break
			last = row
			rows.remove(row)
		self.removeRows(last, count, parent)
		if len(rows) > 0:  # do the same thing with the next cluster
			self.removeListOfRows(rows, parent)

	def removeAll(self):
		self.beginResetModel()
		self._root.clear()
		self._init_internal_dict()
		self.endResetModel()

	def addElement(self, element):
		# parameters first and last of beginInsertRows() are the row numbers that the new rows will have
		row_number = len(self._root)
		self.beginInsertRows(QModelIndex(), row_number, row_number)
		self._root.append(element)
		self._add_to_internal_dict(element, self._root, row_number)
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