from views.viewbase import *
from models.downloadmodel import DownloadModel


class ProgressBarDelegate(QStyledItemDelegate):
	def createEditor(self, parent, option, index):
		progressbar = QProgressBar(parent)
		progressbar.setMaximumHeight(self.sizeHint(option, index).height())
		return progressbar

	def paint(self, painter, option, index):
		QStyledItemDelegate.paint(self, painter, option, index) # takes care of background color
		self.parent().openPersistentEditor(index) # forces the item into "edit" mode


class DownloadView(QueueTreeView):
	_ignored_columns = ['Path']

	def __init__(self):
		download_model = DownloadModel("models/clipboard_example.xml")
		QueueTreeView.__init__(self, download_model)
		#self.setItemDelegateForColumn(3, ProgressBarDelegate(self))
		#self.setItemDelegateForColumn(4, ProgressBarDelegate(self))
		self.downloadMenu = QMenu()
		#info_action = QAction('Info', self, triggered=self.showInfo)
		#self.downloadMenu.addAction(info_action)

	def showContextMenu(self, pos):
		globalPos = self.mapToGlobal(pos)
		self.downloadMenu.exec_(globalPos)

	def addClipboardElement(self, element):
		self.model().addElement(element) # forward to model