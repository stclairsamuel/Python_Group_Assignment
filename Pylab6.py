import threading
import time

myTuple = ("tempName", 3)

def task(name, sleepTime):
    print(f"Thread {name}: starting...")
    time.sleep(sleepTime)
    print(f"Thread {name}: finishing.")

my_thread = threading.Thread(target=task, args=(myTuple[0], myTuple[1],))

# 2. Start the thread
my_thread.start()

print("Main thread: doing other work.")

# 3. Wait for the thread to finish before the main program exits
my_thread.join()

print("Main thread: all done.")