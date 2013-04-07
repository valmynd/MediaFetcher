import multiprocessing
import time

def func1():
	print('Starting:', multiprocessing.current_process().name)
	time.sleep(10)
	print('Exiting :', multiprocessing.current_process().name)

def func2():
	print('Starting:', multiprocessing.current_process().name)
	print('Exiting :', multiprocessing.current_process().name)

if __name__ == '__main__':
	a = multiprocessing.Process(name='a', target=func1)
	b = multiprocessing.Process(name='b', target=func2)
	a.start()
	b.start()

	a.join(1)
	print('a.is_alive()', a.is_alive())
	b.join()
