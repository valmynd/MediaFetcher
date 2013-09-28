from PySide.QtCore import *
from PySide.QtGui import *
from views.settingsview import QFolderChooser
import tempfile
import os

__author__ = "C. Wilhelm"
___license___ = "GPL v3"

thumbnail_path = os.path.join(tempfile.gettempdir(), "mediafetcher_thumbnails")
if not os.path.exists(thumbnail_path):
	os.mkdir(thumbnail_path)


class QueueWidgetMapper(QDataWidgetMapper):
	def __init__(self, queue_model):
		"""
		create model-driven Widgets that are bound to a QueueModel
		@param queue_model: object of a subclass of models.modelbase.ElementTreeModel
		"""
		QDataWidgetMapper.__init__(self)
		self.queueModel = queue_model
		self.setModel(queue_model)

	def map(self, input_widget, column_name, alias=None):
		"""
		Shortcut for mapping a column name to a widget suitible for most use-cases

		@param column_name: column name (string) that is part of QueueModel._columns
		@param input_widget: QWidget that should be responsible for editing
		@param alias: label string to be used instead of the column name
		@return: QLabel object that can be used in forms
		"""
		num_col = self.queueModel._columns.index(column_name)
		self.addMapping(input_widget, num_col)
		if alias is not None:
			return QLabel(alias + ":")
		return QLabel(column_name + ":")


class ItemInfoWidget(QTextBrowser):
	def __init__(self):
		QTextBrowser.__init__(self)
		# templates; see http://qt-project.org/doc/qt-4.8/richtext-html-subset.html
		self.tmpl = '<b>%(title)s <a href="%(url)s">[Link]</a></b><br/>%(thumbnail)s %(description)s'
		self.link_tmpl = '<a href="%s"><img src="%s" height="80" align="left" style="margin-top:5px;margin-right:5px;" /></a>'
		self.load_tmpl = '<a href="%s">[Load Thumbnail]</a> '
		self.noThumbnail = '[No Thumbnail available] '
		# Only show placeholderlink, if there is a thumbnail avaiable
		self.setText("[No Information available]")
		self.setMaximumHeight(82)
		self.setOpenLinks(False)  # thus anchorClicked signal will always be emitted
		self.anchorClicked.connect(self.linkClicked)
		#self.setStyleSheet("QTextEdit {background-color: rgba(255, 255, 255, 1);}")
		self.current_element = None

	def linkClicked(self, qurl):
		url = qurl.toString()
		if self.current_element is None:
			return
		if url == self.current_element.get("url"):
			QDesktopServices.openUrl(qurl)
		elif url == self.current_element.get("thumbnail"):
			# TODO: Download to Thumbnails folder and call setToElement(self.current_element)
			local = "../img/thumbnail_placeholder.png"
			link = self.link_tmpl % (local, local)
			txt = self.tmpl % dict(title=self.current_element.get("title", "[No Title Available]"),
			                       url=self.current_element.get("url", "[No URL Available]"),
			                       thumbnail=link,
			                       description=self.current_element.get("description", "[No Description Available]"))
			self.setText(txt)
			self.reload()
		else:  # open thumbnail path
			thumbnail_path = os.path.dirname(os.path.realpath(url))
			QDesktopServices.openUrl(thumbnail_path)

	def setToElement(self, element):
		self.current_element = element
		link = self.load_tmpl % (element.get("thumbnail", "[No Thumbnail Available]"))
		txt = self.tmpl % dict(title=self.current_element.get("title", "[No Title Available]"),
		                       url=self.current_element.get("url", "[No URL Available]"),
		                       thumbnail=link,
		                       description=self.current_element.get("description", "[No Description Available]"))
		self.setText(txt)
		self.reload()


class InfoBoxDialog(QDialog):
	def __init__(self, parent_widget, model):
		QDialog.__init__(self, parent_widget)
		self.mapper = QueueWidgetMapper(model)
		self.mapper.setSubmitPolicy(QDataWidgetMapper.ManualSubmit)
		self.setWindowTitle("Clipboard Item Description")
		dialoglayout = QVBoxLayout()
		self.setLayout(dialoglayout)

		group = QGroupBox("Clipboard Information")
		layout = QFormLayout()
		group.setLayout(layout)
		dialoglayout.addWidget(group)
		self.infoBrowser = ItemInfoWidget()
		layout.addRow(self.infoBrowser)
		group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

		group = QGroupBox("Download Settings")
		layout = QFormLayout()
		group.setLayout(layout)
		dialoglayout.addWidget(group)
		self.folderField = QFolderChooser(self)
		self.folderLabel = self.mapper.map(self.folderField, "Path", "Download Folder")
		self.fileNameField = QLineEdit(self)
		self.fileNameLabel = self.mapper.map(self.fileNameField, "Filename", "File Name")
		layout.addRow(self.folderLabel, self.folderField)
		layout.addRow(self.fileNameLabel, self.fileNameField)
		self.fileNameLabel.setToolTip("Filename Template Conventions:\n"
		                              "%extension% → transform to lowercase (mp4)\n"
		                              "%EXTENSION% → transform to uppercase (MP4)\n"
		                              "%exTenSiOn% or something like that → no transformation\n\n"
		                              "Available Keywords: title, url, host, extension, quality")

		buttonbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
		buttonbox.accepted.connect(self.submit)
		buttonbox.rejected.connect(self.close)
		dialoglayout.addWidget(buttonbox)

	def open_for_selection(self, selected_index):
		self.mapper.setCurrentModelIndex(selected_index)
		element = selected_index.internalPointer()
		self.infoBrowser.setToElement(element)
		self.exec_()

	def submit(self):
		# TODO: when the filename or path changes and the file is already downloaded,
		#       ask user if the file shall be renamed or moved!!!
		if self.folderField.checkPermissions(self.folderField.text()):
			self.mapper.submit()
			self.close()
