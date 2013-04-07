import os
import subprocess
import multiprocessing


def q_runner(n_procs, list_item, function, *args):
	'''generic function used to start worker processes'''
	task_queue = multiprocessing.Queue()
	results_queue = multiprocessing.JoinableQueue()
	if args:
		arguments = (task_queue, results_queue,) + args
	else:
		arguments = (task_queue, results_queue,)
	results = []
	# reduce processer count if proc count > files
	if len(list_item) < n_procs:
		n_procs = len(list_item)
	for l in list_item:
		task_queue.put(l)
	for _ in range(n_procs):
		p = multiprocessing.Process(target=function, args=arguments).start()
	for _ in range(len(list_item)):
		# indicate done results processing
		results.append(results_queue.get())
		results_queue.task_done()
	#tell child processes to stop
	for _ in range(n_procs):
		task_queue.put('STOP')
	# join the queue until we're finished processing results
	results_queue.join()
	# not closing the Queues caused me untold heartache and suffering
	task_queue.close()
	results_queue.close()
	return results


def worker1(input, output):
	'''worker process'''
	for c in iter(input.get, 'STOP'):
		# do some stuff
		my_sub_call = subprocess.Popen('sleep 1', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate(None)
		# stick the ouput somewhere
		output.put(str(c) + 'a')

def time_consumer(x):
	print(x)
	#time.sleep(random.randint(2, 4))
	#return x

n_procs = 6
list_item = range(10)
r1 = q_runner(n_procs, list_item, worker1)
print('first process completed')
r2 = q_runner(n_procs, list_item, worker1)
print('second process completed')