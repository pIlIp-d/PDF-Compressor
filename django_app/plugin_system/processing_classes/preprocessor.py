from abc import ABC


class Preprocessor(ABC):
    # call before each processing of a file
    def preprocess(self, source_file: str, destination_file: str) -> None: pass
