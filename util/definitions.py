import os
from dataclasses import dataclass


@dataclass
class PathDefinitions:
    def __init__(self):
        os.path.abspath(os.curdir)

        self.abspath_root: str = os.path.abspath(os.curdir)
        self.abspath_debug: str = self.abspath_root + '\\locale'
