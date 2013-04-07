"""
multi_queue.py
"""
from multiprocessing import Process, Queue
import time


def reader(queue):
	while True:
		msg = queue.get()
		if msg == 'DONE':
			break


def writer(count, queue):
	for i in range(0, count):
		queue.put(i)
	queue.put('DONE')


if __name__ == '__main__':
	count = 10

	queue = Queue()
	reader_p = Process(target=reader, args=((queue),))
	reader_p.daemon = True
	reader_p.start()     # Launch the reader process

	_start = time.time()
	writer(count, queue)    # Send a lot of stuff to reader()
	reader_p.join()         # Wait for the reader to finish
	print("Sending %s numbers to Queue() took %s seconds" % (count, (time.time() - _start)))