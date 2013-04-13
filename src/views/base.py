from PySide.QtCore import *
from PySide.QtGui import *


class QueueTreeView(QTreeView):
	def __init__(self, model):
		QTreeView.__init__(self)
		self.setModel(model)

		# Basic Configuration
		self.setAlternatingRowColors(True)
		self.setSelectionBehavior(QAbstractItemView.SelectRows)

		# Configure Header
		self.header().setContextMenuPolicy(Qt.CustomContextMenu)
		self.header().customContextMenuRequested.connect(self.chooseColumns)
		self.columnMenu = QMenu()
		for column_title in model._columns:
			qa = QAction(column_title, self, checkable=True, checked=True, triggered=self.toggleColumn)
			self.columnMenu.addAction(qa)

		# Setup Context Menu
		self.setContextMenuPolicy(Qt.CustomContextMenu)
		self.customContextMenuRequested.connect(self.showContextMenu)
		self.setSelectionBehavior(QAbstractItemView.SelectRows)

	def toggleColumn(self):
		column_title = self.sender().text()
		i = self.model()._columns.index(column_title)
		self.setColumnHidden(i, not self.isColumnHidden(i))

	def chooseColumns(self, pos):
		globalPos = self.mapToGlobal(pos)
		selectedItem = self.columnMenu.exec_(globalPos)

	def showContextMenu(self, pos):
		raise NotImplementedError

	def updateProgress(self):
		pass