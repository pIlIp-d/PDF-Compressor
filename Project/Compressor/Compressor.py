from abc import ABC, abstractmethod


class Compressor(ABC):

    def __init__(self, origin_path, dest_path, os=0):
        self.origin_path = origin_path
        self.dest_path = dest_path
        self.os = os

    @abstractmethod
    def compress(self):
        pass

