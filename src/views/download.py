from PySide.QtCore import *
from PySide.QtGui import *


class ProgressBarDelegate(QStyledItemDelegate):
	def createEditor(self, parent, option, index):
		progressbar = QProgressBar(parent)
		progressbar.setMaximumHeight(self.sizeHint(option, index).height())
		return progressbar

	def paint(self, painter, option, index):
		QStyledItemDelegate.paint(self, painter, option, index) # takes care of background color
		self.parent().openPersistentEditor(index) # forces the item into "edit" mode
