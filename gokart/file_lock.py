import os
import time
import errno
import json
import traceback
from datetime import datetime
 
class FileLockException(Exception):
    pass
 
class FileLock(object):
    """ A file locking mechanism that has context-manager support so 
        you can use it in a with statement. This should be relatively cross
        compatible as it doesn't rely on msvcrt or fcntl for the locking.
    """
    def __init__(self, lock_file, timeout=10, delay=.05):
        """ Prepare the file locker. Specify the file to lock and optionally
            the maximum timeout and the delay between each attempt to lock.
        """
        self.acquired_lock_time = None
        self.lockfile = lock_file
        self.timeout = timeout
        self.delay = delay

    @property
    def is_locked(self):
        try:
            if not self.acquired_lock_time:
                #not locked
                return False
            elif time.time() - self.acquired_lock_time < self.timeout:
                #acquired the lock and is not timeout
                return True
            elif self.acquired_lock_time != os.path.getmtime(self.lockfile):
                #acquired the lock, but is already timeout, and lockfile is modified
                self.acquired_lock_time = None
                return False
            else:
                #acquired the lock, but is already timeout, and lockfile is not modified, renew the lock
                os.utime(self.lockfile,None)
                self.acquired_lock_time = os.path.getmtime(self.lockfile)
                return True
        except OSError as e:
            if e.errno == errno.ENOENT:
                #lock file does not exist
                return False
            raise
        

    @property
    def lock_metadata(self):
        metadata = None
        with open(self.lockfile,"r") as f:
            metadata = f.read()
        if metadata:
            try:
                metadata = json.loads(metadata)
            except:
                metadata = None
        return metadata


    @property
    def is_locked_by_others(self):
        try:
            if os.path.exists(self.lockfile):
                locked = True
                metadata = self.lock_metadata
                try:
                    if metadata:
                        if os.path.exists(os.path.join("/proc",str(metadata["pid"]))) and metadata["process_start_time"] == os.path.getmtime(os.path.join("/proc",str(metadata["pid"]),"cmdline")):
                            #process exist and also the create time of the process is the same as the meta data
                            locked = True
                        else:
                            locked = False
                except:
                    traceback.print_exc()
                    pass
    
                if locked:
                    #check timeout
                    if time.time() - os.path.getmtime(self.lockfile) >= self.timeout:
                        if metadata:
                            raise FileLockException("Lock is required by process ({}) at time ({}),and failed to release it within {} seconds".format(metadata["pid"],datetime.fromtimestamp(os.path.getmtime(self.lockfile)),self.timeout))
                        else:
                            raise FileLockException("Lock is required by other process, but failed to release it within {} seconds, automatically releast it.".format(self.timeout))
    
                if not locked:
                    try:
                        os.remove(self.lockfile)
                    except:
                        pass
    
                return locked
            else:
                return False
        except OSError as e:
            if e.errno == errno.ENOENT:
                #lock file does not exist
                return False
            raise

    def waitUntilRelease(self):
        """ Wait until no one hold the lock, if possible. 
            If the lock is in use, it check again every `wait` seconds. 
            It does this until it either no one hold the lock or
            exceeds `timeout` number of seconds, in which case it throws 
            an exception.
        """
        while self.is_locked_by_others:
            time.sleep(self.delay)
 
    def acquire(self):
        """ Acquire the lock, if possible. If the lock is in use, it check again
            every `wait` seconds. It does this until it either gets the lock or
            exceeds `timeout` number of seconds, in which case it throws 
            an exception.
        """
        if self.is_locked:
            #already get the lock
            if not os.path.exists(self.lockfile):
                #the lock file doesn't exist for whatever reason
                self.acquired_lock_time = None

        if self.is_locked:
            #already get the lock
            return

        while True:
            fd = None
            try:
                fd = os.open(self.lockfile, os.O_CREAT|os.O_EXCL|os.O_RDWR)
                os.write(fd,json.dumps({"pid":os.getpid(),"process_start_time":os.path.getmtime(os.path.join("/proc",str(os.getpid()),"cmdline"))}))
                self.acquired_lock_time = os.path.getmtime(self.lockfile)
                break;
            except OSError as e:
                if e.errno == errno.ENOENT:
                    #folder does not exist,create it and continue
                    os.makedirs(os.path.dirname(self.lockfile))
                    continue
                elif e.errno != errno.EEXIST:
                    raise 

                if not self.is_locked_by_others:
                    #no one acquire the lock, try again
                    continue
                time.sleep(self.delay)
            finally:
                if fd:
                    try:
                        os.close(fd)
                    except:
                        pass
 
    def release(self):
        """ Get rid of the lock by deleting the lockfile. 
            When working in a `with` statement, this gets automatically 
            called at the end.
        """
        if self.is_locked:
            try:
                os.remove(self.lockfile)
            except:
                pass
            self.acquired_lock_time = None

 
    def __enter__(self):
        """ Activated when used in the with statement. 
            Should automatically acquire a lock to be used in the with block.
        """
        if not self.is_locked:
            self.acquire()
        return self
 
 
    def __exit__(self, type, value, traceback):
        """ Activated at the end of the with statement.
            It automatically releases the lock if it isn't locked.
        """
        if self.is_locked:
            self.release()
 
 
    def __del__(self):
        """ Make sure that the FileLock instance doesn't leave a lockfile
            lying around.
        """
	self.release()
