import random
import threading
import time

lock = threading.Lock()

def threaded(func):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=(*args, *kwargs))
        thread.start()

    return wrapper

l = []
def changeList():
    global l

    l = []

    for i in range(random.randint(10 ** 2, 10 ** 3)):
        l.append([])
        for j in range(random.randint(10 ** 2, 10 ** 3)):
            l[i].append(j)

    print("gui l length is", len(l))


def iterThroughList():
    global l

    print("l length is", len(l))
    c = 0
    for i in range(len(l)):
        for j in range(len(l[i])):
            c = l[i][j]


@threaded
def gui():
    while 1:
        if not lock.locked():
            lock.acquire(False)
            print("gui")
            changeList()
            print("gui finished")
            lock.release()
            print("gui locked", lock.locked())


@threaded
def processor():
    while 1:
        if not lock.locked():
            lock.acquire(False)
            print("processor")
            iterThroughList()
            print("processor finished")
            lock.release()

            # print("processor locked", lock.locked())
            # print("poiuytrertyuio")



def main():

    gui()
    processor()

main()
