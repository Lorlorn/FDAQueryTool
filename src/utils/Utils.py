import time
import os

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Timer(metaclass = Singleton):
    def __init__(self):
        self._stop = None
    
    def tic(self):
        self._stop = time.time()
    
    def tac(self):
        if (self._stop == None):
            self.tic()
            return
        print('Time elapsed: {0:.2f}'.format(time.time() - self._stop))
        self._stop = time.time()

    def clear(self):
        self._stop = None

class FilePathHandler:
    DEFAULT_ROOT = '.'

    def __init__(self, path = DEFAULT_ROOT):
        self._root = path
        self._curr_path = None

    @property
    def root(self):
        return self._root
    
    @root.setter
    def root(self, path):
        if (os.path.isdir(path)):
            self._root = path

    @property
    def curr_path(self):
        return self._curr_path
    
    @curr_path.setter
    def curr_path(self, folder_name = ''):
        new_path = self._root + os.path.sep + folder_name
        if (self._curr_path == None) and (not os.path.isdir(new_path)):
            os.mkdir(new_path)
        self._curr_path = new_path
    
    def reset(self):
        self._curr_path = None

    def __del__(self):
        if len(os.listdir(self._curr_path)) == 0:
            os.rmdir(self._curr_path)
