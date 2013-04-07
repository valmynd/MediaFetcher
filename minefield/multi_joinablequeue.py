"""
multi_joinablequeue.py
"""
from multiprocessing import Process, JoinableQueue
import time


def reader(queue):
	while True:
		msg = queue.get()
		queue.task_done()
		#print(msg)


def writer(count, queue):
	for i in range(0, count):
		queue.put(i)


if __name__ == '__main__':
	count= 10

	queue = JoinableQueue()
	reader_p = Process(target=reader, args=((queue),))
	reader_p.daemon = True
	reader_p.start()     # Launch the reader process

	_start = time.time()
	writer(count, queue) # Send a lot of stuff to reader()
	time.sleep(1)
	#queue.join()         # Wait for the reader to finish
	print("Sending %s numbers to JoinableQueue() took %s seconds" % (count, (time.time() - _start)))