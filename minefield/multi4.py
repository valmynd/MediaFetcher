from multiprocessing import Pool, TimeoutError
from time import sleep


def upload(filename):
	print('start upload(): %d' % filename)
	sleep(4)
	print('end upload(): %d' % filename)


ingoing = [n for n in range(10)]

pool = Pool(processes=4)
#pool.map(upload, ingoing)

for n in ingoing:
	result = pool.apply_async(upload, (n,))

for n in ingoing: # separate loop!
	try:
		print(result.get(timeout=2))
	except TimeoutError as e:
		print('timed out: %d' % n)

