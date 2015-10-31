import logging.config
import logging
import os
import json
import http.server
from contextlib import contextmanager
from watchdog.events import FileSystemEventHandler


def setup_logging(default_path='logging.json',
                  default_level=logging.INFO,
                  env_key='LOG_CFG'):
    """
        Setup logging configuration
    """
    # Ensure the build directory exists..
    if not os.path.exists('build/'):
        os.makedirs('build/')

    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


class WatchdogHandler(FileSystemEventHandler):

    def __init__(self, context, action):
        super(WatchdogHandler, self).__init__()
        self._action = action
        self._context = context

    def on_any_event(self, event):
        if event.is_directory:
            return
        self._action(self._context, getattr(event, 'dest_path', event.src_path))


class StoppableServer(http.server.HTTPServer):

    stopped = False
    paused = False

    def __init__(self, *args, **kw):
        super(StoppableServer, self).__init__(*args, **kw)

    def serve_forever(self):
        while not self.stopped:
            while not self.paused:
                self.handle_request()
            sleep(0.5)

    def force_stop(self):
        self.server_close()
        self.stopped = True


@contextmanager
def pushd(newDir):
    previousDir = os.getcwd()
    os.chdir(newDir)
    yield
    os.chdir(previousDir)
