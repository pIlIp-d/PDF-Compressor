from abc import ABC


class Postprocessor(ABC):
    def postprocess(self, source_file: str, destination_file: str) -> None: pass
