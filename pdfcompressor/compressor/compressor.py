from abc import ABC, abstractmethod


class Compressor(ABC):
    @abstractmethod
    def compress(self, source_path: str, destination_path: str) -> None: pass
