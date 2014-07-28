import threading
from asyncio.event import DefaultEventLoopPolicy

class AioEventLoopPolicy(DefaultEventLoopPolicy):
    def get_event_loop(self):
        """Get the event loop.

        This may be None or an instance of EventLoop.
        """
        if (self._local._loop is None and
            not self._local._set_called and
            isinstance(threading.current_thread(), threading._MainThread)):
            self.set_event_loop(self.new_event_loop())
        if self._local._loop is not None:
            # Create a new loop for a new thread.
            self.set_event_loop(self.new_event_loop())
        return self._local._loop
