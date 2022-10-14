from abc import ABC


class Preprocessor(ABC):
    def preprocess(self, source_file: str, destination_file: str) -> None: pass
