import subprocess

class SassWatcher:

    def __init__(self, from_path: str, to_path: str):
        self.__from = from_path
        self.__to = to_path

    @property
    def args(self) -> str:
        return "--watch {}:{} --style compressed".format(self.__from, self.__to)

    def run(self):
        subprocess.Popen('sass {}'.format(self.args), shell=True)
