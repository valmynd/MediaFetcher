#!/usr/bin/env python3
from multiprocessing import Process, SimpleQueue, Event
from PySide.QtCore import *
from PySide.QtGui import *
import os

__author__ = "C. Wilhelm"
___license___ = "GPL v3"


class QueueProcess(Process):
	def __init__(self, task_queue, result_queue, function):
		Process.__init__(self)
		self.function = function
		self.task_queue = task_queue
		self.result_queue = result_queue
		self.soft_interrupt = Event()
		self.hard_interrupt = Event()
		# if daemon is true, python will handle termination of the process
		self.daemon = False

	def load_plugins(self):
		# load plugins from plugin directory (needs to be called when the process is using the plugin mechanism)
		filenames = os.listdir(os.path.dirname(os.path.realpath("../plugins")))
		modules = [f.replace('.py', '') for f in filenames if f.endswith('.py') and f != '__init__']
		for module in modules:
			__import__(module, locals(), globals(), level=1)

	def send_result(self, task_id, result_object, is_exception=False, is_ready=False):
		# always send process name to inform the pool which process is responsible for the task
		self.result_queue.put([self.name, task_id, result_object, is_exception, is_ready])

	def run(self):
		while True:
			# process blocks until queue contains something, so checking for interrupts is done below
			task_object = self.task_queue.get()  # must be an pickable iterable (list, tuple) -> see QueuePool.add_task()
			if self.soft_interrupt.is_set() or self.hard_interrupt.is_set():
				# grab as many tasks as we can and put the task we took to the start of the queue again
				task_objects = [task_object]
				while not self.task_queue.empty():
					task_objects.append(self.task_queue.get())
				for obj in task_objects:
					self.task_queue.put(obj)
				print('%s received Interrupt - Exiting' % self.name)
				break
			if task_object is None:
				# poison pill technique is still needed when the entire pool is shutdown,
				# as self.task_queue.get() would block as long as there are no new entries
				# in the queue and sometimes the event takes longer than the poison pill
				break
			try:
				self.function(*task_object)
			except Exception as e:
				task_id = task_object[0]
				self.send_result(task_id, str(e), is_exception=True)


def compute(self, num_row):
	"""
	Example Function taking random amount of time
	"""
	import time
	import random

	self.send_result(num_row, 0)
	random_number = random.randint(1, 10)
	for second in range(random_number):
		if self.hard_interrupt.is_set():
			print("hard_interrupt.is_set")
			return
		progress = float(second) / float(random_number) * 100
		self.send_result(num_row, progress)
		#if second in (4,5):
		#	raise Exception("Test Exception")s
		time.sleep(1)
	self.send_result(num_row, 100, is_ready=True)


class QueuePool(object):
	Process = QueueProcess

	def __init__(self, callback, pool_size=1, check_intervall=2):
		self.task_queue = SimpleQueue()
		self.result_queue = SimpleQueue()
		self._callback = callback
		self._pool = {}  # {process_name: process}
		self._tasks = {}  # {task_id: process_name}
		for _ in range(pool_size):
			process = self.Process(self.task_queue, self.result_queue)
			self._pool[process.name] = process
			process.start()
		# Check for progress periodically TODO: stop timer when queue is empty!
		self.timer = QTimer()
		self.timer.timeout.connect(self._check_for_results)
		self.timer.start(check_intervall * 1000)

	def _check_for_results(self):
		while not self.result_queue.empty():
			process_name, task_id, result_object, is_exception, is_ready = self.result_queue.get()
			print(process_name, task_id, result_object, is_exception, is_ready)
			if is_ready or is_exception:
				if task_id in self._tasks:
					del self._tasks[task_id]
			else:
				self._tasks[task_id] = process_name
			self._callback(task_id, result_object, is_exception, is_ready)

	def change_check_interval(self, new_interval_in_seconds):
		try:
			interval = float(new_interval_in_seconds)
		except ValueError:
			return
		self.timer.stop()
		self.timer.start(interval * 1000)

	def change_pool_size(self, new_pool_size):
		try:
			diff = int(new_pool_size) - len(self._pool)
		except ValueError:
			return
		if diff < 0:
			for _ in range(abs(diff)):
				process_name, process = self._pool.popitem()
				process.soft_interrupt.set()
		else:
			for _ in range(diff):
				process = QueueProcess(self.task_queue, self.result_queue, function=compute)
				self._pool[process.name] = process
				process.start()

	def add_task(self, task_id, *params):
		self.task_queue.put([task_id] + list(params))

	def cancel_task(self, task_id):
		process_name = self._tasks.get(task_id)
		if process_name is None:
			# task is not active, but it might be part of task_queue where it shall be removed from
			task_objects = []
			while not self.task_queue.empty():
				task_objects.append(self.task_queue.get())
			for obj in task_objects:
				if task_id != obj[0]:
					self.task_queue.put(obj)
			return
		process = self._pool.get(process_name)
		if process is None:
			# process might be already stopped -> ignore for now
			return
		process.hard_interrupt.set()

	def shutdown(self):
		for process in self._pool.values():
			process.hard_interrupt.set()
			self.task_queue.put(None)  # unblock queue

	def terminate(self):
		for process in self._pool.values():
			if process.exitcode is None:
				process.terminate()


class TestApp(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self)
		self.spinBoxPNum = QSpinBox()
		self.spinBoxIVal = QDoubleSpinBox()
		self.toolBar = self.addToolBar("Toolbar")
		self.toolBar.addAction(QAction('Add Task', self, triggered=self.addTask))
		self.toolBar.addWidget(QLabel(" Number of Processes:"))
		self.toolBar.addWidget(self.spinBoxPNum)
		self.toolBar.addWidget(QLabel(" Update Interval:"))
		self.toolBar.addWidget(self.spinBoxIVal)
		self.table = QTableWidget()
		self.table.verticalHeader().hide()
		self.table.setColumnCount(2)
		self.table.setContextMenuPolicy(Qt.CustomContextMenu)
		self.table.customContextMenuRequested.connect(self.showContextMenu)
		self.table.setSelectionMode(QAbstractItemView.SingleSelection)
		self.setCentralWidget(self.table)
		self.resize(400, 600)

		# Add a number of Test Tasks
		self.spinBoxPNum.setValue(0)
		self.spinBoxIVal.setValue(1)
		self.pool = QueuePool(callback=self.handleProgress,
		                      pool_size=self.spinBoxPNum.value(),
		                      check_intervall=self.spinBoxIVal.value())
		self.spinBoxPNum.valueChanged.connect(self.pool.change_pool_size)
		self.spinBoxIVal.valueChanged.connect(self.pool.change_check_interval)
		self.spinBoxIVal.setSingleStep(0.2)
		for _ in range(15):
			self.addTask()

	def closeEvent(self, event):
		#self.pool.terminate()
		self.pool.shutdown()

	def addTask(self):
		num_row = self.table.rowCount()
		self.pool.add_task(num_row)
		label = QLabel("Queued")
		bar = QProgressBar()
		bar.setValue(0)
		self.table.setRowCount(num_row + 1)
		self.table.setCellWidget(num_row, 0, label)
		self.table.setCellWidget(num_row, 1, bar)

	def showContextMenu(self, pos):
		menu = QMenu()
		menu.addAction(QAction('Pause', self, triggered=self.pause))
		globalPos = self.mapToGlobal(pos)
		menu.exec_(globalPos)

	def handleProgress(self, num_row, result, failed, finished):
		#print("received progress of %s at %s" % (result, num_row))
		label = self.table.cellWidget(num_row, 0)
		if failed:
			label.setText(result)
			return
		bar = self.table.cellWidget(num_row, 1)
		bar.setValue(result)
		if result == 100:
			label.setText('Finished')
		elif label.text() == 'Queued':
			label.setText('Downloading')

	def pause(self):
		num_row = self.table.currentRow()
		label = self.table.cellWidget(num_row, 0)
		label.setText("Paused")
		self.pool.cancel_task(num_row)


if __name__ == '__main__':  # run TestApp
	import sys

	app = QApplication(sys.argv)
	main_window = TestApp()
	main_window.show()
	sys.exit(app.exec_())