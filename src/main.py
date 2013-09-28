#!/usr/bin/env python3
from PySide.QtCore import *
from PySide.QtGui import *
from models.settingsmodel import SettingsModel
from views.clipboardview import ClipBoardView
from views.downloadview import DownloadView
from views.settingsview import SettingsDialog, SettingsToolBar, ConfigurableToolBar
import re

__author__ = "C. Wilhelm"
___license___ = "GPL v3"


class TrayIcon(QSystemTrayIcon):
	def __init__(self, main_window):
		QSystemTrayIcon.__init__(self, main_window)
		self.mainWindow = main_window
		self.activated.connect(self.trayActivated)
		self.setIcon(QIcon("../img/icon.png"))
		self.minimizeAction = QAction("Mi&nimize", self, triggered=main_window.hide)
		self.maximizeAction = QAction("Ma&ximize", self, triggered=main_window.showMaximized)
		self.restoreAction = QAction("&Restore", self, triggered=main_window.showNormal)
		self.quitAction = QAction("&Quit", self, shortcut="Ctrl+Q", triggered=main_window.close)
		self.quitAction.setIcon(QIcon.fromTheme("application-exit"))
		menu = QMenu(main_window)
		menu.addAction(self.minimizeAction)
		menu.addAction(self.maximizeAction)
		menu.addAction(self.restoreAction)
		menu.addSeparator()
		menu.addAction(self.quitAction)
		self.setContextMenu(menu)
		if QSystemTrayIcon.isSystemTrayAvailable():
			self.show()

	def trayActivated(self, reason):
		if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
			self.mainWindow.showNormal() if self.mainWindow.isHidden() else self.mainWindow.hide()


class SearchBar(QLineEdit):
	def __init__(self, callback=None):
		QLineEdit.__init__(self)
		self.button = QToolButton(self)
		self.button.setIcon(QIcon("../img/edit-clear.png"))
		self.button.setCursor(Qt.ArrowCursor)
		self.button.clicked.connect(self.clear)
		self.button.hide()
		self.textChanged.connect(self.toggleButton)
		if callback is not None:
			self.returnPressed.connect(lambda: callback(self.text()))
		#self.setFixedHeight(28)
		self.setPlaceholderText(" < Search Term or URL >")

	def resizeEvent(self, event):
		self.button.setStyleSheet("QToolButton {margin: 0 0 0 0; border: 0px;}")
		x = self.size().width() - self.button.sizeHint().width() - 2
		y = (self.size().height() + 1 - self.button.sizeHint().height()) / 2
		self.button.move(x, y)

	def toggleButton(self):
		self.button.setVisible(bool(self.text()))


class MainToolBar(ConfigurableToolBar):
	def __init__(self, main_window):
		ConfigurableToolBar.__init__(self, "Toolbar", main_window)
		self.mainWindow = main_window
		self.searchBar = SearchBar(callback=main_window.search)

		self.openAction = QAction("&Open Container File", self, triggered=main_window.open)
		self.startAction = QAction("&Start Downloads", self, triggered=self.togglePause)
		self.pauseAction = QAction("&Pause Downloads", self, triggered=self.togglePause)
		self.settingsAction = QAction("Prefere&nces", self, triggered=main_window.showSettings)
		self.searchAction = QAction("Search Button", self, triggered=lambda: self.searchBar.returnPressed.emit())
		self.openAction.setIcon(QIcon.fromTheme("folder-open"))
		self.startAction.setIcon(QIcon.fromTheme("media-playback-start"))
		self.pauseAction.setIcon(QIcon.fromTheme("media-playback-pause"))
		self.settingsAction.setIcon(QIcon.fromTheme("emblem-system"))
		self.searchAction.setIcon(QIcon.fromTheme("system-search"))

		self.searchBarAction = QWidgetAction(self)
		self.searchBarAction.setText("Search Bar")  # make it checkable in the menu of visible actions
		self.searchBarAction.setDefaultWidget(self.searchBar)

		self.startButton = QToolButton(self)
		self.startButton.setDefaultAction(self.startAction)
		self.startButtonAction = QWidgetAction(self)
		self.startButtonAction.setText("Start/Pause Downloads")
		self.startButtonAction.setDefaultWidget(self.startButton)

		self.addAction(self.openAction)
		self.addAction(self.searchBarAction)
		self.addAction(self.searchAction)
		self.addAction(self.startButtonAction)
		self.addAction(self.settingsAction)

	def togglePause(self):
		if self.startButton.defaultAction() == self.pauseAction:
			self.startButton.removeAction(self.pauseAction)
			self.startButton.setDefaultAction(self.startAction)
			self.startAction.setDisabled(False)
			self.pauseAction.setDisabled(True)
			self.mainWindow.downloadView.model().pause()
		else:
			self.startButton.removeAction(self.startAction)
			self.startButton.setDefaultAction(self.pauseAction)
			self.pauseAction.setDisabled(False)
			self.startAction.setDisabled(True)
			self.mainWindow.tabBar.setCurrentWidget(self.mainWindow.downloadView)
			self.mainWindow.downloadView.model().start()


class MainWindow(QMainWindow):
	aboutToQuit = Signal()

	def __init__(self):
		QMainWindow.__init__(self)
		self.setWindowTitle("Media Fetcher")
		self.setWindowIcon(QIcon("../img/icon.png"))
		self.tray = TrayIcon(self)
		self.settings = QSettings(QSettings.IniFormat, QSettings.UserScope, "MediaFetcher", "MediaFetcher")
		self.settingsPath = QFileInfo(self.settings.fileName()).absolutePath()
		self.settingsModel = SettingsModel(self.settings)
		self.settingsDialog = SettingsDialog(self, self.settingsModel)
		self.statusBar = SettingsToolBar(self, self.settingsModel)
		self.addToolBar(Qt.BottomToolBarArea, self.statusBar)
		self.toolBar = MainToolBar(self)
		self.addToolBar(Qt.TopToolBarArea, self.toolBar)
		self.initMenus()
		self.initTabs()

		self.loadSettings()
		self.aboutToQuit.connect(self.writeSettings)
		# monitor Clipboard
		QApplication.clipboard().dataChanged.connect(self.clipBoardChanged)

	def closeEvent(self, event):
		# http://qt-project.org/doc/qt-5.0/qtwidgets/qwidget.html#closeEvent
		# http://qt-project.org/doc/qt-5.0/qtcore/qcoreapplication.html#aboutToQuit
		self.aboutToQuit.emit()

	def loadSettings(self):
		self.resize(600, 400)

	def writeSettings(self):
		pass

	def showSettings(self):
		self.settingsDialog.open()

	def initMenus(self):
		# toolbar actions may be set to invisible (exceptions: start, pause), so the main menu can't use these!
		self.openAction = QAction("&Open Container File", self, shortcut=QKeySequence.Open, triggered=self.open)
		self.settingsAction = QAction("Prefere&nces", self, triggered=self.showSettings)
		self.openAction.setIcon(QIcon.fromTheme("folder-open"))
		self.settingsAction.setIcon(QIcon.fromTheme("emblem-system"))

		self.fileMenu = QMenu("&File", self)
		self.fileMenu.addAction(self.openAction)
		self.fileMenu.addSeparator()
		self.fileMenu.addAction(self.toolBar.startAction)
		self.fileMenu.addAction(self.toolBar.pauseAction)
		self.fileMenu.addSeparator()
		self.fileMenu.addAction(self.tray.quitAction)

		self.editMenu = QMenu("&Edit", self)
		self.editMenu.addAction(self.settingsAction)

		self.viewMenu = QMenu("&View", self)
		self.viewMenu.addAction(self.toolBar.toggleViewAction())
		self.viewMenu.addAction(self.statusBar.toggleViewAction())

		self.helpMenu = QMenu("&Help", self)
		self.helpMenu.addAction(QAction("About", self, triggered=self.about))

		self.menuBar().addMenu(self.fileMenu)
		self.menuBar().addMenu(self.editMenu)
		self.menuBar().addMenu(self.viewMenu)
		self.menuBar().addMenu(self.helpMenu)

	def addTab(self, widget, label, closable=True):
		i = self.tabBar.count()
		self.tabBar.addTab(widget, " %s " % label if not closable else label)
		button = self.tabBar.tabBar().tabButton(i, QTabBar.RightSide)
		button.setStyleSheet("QToolButton {margin: 0; padding: 0;}")
		if not closable:
			button.setFixedWidth(0)
		self.tabBar.setCurrentIndex(i)

	def initTabs(self):
		self.tabBar = QTabWidget()
		self.setCentralWidget(self.tabBar)
		self.tabBar.setTabsClosable(True)
		appropriate_height = QLineEdit().sizeHint().height()
		self.tabBar.setStyleSheet("QTabBar::tab {height: %spx;}" % appropriate_height)
		self.tabBar.tabCloseRequested.connect(lambda i: self.tabBar.removeTab(i))
		# Downloads Tab
		self.downloadView = DownloadView(self, self.settings)
		self.addTab(self.downloadView, "Downloads", closable=False)
		# Clipboard Tab
		self.clipboardView = ClipBoardView(self, self.settings, self.downloadView)
		self.addTab(self.clipboardView, "Clipboard", closable=False)

	def clipBoardChanged(self):
		if QApplication.clipboard().mimeData().hasText():
			self.addURL(QApplication.clipboard().text())

	def open(self):
		fileName = QFileDialog.getOpenFileName(self, "Open File", QDir.homePath())
		if fileName:
			pass

	def about(self):
		QMessageBox.about(self, "About Media Fetcher", "Text")

	def addURL(self, url):
		# TODO: ignore/warn/ask when url is already in the clipboard
		for url in re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+])+', url):
			self.clipboardView.addURL(url)
			self.tabBar.setCurrentWidget(self.clipboardView)

	def search(self, text):
		text = text.strip()
		if text == "":
			return
		if 'http' in text:
			return self.addURL(text)
		searchwidget = QLabel("placeholder")
		self.addTab(searchwidget, "Search for %s" % text)


if __name__ == '__main__':
	import sys

	app = QApplication(sys.argv)
	main_window = MainWindow()
	main_window.show()
	sys.exit(app.exec_())
