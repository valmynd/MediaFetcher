#!/usr/bin/env python3
from multiprocessing import Process, SimpleQueue, Event
from PySide.QtCore import *
from PySide.QtGui import *
import os, sys

__author__ = "C. Wilhelm"
___license___ = "GPL v3"


class QueueProcess(Process):
	Plugins = []

	def __init__(self, task_queue, result_queue, function):
		Process.__init__(self)
		self.function = function
		self.task_queue = task_queue
		self.result_queue = result_queue
		self.soft_interrupt = Event()
		self.hard_interrupt = Event()
		# if daemon is true, python will handle termination of the process
		self.daemon = False

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
