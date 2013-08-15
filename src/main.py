#!/usr/bin/env python3

___license___ = "GPL v3"

from PySide.QtCore import *
from PySide.QtGui import *
from views import ClipBoardView, DownloadView


class MainWindow(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self)
		self._initActions()
		self._initMenus()
		self._initToolBars()
		self._initTrayIcon()
		self._initTabs()
		self.setWindowTitle("Media Fetcher")
		self.setWindowIcon(QIcon("../img/icon.png"))
		self.resize(600, 400)
		self.statusBar()

		# monitor Clipboard
		QApplication.clipboard().dataChanged.connect(self.clipBoardChanged)
		if QSystemTrayIcon.isSystemTrayAvailable():
			self.trayIcon.show()

		# Check for progress periodically
		self.timer = QTimer()
		self.timer.timeout.connect(self.updateProgress)
		self.timer.start(2000)

	def _initActions(self):
		self.openAction = QAction("&Open...", self, shortcut=QKeySequence.Open, triggered=self.open)
		self.startAction = QAction("&Start All", self, triggered=self.dummy)
		self.pauseAction = QAction("&Pause All", self, triggered=self.dummy)
		self.toggleStatusBarAction = QAction("Statusbar", self, checkable=True, checked=True,
											 triggered=self.toggleStatusBar)
		self.settingsAction = QAction("Prefere&nces", self, triggered=self.dummy)
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

	def _initMenus(self):
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
		self.viewMenu.addAction(self.toggleStatusBarAction)

		self.helpMenu = QMenu("&Help", self)
		self.helpMenu.addAction(self.aboutAction)

		self.menuBar().addMenu(self.fileMenu)
		self.menuBar().addMenu(self.editMenu)
		self.menuBar().addMenu(self.viewMenu)
		self.menuBar().addMenu(self.helpMenu)

	def _initToolBars(self):
		# http://aseigo.blogspot.de/2006/08/sweep-sweep-sweep-ui-floor.html
		self.searchBar = QLineEdit()
		self.toolBar = self.addToolBar("Toolbar")
		self.toolBar.addAction(self.openAction)
		self.toolBar.addWidget(self.searchBar)
		self.toolBar.addAction(self.searchAction)
		#self.toolBar.addAction(self.startAction)
		self.toolBar.addAction(self.pauseAction)
		self.toolBar.addAction(self.settingsAction)
		self.toolBar.setMovable(False)
		#self.searchAction.setDisabled(True)
		self.pauseAction.setDisabled(True) # QPushButton !

	def _initTrayIcon(self):
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

	def _initTabs(self):
		self.tabBar = QTabWidget()
		self.setCentralWidget(self.tabBar)

		# Downloads Tab
		self.download_view = DownloadView()
		self.tabBar.addTab(self.download_view, "Downloads")

		# Clipboard Tab
		self.clipboard_view = ClipBoardView(self.download_view)
		self.tabBar.addTab(self.clipboard_view, "Clipboard")
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
		fileName = QFileDialog.getOpenFileName(self, "Open File", QDir.currentPath())
		if fileName:
			pass

	def about(self):
		QMessageBox.about(self, "About Media Fetcher", "Text")

	def search(self, text=None):
		# TODO: ignore/warn/ask when url is already in the clipboard
		#if text is None:
		#	text = self.searchBar.text().strip()
		#if '//' in text: # contains URL
		self.clipboard_view.addURL("http://www.youtube.com/watch?v=v776jlfm7vE")

	def updateProgress(self):
		self.tabBar.currentWidget().updateProgress()

	def toggleStatusBar(self):
		self.statusBar().show() if self.statusBar().isHidden() else self.statusBar().hide()

	def trayActivated(self, reason):
		if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
			self.showNormal() if self.isHidden() else self.hide()


if __name__ == '__main__':
	import sys
	from utils.youtube_dl.utils import *
	jar = compat_cookiejar.CookieJar()
	cookie_processor = compat_urllib_request.HTTPCookieProcessor(jar)
	proxy_handler = compat_urllib_request.ProxyHandler()
	opener = compat_urllib_request.build_opener(proxy_handler, cookie_processor, YoutubeDLHandler())
	compat_urllib_request.install_opener(opener)
	socket.setdefaulttimeout(60)

	app = QApplication(sys.argv)
	main_window = MainWindow()
	main_window.show()
	sys.exit(app.exec_())
