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
		self.setSelectionBehavior(QAbstractItemView.SelectRows)

		# Other basic configuration
		#self.setAlternatingRowColors(True) # Somehow doesn't work too well when Delegates are used
		self.header().setMaximumHeight(21)
		self.setSelectionBehavior(QAbstractItemView.SelectRows)

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