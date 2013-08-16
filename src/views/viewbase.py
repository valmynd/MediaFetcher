from PySide.QtCore import *
from PySide.QtGui import *


class QueueTreeView(QTreeView):
	_ignored_columns = [] # columns that would break the table layout, e.g. multiline descriptions, thumbnails

	def __init__(self, model):
		QTreeView.__init__(self)
		self.setModel(model)

		# Configure Header
		self.header().setContextMenuPolicy(Qt.CustomContextMenu)
		self.header().customContextMenuRequested.connect(self.chooseColumns)
		self.columnMenu = QMenu()
		for i, column_title in enumerate(model._columns):
			if column_title in self._ignored_columns:
				self.setColumnHidden(i, True)
				continue
			qa = QAction(column_title, self, checkable=True, checked=True, triggered=self.toggleColumn)
			self.columnMenu.addAction(qa)

		# Setup Context Menu
		self.setContextMenuPolicy(Qt.CustomContextMenu)
		self.customContextMenuRequested.connect(self.showContextMenu)

		# Other basic configuration
		#self.setAlternatingRowColors(True) # Somehow doesn't work too well when Delegates are used
		self.header().setMaximumHeight(21)
		self.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.setSelectionMode(QAbstractItemView.ExtendedSelection)

	def removeSelected(self):
		# QAbstractItemModel.removeRows() expects the removed rows to be one after another and within the same parent!
		# corrupting the tree structure must be avoided! initially the idea was that rows that were missed to remove
		# in a first run would still be selected, so they could be removed in a next run, but that was not entirelly
		# true, as sometimes the rows that were still selected were different from the initially selected...
		# strategy: remove the last rows with the deepest nesting first to avoid errors because of missing indices
		rows_by_parent = {}
		parents_by_depth = {}
		# indices within QItemSelectionModel are in the order in which they were selected -> we must sort them by depth!
		for index in self.selectionModel().selectedRows():
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
				self.model().removeListOfRows(rows_by_parent[parent], parent)

	def removeAll(self):
		self.model().removeAll()

	def toggleColumn(self):
		column_title = self.sender().text()
		i = self.model()._columns.index(column_title)
		self.setColumnHidden(i, not self.isColumnHidden(i))

	def chooseColumns(self, pos):
		globalPos = self.mapToGlobal(pos)
		self.columnMenu.exec_(globalPos)

	def showContextMenu(self, pos):
		raise NotImplementedError

	def updateProgress(self):
		pass


def get_depth_of_index(index, i=0):
	""" return (int) depth of an QModelIndex in a QTreeView """
	if index.isValid():
		return get_depth_of_index(index.parent(), i + 1)
	return i