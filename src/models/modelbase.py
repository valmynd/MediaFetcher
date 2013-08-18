from PySide.QtCore import *
from xml.etree import ElementTree as etree


class ElementTreeModel(QAbstractItemModel):
	"""
	Model for ElementTree Data Structures

	inspired by: https://pypi.python.org/pypi/EuroPython2006_PyQt4_Examples/
	also read: http://qt-project.org/doc/qt-4.8/itemviews-simpletreemodel.html
	qt5: http://qt-project.org/doc/qt-5.0/qtwidgets/model-view-programming.html#model-subclassing-reference
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
		if index.isValid() and role in (Qt.DisplayRole, Qt.EditRole):
			# note: if Qt.EditRole ain't accepted, QDataWidgetMapper wouldn't work properly
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
			print("tried Row: %s in %s" % (row, str(parent_element)))
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
		# returning 1 is actually the trick to have the hole row selected as DropIndicator!
		# alternative: return len(self._columns) // some behaviour would need to be adjusted, then
		return 1

	def supportedDropActions(self):
		return Qt.MoveAction

	def mimeTypes(self):
		return ['text/xml']

	def mimeData(self, indexes):
		# indexes would contain doublettes, if columnCount() returns something else than 1!
		strings = [etree.tostring(index.internalPointer(), encoding="unicode") for index in indexes]
		clipboard = "<clipboard>%s</clipboard>" % "".join(strings)
		mimedata = QMimeData()
		mimedata.setData('text/xml', clipboard)
		return mimedata

	def dropMimeData(self, mimedata, action, row, column, parent):
		if "text/xml" not in mimedata.formats():
			return False
		parent_element = parent.internalPointer() if parent.isValid() else self._root
		elements = list(etree.fromstring(str(mimedata.data("text/xml"))))
		row = len(parent_element) if row == -1 else row
		self.beginInsertRows(parent, row, row + len(elements) - 1)
		for element in reversed(elements):
			parent_element.insert(row, element)
		# the internal dict must be rebuilt, as row-numbers might have changed!
		self._init_internal_dict()
		self.endInsertRows()
		return True

	def removeRows(self, row, count, parent=QModelIndex()):
		""" implementation of QAbstractItemModel.removeRows(), called by most other remove*() methods """
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
		""" variant of removeRows() which takes a lists of rows allowing gaps between the rows """
		# the rows will be removed in groups where one row follows another
		# remove the last rows first to avoid errors with missing indices!
		rows.sort(reverse=True)
		count = 1
		last = -1
		for row in rows.copy():
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

	def removeScatteredRows(self, selected_indexes=[]):
		""" variant of removeRows() which takes a lists of selected indices no matter to which parent they belong """
		# QAbstractItemModel.removeRows() expects the removed rows to be one after another and within the same parent!
		# corrupting the tree structure must be avoided! initially the idea was that rows that were missed to remove
		# in a first run would still be selected, so they could be removed in a next run, but that was not entirelly
		# true, as sometimes the rows that were still selected were different from the initially selected...
		# strategy: remove the last rows with the deepest nesting first to avoid errors because of missing indices
		rows_by_parent = {}
		parents_by_depth = {}
		# indices within QItemSelectionModel are in the order in which they were selected -> we must sort them by depth!
		for index in selected_indexes:
			parent = index.parent()
			if parent not in rows_by_parent:
				rows_by_parent[parent] = []
			rows_by_parent[parent].append(index.row())
		for index in rows_by_parent.keys():
			depth = get_depth_of_index(index)
			if depth not in parents_by_depth:
				parents_by_depth[depth] = []
			parents_by_depth[depth].append(index)
		descending_depths = sorted(parents_by_depth.keys(), reverse=True)
		for depth in descending_depths:
			# that list of parent elements within the current depth must be ordered by their rownumbers!
			parents_by_depth[depth].sort(key=lambda i: i.row(), reverse=True)
			# print([i.row() for i in parents_by_depth[depth]])
			for parent in parents_by_depth[depth]:
				self.removeListOfRows(rows_by_parent[parent], parent)

	def removeAll(self):
		""" variant of removeRows() which flushes the entire tree """
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

	def flags(self, index):
		return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled

	def rowCount(self, parent):
		# Only "package" nodes should have children in the view!
		item = parent.internalPointer() if parent.isValid() else self._root
		if item.tag == "item":
			return 0
		return len(item)

	def dropMimeData(self, mimedata, action, row, column, parent):
		# Only "package" nodes should accept drops!
		parent_element = parent.internalPointer() if parent.isValid() else self._root
		if row == -1 and parent_element.tag not in ("queue", "package"):
			element = parent_element
			parent = parent.parent()
			parent_element = parent.internalPointer() if parent.isValid() else self._root
			row = list(parent_element).index(element)
		return ElementTreeModel.dropMimeData(self, mimedata, action, row, column, parent)


def get_depth_of_index(index):
	""" return (int) depth of an QModelIndex in a QTreeView """
	depth = 0
	while index.isValid():
		index = index.parent()
		depth += 1
	return depth