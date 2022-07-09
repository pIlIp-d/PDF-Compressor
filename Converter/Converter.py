from abc import ABC, abstractmethod


class Converter(ABC):
    def __init__(self, origin_path, dest_path, os_type=0):
        self.origin_path = origin_path
        self.dest_path = dest_path
        self.os_type = os_type

    def convert(self):
        pass
