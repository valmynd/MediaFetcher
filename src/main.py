#!/usr/bin/env python3
from PySide.QtCore import *
from PySide.QtGui import *
from models.settingsmodel import SettingsModel
from views.clipboardview import ClipBoardView
from views.downloadview import DownloadView
from views.settingsview import SettingsDialog, SettingsToolBar, SettingsWidgetMapper, SpinBoxAction
from plugins import *

__author__ = "C. Wilhelm"
___license___ = "GPL v3"


class MainWindow(QMainWindow):
	aboutToQuit = Signal()

	def __init__(self):
		QMainWindow.__init__(self)
		self.loadSettings()
		self.initActions()
		self.initMenus()
		self.initToolBars()
		self.initTrayIcon()
		self.initTabs()
		self.aboutToQuit.connect(self.writeSettings)
		self.setWindowTitle("Media Fetcher")
		self.setWindowIcon(QIcon("../img/icon.png"))
		self.resize(600, 400)

		# monitor Clipboard
		QApplication.clipboard().dataChanged.connect(self.clipBoardChanged)
		if QSystemTrayIcon.isSystemTrayAvailable():
			self.trayIcon.show()

	def closeEvent(self, event):
		# http://qt-project.org/doc/qt-5.0/qtwidgets/qwidget.html#closeEvent
		self.aboutToQuit.emit()

	def writeSettings(self):
		pass

	def loadSettings(self):
		self.settings = QSettings(QSettings.IniFormat, QSettings.UserScope, "MediaFetcher", "MediaFetcher")
		self.settingsPath = QFileInfo(self.settings.fileName()).absolutePath()
		self.settingsModel = SettingsModel(self.settings)
		self.settingsDialog = SettingsDialog(self, self.settingsModel)
		self.mapper = SettingsWidgetMapper(self.settingsModel)
		self.mapper.setSubmitPolicy(QDataWidgetMapper.AutoSubmit)
		self.bottomBar = SettingsToolBar(self, self.settingsModel)
		self.addToolBar(Qt.BottomToolBarArea, self.bottomBar)

	def showSettings(self):
		self.settingsDialog.open()

	def initActions(self):
		self.openAction = QAction("&Open Container File", self, shortcut=QKeySequence.Open, triggered=self.open)
		self.startAction = QAction("&Start Downloads", self, triggered=self.togglePause)
		self.pauseAction = QAction("&Pause Downloads", self, triggered=self.togglePause)
		self.statusBarAction = QAction("Statusbar", self, checkable=True, checked=True, triggered=self.toggleStatusBar)
		self.settingsAction = QAction("Prefere&nces", self, triggered=self.showSettings)
		self.aboutAction = QAction("About", self, triggered=self.about)
		self.searchAction = QAction("Search", self, triggered=self.search)

		self.minimizeAction = QAction("Mi&nimize", self, triggered=self.hide)
		self.maximizeAction = QAction("Ma&ximize", self, triggered=self.showMaximized)
		self.restoreAction = QAction("&Restore", self, triggered=self.showNormal)
		self.quitAction = QAction("&Quit", self, shortcut="Ctrl+Q", triggered=self.close)

		self.openAction.setIcon(QIcon.fromTheme("folder-open"))
		self.startAction.setIcon(QIcon.fromTheme("media-playback-start"))
		self.pauseAction.setIcon(QIcon.fromTheme("media-playback-pause"))
		self.settingsAction.setIcon(QIcon.fromTheme("emblem-system"))
		self.quitAction.setIcon(QIcon.fromTheme("application-exit"))
		self.searchAction.setIcon(QIcon.fromTheme("system-search"))

	def initMenus(self):
		self.fileMenu = QMenu("&File", self)
		self.fileMenu.addAction(self.openAction)
		self.fileMenu.addSeparator()
		self.fileMenu.addAction(self.startAction)
		self.fileMenu.addAction(self.pauseAction)
		self.fileMenu.addSeparator()
		self.fileMenu.addAction(self.quitAction)

		self.editMenu = QMenu("&Edit", self)
		self.editMenu.addAction(self.settingsAction)

		self.viewMenu = QMenu("&View", self)
		self.viewMenu.addAction(self.statusBarAction)

		self.helpMenu = QMenu("&Help", self)
		self.helpMenu.addAction(self.aboutAction)

		self.menuBar().addMenu(self.fileMenu)
		self.menuBar().addMenu(self.editMenu)
		self.menuBar().addMenu(self.viewMenu)
		self.menuBar().addMenu(self.helpMenu)

	def initToolBars(self):
		# http://aseigo.blogspot.de/2006/08/sweep-sweep-sweep-ui-floor.html
		self.searchBar = QLineEdit()
		self.startButton = QToolButton(self)
		self.startButton.setDefaultAction(self.startAction)
		self.toolBar = self.addToolBar("Toolbar")
		self.toolBar.addAction(self.openAction)
		self.toolBar.addWidget(self.searchBar)
		self.toolBar.addAction(self.searchAction)
		self.toolBar.addWidget(self.startButton)
		self.toolBar.addAction(self.settingsAction)
		self.toolBar.setMovable(False)

	def initTrayIcon(self):
		self.trayIconMenu = QMenu(self)
		self.trayIconMenu.addAction(self.minimizeAction)
		self.trayIconMenu.addAction(self.maximizeAction)
		self.trayIconMenu.addAction(self.restoreAction)
		self.trayIconMenu.addSeparator()
		self.trayIconMenu.addAction(self.quitAction)

		self.trayIcon = QSystemTrayIcon(self)
		self.trayIcon.setIcon(QIcon("../img/icon.png"))
		self.trayIcon.setContextMenu(self.trayIconMenu)
		self.trayIcon.activated.connect(self.trayActivated)

	def initTabs(self):
		self.tabBar = QTabWidget()
		self.setCentralWidget(self.tabBar)

		# Downloads Tab
		self.downloadView = DownloadView(self, self.settings)
		self.tabBar.addTab(self.downloadView, "Downloads")

		# Clipboard Tab
		self.clipboardView = ClipBoardView(self, self.settings, self.downloadView)
		self.tabBar.addTab(self.clipboardView, "Clipboard")
		self.tabBar.setCurrentIndex(1)

		# Close Button for all Tabs except Downloads, Clipboard
		self.tabBar.setTabsClosable(True)
		self.tabBar.tabBar().tabButton(0, QTabBar.RightSide).resize(0, 0)
		self.tabBar.tabBar().tabButton(1, QTabBar.RightSide).resize(0, 0)

	def clipBoardChanged(self):
		if not QApplication.clipboard().mimeData().hasText():
			return
		text = QApplication.clipboard().text()
		self.search(text)

	def dummy(self):
		#alert(str(self.downLoadList.getProgress(0)))
		#alert(str(self.clipBoardList.getQuality(0)))
		pass

	def open(self):
		fileName = QFileDialog.getOpenFileName(self, "Open File", QDir.homePath())
		if fileName:
			pass

	def about(self):
		QMessageBox.about(self, "About Media Fetcher", "Text")

	def search(self, text=None):
		# TODO: ignore/warn/ask when url is already in the clipboard
		#if text is None:
		#	text = self.searchBar.text().strip()
		#if '//' in text: # contains URL
		#self.clipboardView.addURL("http://www.youtube.com/watch?v=v776jlfm7vE")
		#self.tabBar.setCurrentWidget(self.clipboardView)
		pass

	def toggleStatusBar(self):
		self.bottomBar.show() if self.bottomBar.isHidden() else self.bottomBar.hide()

	def trayActivated(self, reason):
		if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
			self.showNormal() if self.isHidden() else self.hide()

	def togglePause(self):
		if self.startButton.defaultAction() == self.pauseAction:
			self.startButton.removeAction(self.pauseAction)
			self.startButton.setDefaultAction(self.startAction)
			self.startAction.setDisabled(False)
			self.pauseAction.setDisabled(True)
			self.downloadView.model().pause()
		else:
			self.startButton.removeAction(self.startAction)
			self.startButton.setDefaultAction(self.pauseAction)
			self.pauseAction.setDisabled(False)
			self.startAction.setDisabled(True)
			self.tabBar.setCurrentWidget(self.downloadView)
			self.downloadView.model().start()


if __name__ == '__main__':
	import sys

	app = QApplication(sys.argv)
	main_window = MainWindow()
	main_window.show()
	sys.exit(app.exec_())
