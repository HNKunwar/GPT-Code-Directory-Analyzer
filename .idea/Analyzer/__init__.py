import os
import sys
from threading import Thread
from queue import Queue
import asyncio

from gui import create_window

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Create a queue for tasks
queue = Queue()

# This function will run in a separate thread
def asyncio_thread():
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)

	while True:
		task = queue.get()
		if task is None:
			# If we get None, this means we should exit
			break
		# Otherwise, we assume the task is an asyncio coroutine and we run it
		loop.run_until_complete(task)

if __name__ == "__main__":
	# Create and start the asyncio thread
	asyncio_thread = Thread(target=asyncio_thread)
	asyncio_thread.start()

	window = create_window(queue)
	window.mainloop()

	# Once the Tkinter app ends, we add None to the queue to signal to the asyncio thread to exit
	queue.put(None)

	# Wait for the asyncio thread to finish
	asyncio_thread.join()
