import threading
from time import perf_counter

job = False

def work(name, master):
    global job
    if master:
        job = True
    while not job:
        pass
    starttime = perf_counter()
    longstarttime = perf_counter()
    for i in range(2):
        #print (f"{name} - step {i} in {perf_counter()-starttime} seconds.")
        starttime = perf_counter()
    print (f"{name} finished in {perf_counter()-longstarttime} seconds.")

timer = perf_counter()
t = []
for i in range(4):
    t.append(threading.Thread(target=work, args=(f"Task {i+1}",False)))
t.append(threading.Thread(target=work, args=(f"Task {5}",True)))
for i in range(5):
    t[i].start()
for i in range(5):
    t[i].join()
print (f"Program finished in {perf_counter()-timer} seconds.")
