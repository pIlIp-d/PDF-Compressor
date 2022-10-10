from abc import ABC, abstractmethod

from ..processor.postprocessor import Postprocessor
from ..processor.preprocessor import Preprocessor


class EventHandler(Preprocessor, Postprocessor, ABC):
    def started_processing(self): pass

    def finished_all_files(self): pass

    def preprocess(self, source_file: str, destination_file: str) -> None: pass

    def postprocess(self, source_file: str, destination_file: str) -> None: pass
