import multiprocessing
import time
import random

from PySide.QtGui import *

def consumer(task_queue):
	# consumer-processes take tasks from the queue
	#multiprocessing.Queue().empty()
	#while not task_queue.empty():
	while True:
		msg = task_queue.get()
		task_queue.task_done()

def producer(result_queue):
	# producer-processes produce data in some form and put them into a common data structure
	time.sleep(random.randint(1, 10))
	result_queue.put("yay")

class MainWindow(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self)
		self.toolBar = self.addToolBar("Toolbar")
		self.toolBar.addAction(QAction('Add Task', self, triggered=self.addTask))
		self.list = QListWidget()
		self.setCentralWidget(self.list)

		# Establish communication queues
		self.task_queue = multiprocessing.JoinableQueue(maxsize=100)
		self.result_queue = multiprocessing.Queue()
		self.consumer = multiprocessing.Process(target=consumer, args=(self.task_queue,))
		self.consumer.daemon = True

	def logResult(self, result):
		"""
		This is called whenever time_consumer(i) returns a result.
		result_list is modified only by the main process, not the pool workers.
		"""
		self.result_list.append(result)

	def addTask(self):
		item = QListWidgetItem("item")
		self.list.addItem(item)

if __name__ == '__main__':
	import sys

	app = QApplication(sys.argv)
	main_window = MainWindow()
	main_window.show()
	sys.exit(app.exec_())