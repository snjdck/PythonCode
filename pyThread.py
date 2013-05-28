import thread
_start_new_thread = thread.start_new_thread
_allocate_lock = thread.allocate_lock
_get_ident = thread.get_ident
del thread

from collections import deque

class Lock(object):
    def __init__(self):
        self._mutex = _allocate_lock()
        self._owner = None
        
    def acquire(self):
        self._mutex.acquire()
        self._owner = _get_ident()
        
    def release(self):
        self._owner = None
        self._mutex.release()
        
    def isOwner(self):
        return _get_ident() == self._owner


class Condition(object):
    def __init__(self, lock=None):
        self._lock = lock or Lock()
        self._waiters = []
        
        self.acquire = self._lock.acquire
        self.release = self._lock.release
        self.isOwner = self._lock.isOwner
    
    def waitIf(self, test):
        while test():
            self.wait()
                
    def wait(self):
        assert self.isOwner()
        waiter = Lock()
        waiter.acquire()
        self._waiters.append(waiter)
        self.release()
        waiter.acquire()
        self.acquire()
    
    def notify(self, n=1):
        assert self.isOwner()
        while n > 0 and len(self._waiters) > 0:
            self._waiters.pop().release()
            n -= 1
            
    def notifyAll(self):
        self.notify(len(self._waiters))
        

class Event(object):
    def __init__(self):
        self._cond = Condition()
        self._flag = False
        
    def set(self):
        self._cond.acquire()
        self._flag = True
        self._cond.notifyAll()
        self._cond.release()
        
    def clear(self):
        self._cond.acquire()
        self._flag = False
        self._cond.release()
        
    def wait(self):
        self._cond.acquire()
        if not self._flag:
            self._cond.wait()
        self._cond.release()


class Thread(object):
    def __init__(self, func=None, args=()):
            self._func = func
            self._args = args
            
    def start(self):
            _start_new_thread(self._thread_run, ())
            
    def _thread_run(self):
        try:
            self.run()
        except Exception, e:
            print repr(e)
                    
    def run(self):
            self._func(*self._args)


class Queue(object):
    def __init__(self, maxsize=0):
        self._mutex = Lock()
        self._not_empty = Condition(self._mutex)
        self._not_full = Condition(self._mutex)
        self._queue = deque()
        self.maxsize = maxsize
        
    def get(self):
        self._not_empty.acquire()
        self._not_empty.waitIf(self._isEmpty)
        item = self._queue.popleft()
        self._not_full.notify()
        self._not_empty.release()
        return item
        
    def put(self, item):
        self._not_full.acquire()
        self._not_full.waitIf(self._isFull)
        self._queue.append(item)
        self._not_empty.notify()
        self._not_full.release()
        
    def isEmpty(self):
        self._mutex.acquire()
        val = self._isEmpty()
        self._mutex.release()
        return val
    
    def isFull(self):
        self._mutex.acquire()
        val = self._isFull()
        self._mutex.release()
        return val
    
    def size(self):
        self._mutex.acquire()
        val = self._size()
        self._mutex.release()
        return val
        
    def _isEmpty(self):
        return self._size() == 0
    
    def _isFull(self):
        return self.maxsize > 0 and self._size() >= self.maxsize
    
    def _size(self):
        return len(self._queue)
    

class ThreadPool(object):
    def __init__(self, nThreads=1):
        self._taskQueue = Queue(nThreads)
        while nThreads > 0:
            Thread(self._loop).start()
            nThreads -= 1
    
    def addTask(self, task):
        self._taskQueue.put(task)
    
    def _loop(self):
        while True:
            handler, arg = self._taskQueue.get()
            handler(arg)
            
class ThreadTask(ThreadPool):
    def __init__(self, handler, nThreads=1):
        self._handler = handler
        ThreadPool.__init__(self, nThreads)
        
    def _loop(self):
        while True:
            arg = self._taskQueue.get()
            self._handler(arg)


class Process(object):
    def __init__(self):
        self._msgQueue = Queue()
    
    def send(self, msg):
        self._msgQueue.put(msg)
    
    def recv(self, handler):
        msg = self._msgQueue.get()
        handler(msg)
