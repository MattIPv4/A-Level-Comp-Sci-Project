import os
import signal
import subprocess


class SassWatcher:

    def __init__(self, from_path: str, to_path: str):
        self.__from = from_path
        self.__to = to_path
        self.__p = None

    @property
    def args(self) -> str:
        return "--watch {}:{} --style compressed".format(self.__from, self.__to)

    def run(self):
        if self.__p is None:
            self.__p = subprocess.Popen('sass {}'.format(self.args), shell=True)

    def close(self):
        if self.__p is not None:
            os.killpg(os.getpgid(self.__p.pid), signal.SIGTERM)
            self.__p = None
