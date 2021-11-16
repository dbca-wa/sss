import logging
import threading

class MessageHandler(logging.Handler):
    INSTANCES = {}

    def __new__(cls,name,*args,**argv):
        if  name in cls.INSTANCES:
            return cls.INSTANCES[name]
        else:
            return super(MessageHandler,cls).__new__(cls,*args,**argv)

    def __init__(self,name,*args,**argv):
        if  name in self.INSTANCES:
            return 
        super(MessageHandler,self).__init__(*args,**argv)
        self._name = "log_{}".format(name)

        self.INSTANCES[name] = self

    @property
    def started(self):
        return hasattr(threading.currentThread(),self._name)

    def start(self):
        """
        Start it if it is not started yet
        """
        if not hasattr(threading.currentThread(),self._name):
            setattr(threading.currentThread(),self._name,[])

    def restart(self):
        """
        start it if it is not started yet; clean existing messages if it is already started.
        """
        setattr(threading.currentThread(),self._name,[])


    def stop(self):
        if hasattr(threading.currentThread(),self._name):
            delattr(threading.currentThread(),self._name)

    @property
    def messages(self):
        if hasattr(threading.currentThread(),self._name):
            return getattr(threading.currentThread(),self._name)
        else:
            return None


    def emit(self,record):
        messages = self.messages
        if messages != None:
            messages.append(self.format(record))

