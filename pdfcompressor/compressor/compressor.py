from abc import ABC, abstractmethod

from pdfcompressor.processor.processor import Processor


class Compressor(Processor, ABC):

    @abstractmethod
    def compress(self, source_path: str, destination_path: str) -> None: pass

    @abstractmethod
    def compress_file(self, source_file: str, destination_file: str) -> None: pass

    @abstractmethod
    def compress_file_list(self, source_files: list, destination_files: list) -> None: pass

    def compress_file_list_multi_threaded(self, source_files: list, destination_files: list) -> None:
        args_list = [{"source_file": source, "destination_file": destination}
                     for source, destination in zip(source_files, destination_files)]
        self._custom_map_execute(self.compress_file, args_list)
