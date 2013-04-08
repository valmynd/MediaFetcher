#!/usr/bin/env python

import multiprocessing, time, random
from PySide.QtCore import *
from PySide.QtGui import *


def compute(num):
	print("worker() started at %d" % num)
	random_number = random.randint(1, 6)
	if random_number in (2, 4, 6):
		raise Exception('Random Exception in _%d' % num)
	time.sleep(random_number)
	return num


class MainWindow(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self)
		self.toolBar = self.addToolBar("Toolbar")
		self.toolBar.addAction(QAction('Add Task', self, triggered=self.addTask))
		self.list = QListWidget()
		self.setCentralWidget(self.list)

		# Pool of Background Processes
		self.pool = multiprocessing.Pool(processes=4)

	def addTask(self):
		num_row = self.list.count()
		self.pool.apply_async(func=compute, args=(num_row,), callback=self.receiveResult,
							  error_callback=self.receiveException)
		item = QListWidgetItem("item %d" % num_row)
		item.setForeground(Qt.gray)
		self.list.addItem(item)

	def receiveResult(self, result):
		assert isinstance(result, int)
		print("end_work(), where result is %s" % result)
		self.list.item(result).setForeground(Qt.darkGreen)

	def receiveException(self, exception):
		error = str(exception)
		_pos = error.find('_') + 1
		num_row = int(error[_pos:])
		item = self.list.item(num_row)
		item.setForeground(Qt.darkRed)
		item.setText(item.text() + ' Retry...')
		self.pool.apply_async(func=compute, args=(num_row,), callback=self.receiveResult,
							  error_callback=self.receiveException)


if __name__ == '__main__':
	import sys

	app = QApplication(sys.argv)
	main_window = MainWindow()
	main_window.show()
	sys.exit(app.exec_())