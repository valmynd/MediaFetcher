from PySide.QtCore import *
from PySide.QtGui import *
import os

__author__ = "C. Wilhelm"
___license___ = "GPL v3"


class QFolderChooser(QLineEdit):
	def __init__(self, parent_widget):
		QLineEdit.__init__(self, parent_widget)
		self.button = QToolButton(self)
		self.button.setText("Browse")
		self.button.setCursor(Qt.PointingHandCursor)
		self.button.clicked.connect(self.chooseFolder)
		self.realText = self.text()
		self.setStyleSheet("QLineEdit {background: rgb(220,220,220);}")

	def resizeEvent(self, event):
		self.button.setStyleSheet("QToolButton {margin: 2 0 2 0;}")
		x = self.size().width() - self.button.sizeHint().width()
		self.button.move(x, 0)

	def chooseFolder(self):
		folder = QFileDialog.getExistingDirectory(parent=self, dir=self.text())
		if self.checkPermissions(folder):
			self.setText(folder)

	def checkPermissions(self, folder):
		if not os.access(folder, os.W_OK):
			msg = QMessageBox(self)
			msg.setText("You have no writing priviliges\nfor that folder. Please try again!")
			msg.exec_()
			return False
		return True


class SettingsWidgetMapper(QDataWidgetMapper):
	def __init__(self, settings_model):
		"""
		create model-driven Widgets that are bound to a SettingsModel
		@param settings_model: models.settingsmodel.SettingsModel
		"""
		QDataWidgetMapper.__init__(self)
		self.settingsModel = settings_model
		self.setModel(settings_model)

	def map(self, input_widget, settings_key):
		"""
		Shortcut for mapping a settings key to a widget suitible for most use-cases

		@param settings_key: QSettings Key (string), e.g. "DefaultDownloadFolder"
		@param input_widget: QWidget that should be responsible for editing
		@return: QLabel object (with default label defined in SettingsModel)
		"""
		num_col = self.settingsModel._keys.index(settings_key)
		label_text = self.settingsModel._entries[settings_key]
		print(num_col, label_text)
		self.addMapping(input_widget, num_col)
		return QLabel(label_text)


class SettingsDialog(QDialog):
	def __init__(self, main_window, settings_model):
		QDialog.__init__(self, main_window)
		self.setWindowTitle("Preferences")
		self.settingsModel = settings_model
		self.mapper = SettingsWidgetMapper(self.settingsModel)
		self.mapper.setSubmitPolicy(QDataWidgetMapper.ManualSubmit)
		buttonbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
		buttonbox.accepted.connect(self.submit)
		buttonbox.rejected.connect(self.close)

		layout = QFormLayout()
		self.setLayout(layout)
		self.folderChooser = QFolderChooser(self)
		self.filenameChooser = QLineEdit()
		layout.addRow(self.mapper.map(self.folderChooser, "DefaultDownloadFolder"), self.folderChooser)
		layout.addRow(self.mapper.map(self.filenameChooser, "DefaultFileName"), self.filenameChooser)
		layout.addRow(QLabel())
		layout.addRow(buttonbox)

	def open(self):
		self.mapper.toFirst()
		self.exec_()

	def submit(self):
		if self.folderChooser.checkPermissions(self.folderChooser.text()):
			self.mapper.submit()
			self.close()


class SpinBoxAction(QWidgetAction):
	def __init__(self, parent, mapper, settings_key):
		QWidgetAction.__init__(self, parent)
		self.settings_key = settings_key
		self.mapper = mapper

	def createMainWidget(self):
		if self.settings_key == "PoolUpdateFrequency":
			return QDoubleSpinBox()
		return QSpinBox()

	def createWidget(self, parent):
		# From QT Docs: "When a QToolBar is not a child of a QMainWindow , it looses the ability to populate the
		# extension pop up with widgets added to the toolbar using QToolBar.addWidget() . Please use widget actions
		# created by inheriting QWidgetAction and implementing QWidgetAction.createWidget() instead"
		# -> if I would not do it this way, the QToolBarExtension Button would not work at all in this scenario
		#    (tried creating the widget in the constructor and calling setDefaultWidget() with the described result)
		widget = self.createMainWidget()
		label = self.mapper.map(widget, self.settings_key)
		widget = self.createMainWidget()
		layout = QHBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(label)
		layout.addWidget(widget)
		widget.setFixedHeight(label.sizeHint().height() + 5)
		default = QWidget(parent)
		default.setLayout(layout)
		default.setParent(parent)
		#self.setDefaultWidget(default)
		self.mapper.toFirst()
		return default


class SettingsStatusBar(QStatusBar):
	# depending on which tab is opened, show number of download or clipboard processes (etc.)
	# TODO: configurable short-cuts to settings in statusbar
	def __init__(self, main_window, settings_model):
		QStatusBar.__init__(self, main_window)
		self.mainWindow = main_window
		#self.mainWindow.tabBar.currentChanged.connect(self.changeContext)
		self.setSizeGripEnabled(False)
		self.label = QLabel("Download Speed: 0 kb/s")
		self.toolBar = QToolBar()
		self.toolBar.addWidget(self.label)
		self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.addWidget(self.toolBar, stretch=True)

		self.settingsModel = settings_model
		self.mapper = SettingsWidgetMapper(settings_model)
		self.mapper.setSubmitPolicy(QDataWidgetMapper.AutoSubmit)

		self.toolBar.addSeparator()
		self.toolBar.addAction(SpinBoxAction(self.toolBar, self.mapper, "DownloadSpeedLimit"))
		self.toolBar.addSeparator()
		self.toolBar.addAction(SpinBoxAction(self.toolBar, self.mapper, "PoolUpdateFrequency"))
		self.toolBar.addSeparator()
		self.toolBar.addAction(SpinBoxAction(self.toolBar, self.mapper, "DownloadProcesses"))
		self.toolBar.addSeparator()
		self.toolBar.addAction(SpinBoxAction(self.toolBar, self.mapper, "ExtractionProcesses"))