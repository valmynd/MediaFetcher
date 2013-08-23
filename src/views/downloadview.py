from views.viewbase import *
from models.downloadmodel import DownloadModel


class ProgressBarDelegate(QStyledItemDelegate):
	def __init__(self, parent_widget, model):
		QStyledItemDelegate.__init__(self, parent_widget)
		self._model = model

	def createEditor(self, parent_widget, option, index):
		element = index.internalPointer()
		progressbar = self._model.progress_bars[element]
		progressbar.setMaximumHeight(self.sizeHint(option, index).height())
		progressbar.setParent(parent_widget)
		return progressbar

	def paint(self, painter, option, index):
		QStyledItemDelegate.paint(self, painter, option, index)  # takes care of background color
		element = index.internalPointer()
		if element.tag == 'item':
			self.parent().openPersistentEditor(index)  # forces the item into "edit" mode


class DownloadView(QueueTreeView):
	_ignored_columns = ['Url', 'Thumbnail', 'Description']
	_hidden_columns = ['Path', 'Filename', 'Extension', 'Quality']

	def __init__(self):
		download_model = DownloadModel("models/clipboard_example.xml")
		QueueTreeView.__init__(self, download_model)
		self.setItemDelegateForColumn(10, ProgressBarDelegate(self, download_model))

		self.pauseSelectedAction = QAction('Pause Selected', self, triggered=self.pauseSelected)
		self.resumeSelectedAction = QAction('Resume Selected', self, triggered=self.resumeSelected)
		self.removeSelectedAction = QAction('Remove Selected', self, triggered=self.removeSelected)
		self.removeAllAction = QAction('Remove All', self, triggered=self.removeAll)
		self.infoAction = QAction('Info', self, triggered=self.showInfo)

	def showContextMenu(self, pos):
		menu = QMenu()
		# TODO: grey out certain options, e.g. no "pause" if all selected items are paused
		menu.addAction(self.pauseSelectedAction)
		menu.addAction(self.resumeSelectedAction)
		menu.addSeparator()
		menu.addAction(self.removeSelectedAction)
		menu.addAction(self.removeAllAction)
		menu.addSeparator()
		menu.addAction(self.infoAction)
		globalPos = self.mapToGlobal(pos)
		menu.exec_(globalPos)

	def pauseSelected(self):
		pass

	def resumeSelected(self):
		pass

	def addClipboardElement(self, element):
		self.model().addElement(element) # forward to model