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
		self.parent().openPersistentEditor(index)  # forces the item into "edit" mode


class DownloadView(QueueTreeView):
	_ignored_columns = ['Path']

	def __init__(self):
		download_model = DownloadModel("models/clipboard_example.xml")
		QueueTreeView.__init__(self, download_model)
		self.setItemDelegateForColumn(3, ProgressBarDelegate(self, download_model))

		self.infoAction = QAction('Info', self, triggered=self.showInfo)

	def showContextMenu(self, pos):
		menu = QMenu()
		menu.addAction(self.infoAction)
		globalPos = self.mapToGlobal(pos)
		menu.exec_(globalPos)

	def addClipboardElement(self, element):
		self.model().addElement(element) # forward to model