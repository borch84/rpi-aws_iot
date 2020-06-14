import threading

e = threading.Event()
threads = []

def runner():
    tname = threading.current_thread().name
    print ('Thread waiting for event: %s' % tname)
    e.wait()
    print ('Thread got event: %s' % tname)

for t in range(100):
    t = threading.Thread(target=runner)
    threads.append(t)
    t.start()

s = input('-->')
e.set()
e.clear()
for t in threads:
    t.join()
print ('All done.')