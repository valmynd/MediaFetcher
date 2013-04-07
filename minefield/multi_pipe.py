"""
multi_pipe.py
"""
from multiprocessing import Process, Pipe
import time


def reader(pipe):
	output_p, input_p = pipe
	input_p.close()    # We are only reading
	while True:
		try:
			msg = output_p.recv()    # Read msg off the pipe and do nothing
		except EOFError:
			break


def writer(count, input_p):
	for i in range(0, count):
		input_p.send(i)


if __name__ == '__main__':
	count = 10
	output_p, input_p = Pipe()
	reader_p = Process(target=reader, args=((output_p, input_p),))
	reader_p.start()     # Launch the reader process

	output_p.close()       # We no longer need this part of the Pipe()
	_start = time.time()
	writer(count, input_p) # Send a lot of stuff to reader()
	input_p.close()        # Ask the reader to stop when it reads EOF
	reader_p.join()
	print("Sending %s numbers to Pipe() took %s seconds" % (count, (time.time() - _start)))