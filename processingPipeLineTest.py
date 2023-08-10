import shutil
from typing import Callable


class ProcessingPipeline:
    def __init__(self, *processors: Callable[[str, str], None]):
        self.processors = processors

    def process_file_list_async(self, source_files: list[str], destination_files: list[str]) -> None:
        # add check for order resolution with file types

        def process_pipeline(source_file: str, destination_path: str):
            temp_source = source_file
            temp_dest = self.get_temp_file(source_file)
            for processor in self.processors:
                processor(temp_source, temp_dest)
                temp_source = temp_dest
            # move result file to real destination
            shutil.move(temp_source, destination_path)

        # Iterate over the file pairs and process each file
        map(process_pipeline, *zip(source_files, destination_files))
    @staticmethod
    def get_temp_file(file_ending: str):
        return file_ending.split(".")[-1]
