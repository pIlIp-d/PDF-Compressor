from abc import ABC, abstractmethod
import os


class Converter(ABC):
    def __init__(self, origin_path, dest_path):
        self.origin_path = os.path.abspath(origin_path)
        self.dest_path = os.path.abspath(dest_path)

    @abstractmethod
    def convert(self):
        pass
